import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiohttp import web

# Loglarni yoqamiz (xatolarni ko'rish uchun)
logging.basicConfig(level=logging.INFO)

# Render'dan o'zgaruvchilarni olamiz
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Holatlar (States)
class OrderState(StatesGroup):
    waiting_for_info = State()

# O'yinlar va narxlar
GAMES = {
    "bs": {"name": "🎮 Brawl Stars", "items": {"30 Gem": "18.000", "80 Gem": "40.000"}},
    "pubg": {"name": "🔫 PUBG Mobile", "items": {"60 UC": "13.000", "300 UC": "55.000"}},
    "st2": {"name": "🔪 Standoff 2", "items": {"100G": "25.000", "500G": "97.000"}},
    "roblox": {"name": "🌐 Roblox", "items": {"40 R": "10.000", "400 R": "82.000"}}
}

@dp.message(Command("start"))
async def start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=GAMES[g]["name"], callback_data=f"game_{g}")] for g in GAMES])
    await message.answer("Xush kelibsiz! O'yinni tanlang:", reply_markup=kb)

@dp.callback_query(F.data.startswith("game_"))
async def show_items(callback: types.CallbackQuery):
    game = callback.data.split("_")[1]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{item} - {price} UZS", callback_data=f"buy_{game}_{item}")] for item, price in GAMES[game]["items"].items()])
    await callback.message.edit_text(f"{GAMES[game]['name']} paketini tanlang:", reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_"))
async def ask_info(callback: types.CallbackQuery, state: FSMContext):
    game, item = callback.data.split("_")[1], callback.data.split("_")[2]
    await state.update_data(game=game, item=item)
    
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

async def web_server():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
