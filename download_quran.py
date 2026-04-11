from pathlib import Path
import time
import argparse
import json
import httpx
import tqdm


class QuranDownloader:
    def __init__(self, url: str, directory: Path, sura_names: list[str]):
        self.url = self._normalize_url(url)
        self.directory = directory
        self.suras = [
            Sura(number, name) for number, name in enumerate(sura_names, start=1)
        ]

    def download(self) -> None:
        with httpx.Client(verify=False) as client:
            for sura in tqdm.tqdm(self.suras, total=len(self.suras)):
                sura.download(self.url, self.directory, client)

    @staticmethod
    def _normalize_url(url: str) -> str:
        url = url.strip()
        if not url:
            raise ValueError("A base URL is required.")
        return url if url.endswith("/") else f"{url}/"


class Sura:
    def __init__(self, number: int, name: str):
        self.number = number
        self.name = name

    def download(
        self,
        quran_url: str,
        quran_directory: Path,
        client: httpx.Client,
    ) -> None:
        response = client.get(self.resource_url(quran_url))
        response.raise_for_status()

        with self.local_file(quran_directory).open("wb") as file:
            file.write(response.content)

    def resource_url(self, quran_url: str) -> str:
        return f"{quran_url}{self.number:03}.mp3"

    def local_file(self, quran_directory: Path) -> Path:
        return quran_directory / f"{self.number:03} - {self.name}.mp3"


def get_base_url() -> str:
    parser = argparse.ArgumentParser(description="Download Quran MP3 files.")
    parser.add_argument(
        "--url",
        help="Base URL for Quran audio files, e.g. https://server/path/",
    )
    args = parser.parse_args()
    return args.url or input("Enter Quran base URL (e.g. https://server/path/): ")


def load_sura_names() -> list[str]:
    with open(Path(__file__).parent / "sura_names.json", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    directory = Path("/home/loai/Quran")
    directory.mkdir(parents=True, exist_ok=True)

    downloader = QuranDownloader(
        url=get_base_url(),
        directory=directory,
        sura_names=load_sura_names(),
    )
    downloader.download()


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")
