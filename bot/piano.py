import json
import os

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

from database.mongo_db import Database
from scraper.tap_az import parse_and_save

router = Router()

db = Database()

token = os.getenv("BOT_TOKEN")

dp = Dispatcher()
dp.include_router(router)

bot = Bot(token=token, parse_mode="HTML")


@router.message(Command(commands=['start']))
async def start(message: types.Message):
    await message.answer(
        "Бот для поиска объявлений с Tap az, введите название товара",
    )
    db.set_user_last_viewed_index(message.from_user.id, 0)


@router.message(lambda message: message.text == "Следующий")
async def next_item(message: types.Message):
    await send_next_item(message)


@router.message()
async def search_item(message: types.Message):
    item_name = message.text
    user_id = message.from_user.id
    await message.reply('Запрос принял, собираю данные...')
    db.delete_all_items(user_id)
    parse_and_save(user_id, item_name)
    await send_next_item(message)


async def send_next_item(message: types.Message):
    last_viewed_index = db.get_user_last_viewed_index(message.from_user.id)

    if not hasattr(send_next_item, "current_index"):
        send_next_item.current_index = last_viewed_index

    cursor = db.get_all_items(message.from_user.id)

    items_data = []

    for doc in cursor:
        doc_json = json.dumps(doc, ensure_ascii=False)
        doc_dict = json.loads(doc_json)
        name = doc_dict["name"]
        price = doc_dict["price"]
        created = doc_dict["created"]
        link = doc_dict["link"]

        caption = f"<b>{name}</b>\n"
        caption += f"Цена: <code>{price} AZN</code>\n"
        caption += f"Создано: {created}\n"
        caption += f"ссылка: {link}"

        try:
            img_url = doc_dict["image_url"]
            items_data.append((img_url, caption))
        except KeyError:
            continue

    if not items_data:
        await message.answer("Ничего не удалось найти по запросу")
        return

    send_next_item.current_index %= len(items_data)
    img_url, caption = items_data[send_next_item.current_index]
    send_next_item.current_index += 1

    if last_viewed_index != len(items_data):
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
        await message.answer("Вы просмотрели весь список объявлений")

    db.set_user_last_viewed_index(message.from_user.id, send_next_item.current_index)


# async def main():
#     load_dotenv()

    
#     await bot.delete_webhook()
#     await dp.start_polling(bot)
