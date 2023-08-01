# import asyncio
# import logging


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     asyncio.run(main())
from bot.piano import bot, dp
import os


from fastapi import FastAPI
from aiogram import Dispatcher, Bot, types
import uvicorn

from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()


app = FastAPI()
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST') 
WEBHOOK_PATH = f'/bot/{BOT_TOKEN}' 
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'


@app.on_event('startup')
async def startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: Dict[str, Any]):
    telegram_update = types.Update(**update)
    Dispatcher.feed_webhook_update(dp)
    Bot.get_updates(bot)
    await dp._process_update(telegram_update)


@app.on_event('shutdown')
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
