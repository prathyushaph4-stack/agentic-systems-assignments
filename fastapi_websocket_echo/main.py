from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            print(f"Received from client: {data}")

            # Send response back
            await websocket.send_text(f"Server received: {data}")

    except WebSocketDisconnect:
        print("Client disconnected")