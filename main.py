import os

import uvicorn
from aiogram import types
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from bot.piano import bot, bot_token, dp

load_dotenv()

app = FastAPI()

WEBHOOK_HOST = os.getenv('WEBHOOk_HOST')


@app.on_event("startup")
async def on_startup():
    webhook_uri = f'{WEBHOOK_HOST}/{bot_token}'
    await bot.set_webhook(webhook_uri)


@app.on_event('shutdown')
async def on_shutdown():
    await bot.delete_webhook()


@app.post(f"/{bot_token}")
async def webhook(request: Request):
    update = types.Update(**await request.json())
    await dp.process_update(update)
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
