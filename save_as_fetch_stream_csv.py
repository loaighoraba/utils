#!/usr/bin/env python3
"""
Stream URLs from many Excel files, fetch data with httpx using an asyncio worker pool,
and write results incrementally to a CSV using csv.writer running in a dedicated thread.

This version uses the synchronous csv.writer (faster and CSV-correct) while ensuring
the event loop never blocks by handing CSV writes to a background thread via a
thread-safe queue.Queue.

Usage:
    python fetch_stream_csv_writer.py urls1.xlsx urls2.xlsx ...
"""

import asyncio
import csv
import logging
import threading
import time
from typing import List, Optional

import httpx
from openpyxl import load_workbook
import queue as sync_queue_module

# --------- Configuration ----------
CONCURRENCY = 50
URL_QUEUE_MAXSIZE = 2000
RESULT_QUEUE_MAXSIZE = 2000
REQUEST_TIMEOUT = 20.0
RETRIES = 2
BACKOFF_BASE = 0.5  # seconds
CSV_OUT = "results.csv"
URL_COLUMN_INDEX = 1  # 1-based index of column that contains URL in Excel (adjust)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


# ---------- Excel reader (runs in a thread) ----------
def _read_excel_enqueue(
    path: str, loop: asyncio.AbstractEventLoop, url_queue: asyncio.Queue
):
    """
    This runs in a thread (via asyncio.to_thread). It reads rows from the Excel
    file using openpyxl in read_only mode and schedules queue.put coroutines
    back onto the event loop via asyncio.run_coroutine_threadsafe.
    """
    logging.info("Reading Excel: %s", path)
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    for row in ws.iter_rows(values_only=True):
        if not row:
            continue
        url = row[URL_COLUMN_INDEX - 1] if len(row) >= URL_COLUMN_INDEX else None
        if not url:
            continue
        # schedule putting into asyncio.Queue from this separate thread
        asyncio.run_coroutine_threadsafe(url_queue.put(str(url).strip()), loop)
    wb.close()
    logging.info("Finished scheduling URLs from: %s", path)


async def produce_from_excels(paths: List[str], url_queue: asyncio.Queue):
    loop = asyncio.get_running_loop()
    for path in paths:
        # read each excel file in its own thread to avoid blocking
        await asyncio.to_thread(_read_excel_enqueue, path, loop, url_queue)


# ---------- HTTP fetching with httpx (async) ----------
async def fetch_with_retries(client: httpx.AsyncClient, url: str) -> str:
    last_exc: Optional[Exception] = None
    for attempt in range(1, RETRIES + 2):
        try:
            r = await client.get(url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            # parse/derive the needed info here. Replace with your real parsing:
            return r.text[:200]  # example: first 200 chars
        except Exception as exc:
            last_exc = exc
            if attempt <= RETRIES:
                await asyncio.sleep(BACKOFF_BASE * (2 ** (attempt - 1)))
            else:
                return f"ERROR: {repr(last_exc)}"
    return f"ERROR: {repr(last_exc)}"


# ---------- Worker (async) ----------
async def worker(
    worker_id: int,
    url_queue: asyncio.Queue,
    result_sync_queue: sync_queue_module.Queue,
    client: httpx.AsyncClient,
):
    loop = asyncio.get_running_loop()
    logging.info("Worker %d started", worker_id)
    while True:
        url = await url_queue.get()
        if url is None:
            url_queue.task_done()
            break
        try:
            result = await fetch_with_retries(client, url)
            # Put result into synchronous queue using the thread pool so we never block the loop.
            # This will execute sync_queue.put((url, result)) in a worker thread (not the writer thread).
            await loop.run_in_executor(None, result_sync_queue.put, (url, result))
        except Exception as exc:
            await loop.run_in_executor(
                None, result_sync_queue.put, (url, f"ERROR: {exc!r}")
            )
        finally:
            url_queue.task_done()
    logging.info("Worker %d exiting", worker_id)


# ---------- CSV writer thread (synchronous csv.writer) ----------
def csv_writer_thread(result_sync_queue: sync_queue_module.Queue, csv_path: str):
    """
    Runs in a dedicated thread. Consumes (url, result) tuples from result_sync_queue
    and writes them using csv.writer. Stops when it receives a None sentinel.
    """
    logging.info("CSV writer thread starting, writing to %s", csv_path)
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["url", "result"])
        while True:
            item = result_sync_queue.get()  # blocking
            try:
                if item is None:
                    # sentinel received; mark task done and break
                    result_sync_queue.task_done()
                    break
                url, result = item
                # Ensure result is a primitive string (avoid writing complex objects)
                writer.writerow([url, str(result)])
                # flush can be added if desired:
                # f.flush()
                result_sync_queue.task_done()
            except Exception:
                # Ensure we always mark task_done even on error to avoid join blocking forever.
                result_sync_queue.task_done()
                raise
    logging.info("CSV writer thread finished")


# ---------- main ----------
async def main(excel_paths: List[str], out_csv: str = CSV_OUT):
    url_queue: asyncio.Queue = asyncio.Queue(maxsize=URL_QUEUE_MAXSIZE)
    result_sync_queue: sync_queue_module.Queue = sync_queue_module.Queue(
        maxsize=RESULT_QUEUE_MAXSIZE
    )

    # start CSV writer thread
    writer_thread = threading.Thread(
        target=csv_writer_thread, args=(result_sync_queue, out_csv), daemon=False
    )
    writer_thread.start()

    # httpx client with connection limits
    limits = httpx.Limits(
        max_connections=CONCURRENCY, max_keepalive_connections=CONCURRENCY
    )
    async with httpx.AsyncClient(limits=limits) as client:
        # start workers
        workers = [
            asyncio.create_task(worker(i, url_queue, result_sync_queue, client))
            for i in range(CONCURRENCY)
        ]

        # start producer - this will schedule url_queue.put from threads
        await produce_from_excels(excel_paths, url_queue)

        # producer finished, send sentinel None per worker so they shut down
        for _ in range(CONCURRENCY):
            await url_queue.put(None)

        # wait until all URL tasks are processed
        await url_queue.join()

        # wait for all workers to finish
        await asyncio.gather(*workers)

    # all workers finished — send a single sentinel to the sync result queue to stop writer thread
    loop = asyncio.get_running_loop()
    # put the sentinel in the sync queue in the threadpool (non-blocking to event loop)
    await loop.run_in_executor(None, result_sync_queue.put, None)

    # wait for the writer thread to process all items and exit
    await loop.run_in_executor(None, result_sync_queue.join)
    writer_thread.join()
    logging.info("All done. Results written to %s", out_csv)


if __name__ == "__main__":
    import sys

    excel_files = sys.argv[1:]
    if not excel_files:
        print("Usage: python fetch_stream_csv_writer.py file1.xlsx file2.xlsx ...")
        raise SystemExit(1)

    t0 = time.time()
    asyncio.run(main(excel_files, CSV_OUT))
    logging.info("Total elapsed: %.2f seconds", time.time() - t0)
