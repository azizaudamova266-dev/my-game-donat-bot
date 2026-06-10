import logging

# Loglarni yoqish (bu xatolikni Render logida ko'rsatib beradi)
logging.basicConfig(level=logging.INFO
                    import os

import asyncio

from aiogram import Bot, Dispatcher, F, types

from aiogram.filters import Command

from aiogram.fsm.context import FSMContext

from aiogram.fsm.state import State, StatesGroup

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from aiohttp import web



TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)

dp = Dispatcher()



# Holatlar (States)

class OrderState(StatesGroup):

    waiting_for_info = State()



# Narxlar va ularning tugmalari

GAMES = {

    "bs": {"name": "🎮 Brawl Stars", "items": {"30 Gem": "18.000", "80 Gem": "40.000", "170 Gem": "75.000"}},

    "pubg": {"name": "🔫 PUBG Mobile", "items": {"60 UC": "13.000", "300 UC": "55.000"}}

}



@dp.message(Command("start"))

async def start(message: Message):

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=GAMES[g]["name"], callback_data=f"game_{g}")] for g in GAMES])

    await message.answer("Xush kelibsiz! O'yinni tanlang:", reply_markup=kb)



@dp.callback_query(F.data.startswith("game_"))

async def show_items(callback: types.CallbackQuery):

    game = callback.data.split("_")[1]

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{item} - {price}", callback_data=f"buy_{game}_{item}")] for item, price in GAMES[game]["items"].items()])

    await callback.message.edit_text(f"{GAMES[game]['name']} paketini tanlang:", reply_markup=kb)



@dp.callback_query(F.data.startswith("buy_"))

async def ask_info(callback: types.CallbackQuery, state: FSMContext):

    game, item = callback.data.split("_")[1], callback.data.split("_")[2]

    await state.update_data(game=game, item=item)

    

    # O'yin turiga qarab so'rov

    if game == "bs":

        text = "Brawl Stars uchun Email va Kodni yuboring (format: email,kod):"

    elif game == "pubg":

        text = "PUBG uchun ID raqamingizni yuboring:"

    elif game == "roblox":

        text = "Roblox Username'ingizni yuboring:"

    else:

        text = "ID raqamingizni yuboring:"

        

    await callback.message.answer(text)

    await state.set_state(OrderState.waiting_for_info)



@dp.message(OrderState.waiting_for_info)

async def process_info(message: Message, state: FSMContext):

    data = await state.get_data()

    await message.answer(f"✅ Buyurtma qabul qilindi!\nO'yin: {data['game']}\nPaket: {data['item']}\nMa'lumot: {message.text}\n\nAdmin tez orada bog'lanadi.")

    await state.clear()



# ... (web_server va main qismi avvalgidek qoladi) ...
