import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Dict

try:
    from config import POLL_INTERVAL, WIN_DEBUG_ACTIVE, VISUALISE_LYRICS
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from config import POLL_INTERVAL, WIN_DEBUG_ACTIVE, VISUALISE_LYRICS

from processor.data_cacher import get_song_data
from frontend.console_visualiser import stop_visualiser, visualise


async def get_media_info() -> Optional[Dict[str, str]]:
    try:
        metadata = subprocess.run(
            [
                "playerctl",
                "metadata",
                "--format",
                "{{artist}}|{{title}}"
            ],
            capture_output=True,
            text=True,
        )

        if metadata.returncode != 0:
            return None

        line = metadata.stdout.strip()

        if "|" not in line:
            return None

        artist, title = line.split("|", 1)

        status = subprocess.run(
            [
                "playerctl",
                "status"
            ],
            capture_output=True,
            text=True,
        )

        if status.returncode != 0:
            return None

        playback_status = status.stdout.strip()

        return {
            "title": title.strip(),
            "artist": artist.strip(),
            "playback_status": playback_status,
        }

    except Exception:
        return None


async def watch_media_changes(
    poll_interval: float = POLL_INTERVAL,
    debug: bool = WIN_DEBUG_ACTIVE,
) -> None:

    previous_signature = None
    had_session = True

    while True:
        media_info = await get_media_info()

        if media_info is None:
            if had_session:
                print("No active media session.")
                if VISUALISE_LYRICS:
                    stop_visualiser()

                had_session = False
                previous_signature = None

        else:
            start_time = time.time()
            had_session = True

            current_signature = (
                media_info["title"],
                media_info["artist"],
                media_info["playback_status"],
            )

            if (
                current_signature != previous_signature
                and media_info["playback_status"] == "Playing"
            ):

                aligned_path = await get_song_data(
                    artist=media_info["artist"],
                    title=media_info["title"],
                )

                if aligned_path:
                    entry_point = time.time() - start_time
                    track_key = (
                        media_info["title"],
                        media_info["artist"],
                    )

                    if VISUALISE_LYRICS:
                        visualise(
                            aligned_path,
                            entry_point,
                            track_key,
                        )

                    if debug:
                        print(
                            f'Currently playing: {media_info["title"]} '
                            f'by {media_info["artist"]}. '
                            f'Status: {media_info["playback_status"]}'
                        )

                else:
                    print(
                        "Oops! the song is instrumental! "
                        "we cannot handle this one, yet..."
                    )

                previous_signature = current_signature

        await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    try:
        print("Started Linux listener...")
        asyncio.run(watch_media_changes())
    except KeyboardInterrupt:
        print("Stopped media watcher.")