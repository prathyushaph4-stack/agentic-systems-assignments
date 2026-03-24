import asyncio
import websockets

async def test():
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        await websocket.send("Hello Server")
        response = await websocket.recv()
        print(response)

asyncio.run(test())
