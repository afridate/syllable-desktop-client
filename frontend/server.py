import asyncio
from websockets import serve
import json
from track_provider import get_song

async def handler(websocket):
    print("Браузер подключился!")

    song = await get_song()

    await websocket.send(json.dumps(song))

    await websocket.wait_closed()

async def main():
    async with serve(handler, "localhost", 8765):
        print("WebSocket сервер запущен")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())