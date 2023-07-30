import json
import os

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

from database.mongo_db import Database

router = Router()

db = Database()


@router.message(Command(commands=["start"]))
async def start(message: types.Message):
    await message.answer("Tap az'dan melumat toplayan botam")
    db.set_user_last_viewed_index(message.from_user.id, 0)
    await next_piano(message)
    await next_piano(message)


@router.message(lambda message: message.text == "Следующий")
async def next_piano(message: types.Message):
    await send_next_piano(message)


async def send_next_piano(message: types.Message):
    
    last_viewed_index = db.get_user_last_viewed_index(message.from_user.id)
    
    if not hasattr(send_next_piano, "current_index"):
        send_next_piano.current_index = last_viewed_index

    cursor = db.get_all_pianos()

    pianos_data = []

    for doc in cursor:
        doc_json = json.dumps(doc, ensure_ascii=False)
        doc_dict = json.loads(doc_json)
        name = doc_dict["name"]
        price = doc_dict["price"]
        created = doc_dict["created"]
        link = doc_dict["link"]

        caption = f"<b>{name}</b>\n"
        caption += f"Цена: <code>{price}</code>\n"
        caption += f"Создано: {created}\n"
        caption += f"ссылка: {link}"

        try:
            img_url = doc_dict["image_url"]
            pianos_data.append((img_url, caption))
        except KeyError:
            continue

    if not pianos_data:
        await message.answer("No pianos data available.")
        return

    send_next_piano.current_index %= len(pianos_data)
    img_url, caption = pianos_data[send_next_piano.current_index]
    send_next_piano.current_index += 1

    if last_viewed_index != len(pianos_data):
        await message.answer_photo(
            img_url,
            caption=caption,
            parse_mode=types.UNSET_PARSE_MODE,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Следующий")],
                ],
                resize_keyboard=True,
            ),
        )
    else:
        await message.answer('Вы просмотрели весь список объявлений')
    
    db.set_user_last_viewed_index(message.from_user.id, send_next_piano.current_index)


async def main():
    
    load_dotenv()
    
    token = os.getenv('BOT_TOKEN')
    
    dp = Dispatcher()
    dp.include_router(router)

    bot = Bot(token=token, parse_mode="HTML")
    await dp.start_polling(bot)
