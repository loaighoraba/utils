from pathlib import Path

import requests

SURA_NAMES = ["الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس", "هود", "يوسف", "الرعد", "إبراهيم", "الحجر", "النحل", "الإسراء", "الكهف", "مريم", "طه", "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان", "الشعراء", "النمل", "القصص", "العنكبوت", "الروم", "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر", "يس", "الصافات", "ص", "الزمر", "غافر", "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية", "الأحقاف", "محمد", "الفتح", "الحجرات", "ق", "الذاريات", "الطور", "النجم", "القمر", "الرحمن", "الواقعة", "الحديد", "المجادلة",
              "الحشر", "الممتحنة", "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق", "التحريم", "الملك", "القلم", "الحاقة", "المعارج", "نوح", "الجن", "المزمل", "المدثر", "القيامة", "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس", "التكوير", "الانفطار", "المطففين", "الانشقاق", "البروج", "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد", "الشمس", "الليل", "الضحى", "الشرح", "التين", "العلق", "القدر", "البينة", "الزلزلة", "العاديات", "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل", "قريش", "الماعون", "الكوثر", "الكافرون", "النصر", "المسد", "الإخلاص", "الفلق", "الناس"]


class QuranDownloader:
    def __init__(self, url, directory: Path):
        self.url = url
        self.directory = directory

    def download(self):
        for sura_number in range(1, len(SURA_NAMES) + 1):
            sura = Sura(sura_number, SURA_NAMES[sura_number - 1])
            sura.download(self.url, self.directory)


class Sura:
    def __init__(self, number, name):
        self.number = number
        self.name = name

    def download(self, quran_url, quran_directory):
        with self._local_file(quran_directory).open("wb") as f:
            f.write(self._resource(quran_url).content)

    def _resource(self, quran_url):
        sura_url = f"{quran_url}{self.number:03}.mp3"
        return requests.get(sura_url)

    def _local_file(self, quran_directory):
        return quran_directory / f"{self.number:03} - {self.name}.mp3"


directory = Path("/home/loai/Quran")
directory.mkdir(parents=True, exist_ok=True)
url = "http://download.quran.islamway.net/quran3/133/128/"

downloader = QuranDownloader(url, directory)
downloader.download()
