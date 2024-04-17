from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import uvicorn
from openai import OpenAI
import requests, tempfile, asyncio, os

app = FastAPI()
client = OpenAI(api_key="API_KEY")

@app.get("/")
async def main():
    return FileResponse('static/index.html')

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket, input_text: str):
    await websocket.accept()
    try:
        completion = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a friendly AI assistant."},
                {"role": "user", "content": input_text},
            ],
            # stream=True,
            temperature=0,
            # max_tokens=500,
        )

        joke_text = completion.choices[0].message.content
        print(joke_text)
        await websocket.send_text(joke_text)

        audio_data = await generate_audio(joke_text, websocket)
        if audio_data:
            await websocket.send_bytes(audio_data)
    except Exception as e:
        await websocket.send_text(str(e))
    finally:
        await websocket.close()

import aiohttp
import asyncio

async def generate_audio(text, websocket):
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": "Bearer API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "model": "tts-1",
        "input": text,
        "voice": "nova",
        "response_format": "opus",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                headers = response.headers
                content_type = headers.get("Content-Type")
                content_length = int(headers.get("Content-Length"))

                # Set the response headers to match the audio file
                websocket.response.headers["Content-Type"] = content_type
                websocket.response.headers["Content-Length"] = content_length

                # Stream the audio data directly to the client
                async for chunk in response.content.iter_chunked(4096):
                    await websocket.send_bytes(chunk)
            else:
                print(f"Error: {response.status} - {await response.text()}")
                await websocket.send_text(f"Error: {response.status} - {await response.text()}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
