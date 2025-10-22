from mutagen.easyid3 import EasyID3
from pathlib import Path


def update_mp3_tags(directory: Path, *, album, artist):
    """
    Updates the album and artist tags for all MP3 files in the given directory.

    :param directory: Path to the directory containing MP3 files.
    :param album: The album name to set.
    :param artist: The artist name to set.
    """

    for mp3_file in directory.glob("*.mp3"):
        try:
            audio = EasyID3(mp3_file)
            # Set title to the file name without extension
            audio["title"] = mp3_file.stem
            audio["album"] = album
            audio["artist"] = artist
            audio.save()
            print(f"Updated tags for: {mp3_file.name}")
        except Exception as e:
            print(f"Failed to update tags for: {mp3_file.name}. Error: {e}")


directory = Path("/home/loai/Quran")
album = "المصحف المرتل"
artist = "محمد صديق المنشاوي"

update_mp3_tags(directory, album=album, artist=artist)
