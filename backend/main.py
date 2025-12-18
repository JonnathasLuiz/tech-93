import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

async def ffmpeg_processor(websocket: WebSocket):
    """
    Creates an FFmpeg subprocess to convert incoming WebM/Opus audio
    stream to raw PCM audio format (16kHz, 16-bit signed little-endian).
    """
    try:
        # Command to convert WebM/Opus to raw PCM
        # -i pipe:0 -> read from stdin
        # -f s16le -> format is signed 16-bit little-endian PCM
        # -ar 16000 -> audio sample rate 16kHz
        # -ac 1 -> audio channels 1 (mono)
        # - -> output to stdout
        ffmpeg_command = [
            'ffmpeg',
            '-loglevel', 'error',
            '-i', 'pipe:0',
            '-f', 's16le',
            '-ar', '16000',
            '-ac', '1',
            'pipe:1'
        ]

        process = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )

        logger.info("FFmpeg subprocess started.")

        async def forward_to_ffmpeg():
            """Receives audio from WebSocket and forwards it to FFmpeg's stdin."""
            while True:
                try:
                    data = await websocket.receive_bytes()
                    if process.stdin.is_closing():
                        break
                    process.stdin.write(data)
                    await process.stdin.drain()
                except WebSocketDisconnect:
                    logger.info("Client disconnected. Closing FFmpeg stdin.")
                    break
                except Exception as e:
                    logger.error(f"Error receiving from websocket: {e}")
                    break

            if not process.stdin.is_closing():
                process.stdin.close()

        async def read_from_ffmpeg():
            """Reads processed PCM data from FFmpeg's stdout."""
            while True:
                # Read a chunk of PCM data. The size can be tuned.
                # 4096 bytes is a common chunk size.
                pcm_chunk = await process.stdout.read(4096)
                if not pcm_chunk:
                    logger.info("End of FFmpeg stdout stream.")
                    break

                # --- For the next step, this is where we'll send pcm_chunk to Deepgram ---
                # For now, we just confirm we are receiving data.
                logger.info(f"Received {len(pcm_chunk)} bytes of PCM data from FFmpeg.")


        # Run both tasks concurrently
        await asyncio.gather(forward_to_ffmpeg(), read_from_ffmpeg())

        # Wait for the process to terminate
        await process.wait()
        logger.info(f"FFmpeg process finished with exit code {process.returncode}.")

    except FileNotFoundError:
        logger.error("ffmpeg not found. Please ensure ffmpeg is installed and in your PATH.")
        await websocket.close(code=1011, reason="Server error: ffmpeg not available")
    except Exception as e:
        logger.error(f"An error occurred in ffmpeg_processor: {e}")
        if websocket.client_state != "DISCONNECTED":
            await websocket.close(code=1011, reason=f"Server error: {e}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handles the WebSocket connection and starts the audio processing pipeline."""
    await websocket.accept()
    logger.info("WebSocket connection accepted.")
    try:
        await ffmpeg_processor(websocket)
    except WebSocketDisconnect:
        logger.info("Client disconnected gracefully.")
    except Exception as e:
        logger.error(f"Error in websocket_endpoint: {e}")
    finally:
        logger.info("WebSocket connection closed.")

@app.get("/")
def read_root():
    return {"message": "The Architect Backend is running and ready for audio streaming."}
