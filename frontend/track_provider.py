import asyncio
import anyascii
import re
import requests
from config import PASSWORD
import json
from linux import get_media_info

async def get_song():
    media = await get_media_info()

    if media is None:
        return None
    # заглушка, потом поменять!!
    #media = {
        "title": "ванна, красный пол",
        "artist": "CUPSIZE",
        "playback_status": "Playing"
    #}

    slug = slugify(media["artist"] + "_" + media["title"])

    url = "https://api.lyricapp.ru/tracks/get"
    payload = create_payload(slug)

    #response = requests.post(url, json=payload)

    #print(response)
    #print(response.headers)
    #print(response.text)


    song = get_song_data()
    return song


def slugify(text: str):
    normalized = anyascii.anyascii(text)
    normalized = normalized.lower()
    normalized = re.sub(r"\s+", "_", normalized)
    normalized = re.sub(r"[^a-z0-9_]", "", normalized)
    return normalized.strip("_")

def get_song_data():
    with open("mock_response.json", encoding="utf-8") as f:
        return json.load(f)

def create_payload(slug: str):
    return {
        "user_id": 1,
        "password": PASSWORD,
        "slug": slug
    }

if __name__ == "__main__":
    asyncio.run(get_song())
