import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import aiofiles

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles the WebSocket connection, receives audio chunks,
    and saves them to a file.
    """
    await websocket.accept()
    print("WebSocket connection accepted.")

    # Use a context manager to ensure the file is closed properly
    try:
        async with aiofiles.open('output.webm', 'wb') as f:
            while True:
                # The frontend sends binary data (ArrayBuffer)
                data = await websocket.receive_bytes()
                await f.write(data)
                # Optional: Send a confirmation back to the client
                # await websocket.send_text("Chunk received")
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("WebSocket connection closed.")

@app.get("/")
def read_root():
    return {"message": "The Architect Backend is running."}
