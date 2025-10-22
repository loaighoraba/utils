from pathlib import Path
import time
import urllib3
import asyncio
import httpx
import requests
import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SURA_NAMES = [
    "الفاتحة",
    "البقرة",
    "آل عمران",
    "النساء",
    "المائدة",
    "الأنعام",
    "الأعراف",
    "الأنفال",
    "التوبة",
    "يونس",
    "هود",
    "يوسف",
    "الرعد",
    "إبراهيم",
    "الحجر",
    "النحل",
    "الإسراء",
    "الكهف",
    "مريم",
    "طه",
    "الأنبياء",
    "الحج",
    "المؤمنون",
    "النور",
    "الفرقان",
    "الشعراء",
    "النمل",
    "القصص",
    "العنكبوت",
    "الروم",
    "لقمان",
    "السجدة",
    "الأحزاب",
    "سبأ",
    "فاطر",
    "يس",
    "الصافات",
    "ص",
    "الزمر",
    "غافر",
    "فصلت",
    "الشورى",
    "الزخرف",
    "الدخان",
    "الجاثية",
    "الأحقاف",
    "محمد",
    "الفتح",
    "الحجرات",
    "ق",
    "الذاريات",
    "الطور",
    "النجم",
    "القمر",
    "الرحمن",
    "الواقعة",
    "الحديد",
    "المجادلة",
    "الحشر",
    "الممتحنة",
    "الصف",
    "الجمعة",
    "المنافقون",
    "التغابن",
    "الطلاق",
    "التحريم",
    "الملك",
    "القلم",
    "الحاقة",
    "المعارج",
    "نوح",
    "الجن",
    "المزمل",
    "المدثر",
    "القيامة",
    "الإنسان",
    "المرسلات",
    "النبأ",
    "النازعات",
    "عبس",
    "التكوير",
    "الانفطار",
    "المطففين",
    "الانشقاق",
    "البروج",
    "الطارق",
    "الأعلى",
    "الغاشية",
    "الفجر",
    "البلد",
    "الشمس",
    "الليل",
    "الضحى",
    "الشرح",
    "التين",
    "العلق",
    "القدر",
    "البينة",
    "الزلزلة",
    "العاديات",
    "القارعة",
    "التكاثر",
    "العصر",
    "الهمزة",
    "الفيل",
    "قريش",
    "الماعون",
    "الكوثر",
    "الكافرون",
    "النصر",
    "المسد",
    "الإخلاص",
    "الفلق",
    "الناس",
]

MAX_CONCURRENT_DOWNLOADS = 50


class QuranDownloader:
    def __init__(self, url, directory: Path):
        self.url = url
        self.directory = directory

    async def download(self):
        suras = [Sura(number, name) for number, name in enumerate(SURA_NAMES, start=1)]
        semaphore = asyncio.BoundedSemaphore(MAX_CONCURRENT_DOWNLOADS)
        async with httpx.AsyncClient(verify=False) as client:
            tasks = []
            for sura in suras:

                async def download_with_metadata(sura):
                    await sura.download(self.url, self.directory, client, semaphore)
                    return sura

                tasks.append(asyncio.create_task(download_with_metadata(sura)))

            for task in tqdm.tqdm(
                asyncio.as_completed(tasks), desc="Downloading Quran Suras"
            ):
                sura = await task
                print(f"Downloaded Sura {sura.number}: {sura.name}")


class Sura:
    def __init__(self, number, name):
        self.number = number
        self.name = name

    async def download(self, quran_url, quran_directory, client, semaphore):
        async with semaphore:
            # print(f"Downloading Sura {self.number}: {self.name}")
            response = await client.get(self._resource_url(quran_url))
            # response.raise_for_status()
            with self._local_file(quran_directory).open("wb") as f:
                f.write(response.content)

            return

    def _resource_url(self, quran_url):
        return f"{quran_url}{self.number:03}.mp3"

    def _local_file(self, quran_directory):
        return quran_directory / f"{self.number:03} - {self.name}.mp3"


async def main():
    directory = Path("/home/loai/Quran")
    directory.mkdir(parents=True, exist_ok=True)
    url = "https://download.quran.islamway.net/quran3/696/"

    downloader = QuranDownloader(url, directory)
    await downloader.download()


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time} seconds")
