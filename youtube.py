from pathlib import Path
import subprocess


def download_playlists(playlists: list[str], base_directory: str):
    base_path = Path(base_directory)
    base_path.mkdir(parents=True, exist_ok=True)

    for index, playlist in enumerate(playlists, 1):
        playlist_path = base_path / str(index)
        playlist_path.mkdir(parents=True, exist_ok=True)

        print(f"Downloading playlist: {playlist} into {playlist_path}")
        try:
            subprocess.run(
                ["yt-dlp", "-P", str(playlist_path), playlist],
                check=True
            )
            print(f"Successfully downloaded playlist: {index}: {playlist}")
        except subprocess.CalledProcessError as e:
            print(
                f"Failed to download playlist: {index}: {playlist}. Error: {e}")


# Example usage
playlists_str = """
https://www.youtube.com/playlist?list=PLbwoEuzvC1jkQcIPE7t6784FJuLCKPZgB
https://www.youtube.com/playlist?list=PL6Ovc8VkebWfEoEj4tC65XKvXFA9KokL6
https://www.youtube.com/playlist?list=PLw_nS0jRO9hOYpeC1Iq8IbenE34OPwdU1
https://www.youtube.com/playlist?list=PLbwoEuzvC1jkPSRMfSPsyxUCZCbRwuh8J
https://www.youtube.com/playlist?list=PLBo0ObYRfprhIjejusffN27Gyz9lDKb3E
https://www.youtube.com/playlist?list=PLXGZ5siRlKlbIdANw8dOwRhHB3F8FUwoi
https://www.youtube.com/playlist?list=PLrCMZokRKURo-IlB8Ef0_D195U8-3OlpS
https://www.youtube.com/playlist?list=PLBo0ObYRfprjmcgmEvm5L1mpeOMSXR1zr
https://www.youtube.com/playlist?list=PLNfxI9NLmQZZ_DdXn0tUX7OroUc9rJLE5
https://www.youtube.com/playlist?list=PLbVLBZiLIlN0vEBK6zz8NOUYAT4j2PZtc
https://www.youtube.com/playlist?list=PLCIym5Znu5q6TPHyIWZ-9jUMUOfSChMC0
https://www.youtube.com/playlist?list=PLLe92-DrXr5rLYHpdtQzhspdUVyAL_j6u
https://www.youtube.com/playlist?list=PLf2nHmuYPSp0KMpYhU38am3dOr-goZFzC
https://www.youtube.com/playlist?list=PLwjVq3ledbwVSbiXDeUjLsaOxbrmyWuDA
https://www.youtube.com/playlist?list=PLlhB8IcWC_ZD3hWomiIr_axBAWaWa24xr
https://www.youtube.com/playlist?list=PLSrc9hONoxlGrueBRPLIzEqZH5ajagms1
https://www.youtube.com/playlist?list=PLs3bxgtXOysinhGuS9zX0nvPXY771RpAe
https://www.youtube.com/playlist?list=PLLNccfV_UuqqzTyWe_GdKfGfFlIRlbIH5
https://www.youtube.com/playlist?list=PLw_nS0jRO9hOJVqQcqzXUzljQKwSxn-R1
"""
playlists = [line.strip()
             for line in playlists_str.strip().split("\n") if line.strip()]
# Replace with your desired base directory
base_directory = "/home/loai/Youtube playlists/"

download_playlists(playlists, base_directory)
