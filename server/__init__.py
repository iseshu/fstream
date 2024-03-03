from fastapi import FastAPI
from uvicorn import Server as UvicornServer, Config
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from math import ceil, floor
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from bot import bot

def size_format(b):
    if b < 1000:
              return '%i' % b + 'B'
    elif 1000 <= b < 1000000:
        return '%.1f' % float(b/1000) + 'KB'
    elif 1000000 <= b < 1000000000:
        return '%.1f' % float(b/1000000) + 'MB'
    elif 1000000000 <= b < 1000000000000:
        return '%.1f' % float(b/1000000000) + 'GB'
    elif 1000000000000 <= b:
        return '%.1f' % float(b/1000000000000) + 'TB'

async def check_file(id):
    message = await bot.get_messages(-1001922965510, id)
    if message.document or message.audio or message.video:
        file_name = message.document.file_name
        mime_type = message.document.mime_type
        file_size = message.document.file_size
        return {"file_name": file_name, "mime_type": mime_type, "file_size": file_size,"message":message}

@app.get("/")
async def read_root():
    me = await bot.get_me()
    user_name = me.username
    return {"message": "Hello World", "bot": user_name}

@app.get("/dl/{item_id}/{file_name}")
async def read_item(item_id: int, file_name: str):
    message = await check_file(item_id)
    if not message or not file_name:
        return {"error": "file not found"}

    file_size = message["file_size"]  # Assigning file_size here
    from_bytes = 0
    until_bytes = file_size - 1
    chunk_size = 1024 * 1024
    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1
    req_length = until_bytes - from_bytes + 1
    part_count = ceil(until_bytes / chunk_size) - floor(offset / chunk_size)
    mime_type = message["mime_type"]
    file_name = message["file_name"]
    message = message['message']

    headers = {
        "Content-Type": mime_type,
        "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
        "Content-Length": str(req_length),
        "Content-Disposition": f'attachment; filename="{file_name}"',
        "Accept-Ranges": "bytes",
    }

    async def file_generator():
        current_part = 1
        async for chunk in bot.stream_media(message, offset=offset):
            if not chunk:
                break
            elif part_count == 1:
                yield chunk[first_part_cut:last_part_cut]
            elif current_part == 1:
                yield chunk[first_part_cut:]
            elif current_part == part_count:
                yield chunk[:last_part_cut]
            else:
                yield chunk

            current_part += 1

            if current_part > part_count:
                break

    return StreamingResponse(file_generator(), headers=headers, status_code=206)

server = UvicornServer (
    Config (
        app=app,
        host="0.0.0.0",
        port=8080
    )
)
