import json
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from database.mongo_db import Database
from scraper.tap_az import parse_and_save

db = Database()

bot_token = os.getenv("BOT_TOKEN")

bot = Bot(token=bot_token)
Bot.set_current(bot)

dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Бот для поиска объявлений с Tap az, введите название товара",
    )
    db.set_user_last_viewed_index(message.from_user.id, 0)


@dp.message_handler(lambda message: message.text == "Следующий")
async def next_item(message: types.Message):
    await send_next_item(message)


@dp.message_handler()
async def search_item(message: types.Message):
    item_name = message.text
    user_id = message.from_user.id
    await message.reply("Запрос принял, собираю данные...")
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

        try:
            img_url = doc_dict["image_url"]
            items_data.append((img_url, caption, link))
        except KeyError:
            continue

    if not items_data:
        await message.answer("Ничего не удалось найти по запросу")
        return

    send_next_item.current_index %= len(items_data)
    img_url, caption, item_link = items_data[send_next_item.current_index]
    send_next_item.current_index += 1

    if last_viewed_index != len(items_data):
        
        inline_keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text="Перейти", url=item_link)
        )
        
        await message.answer_photo(
            img_url,
            caption=caption,
            parse_mode=types.ParseMode.HTML,
            reply_markup=inline_keyboard,  # Use inline_keyboard here
        )
    else:
        await message.answer("Вы просмотрели весь список объявлений")

    db.set_user_last_viewed_index(message.from_user.id, send_next_item.current_index)
