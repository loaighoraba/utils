from pathlib import Path
import subprocess
import os
from dotenv import load_dotenv


load_dotenv()


def download_playlists(playlists: list[str], base_directory: str):
    base_path = Path(base_directory)
    base_path.mkdir(parents=True, exist_ok=True)

    for index, playlist in enumerate(playlists, 1):
        playlist_path = base_path / str(index)
        playlist_path.mkdir(parents=True, exist_ok=True)

        print(f"Downloading playlist: {playlist} into {playlist_path}")
        try:
            subprocess.run(["yt-dlp", "-P", str(playlist_path), playlist], check=True)
            print(f"Successfully downloaded playlist: {index}: {playlist}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download playlist: {index}: {playlist}. Error: {e}")


playlists_csv = os.getenv("YOUTUBE_PLAYLIST_URLS", "")
playlists = [url.strip() for url in playlists_csv.split(",") if url.strip()]
if not playlists:
    raise ValueError("YOUTUBE_PLAYLIST_URLS is not set in the environment")
# Replace with your desired base directory
base_directory = "/home/loai/Youtube playlists/"

download_playlists(playlists, base_directory)
