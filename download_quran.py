from pathlib import Path
import time
import urllib3
import asyncio
import httpx

import tqdm
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_CONCURRENT_DOWNLOADS = 10


class QuranDownloader:
    def __init__(self, url, directory: Path, sura_names: list[str]):
        self.url = url
        self.directory = directory
        self.sura_names = sura_names

    async def download(self):
        suras = [
            Sura(number, name) for number, name in enumerate(self.sura_names, start=1)
        ]
        semaphore = asyncio.BoundedSemaphore(MAX_CONCURRENT_DOWNLOADS)

        async with httpx.AsyncClient(verify=False) as client:
            tasks = [
                sura.download(self.url, self.directory, client, semaphore)
                for sura in suras
            ]

            for task in tqdm.tqdm(asyncio.as_completed(tasks)):
                sura = await task
                print(f"Downloaded Sura {sura.number}: {sura.name}")


class Sura:
    def __init__(self, number, name):
        self.number = number
        self.name = name

    async def download(self, quran_url, quran_directory, client, semaphore):
        async with semaphore:
            response = await client.get(self._resource_url(quran_url))
            with self._local_file(quran_directory).open("wb") as f:
                f.write(response.content)

        return self

    def _resource_url(self, quran_url):
        return f"{quran_url}{self.number:03}.mp3"

    def _local_file(self, quran_directory):
        return quran_directory / f"{self.number:03} - {self.name}.mp3"


async def main():
    directory = Path("/home/loai/Quran")
    directory.mkdir(parents=True, exist_ok=True)

    # Load configuration from resources.json
    with open(Path(__file__).parent / "resources.json", encoding="utf-8") as f:
        config = json.load(f)

    url = config.get("quran_base_url")
    if not url:
        raise ValueError("quran_base_url is not set in resources.json")

    # Load sura names from external JSON file
    with open(Path(__file__).parent / "sura_names.json", encoding="utf-8") as f:
        sura_names = json.load(f)

    downloader = QuranDownloader(url, directory, sura_names)
    await downloader.download()


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")
