from pathlib import Path
import subprocess
import os

import json

# Load configuration from resources.json
with open(Path(__file__).parent / "resources.json", encoding="utf-8") as f:
    config = json.load(f)


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


# Get playlists from config
playlists = config.get("youtube_playlist_urls", [])
if not playlists:
    raise ValueError("youtube_playlist_urls is not set in resources.json")
# Replace with your desired base directory
base_directory = "/home/loai/Youtube playlists/"

download_playlists(playlists, base_directory)
