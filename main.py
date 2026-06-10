import os
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiohttp import web

# Render'dan o'zgaruvchilarni olamiz
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Narxlar lug'ati
GAME_PRICES = {
    "bs": "🎮 **Brawl Stars narxlari:**\n\n💎 30 Gem — 18.000 so'm\n💎 80 Gem — 40.000 so'm\n💎 170 Gem — 75.000 so'm\n💎 360 Gem — 150.000 so'm\n💎 950 Gem — 359.000 so'm\n💎 2000 Gem — 710.000 so'm\n\n🛡 Brawl Pass — 66.000 so'm\n🛡 Brawl Pass+ — 99.000 so'm\n🛡 PRO PASS — 179.000 so'm",
    "pubg": "🔫 **PUBG Mobile UC narxlari:**\n\n60 UC — 13.000 | 120 UC — 26.000\n180 UC — 38.000 | 325 UC — 62.000\n385 UC — 73.000 | 660 UC — 125.000\n720 UC — 137.000 | 985 UC — 185.000\n1320 UC — 245.000 | 1800 UC — 299.000\n2125 UC — 360.000 | 3120 UC — 540.000\n(Boshqa ko'plab paketlar mavjud...)",
    "stars": "⭐️ **Telegram Stars:**\n\n😎 50 — 15.000 | 😎 100 — 28.000\n😎 500 — 128.000 | 😎 1000 — 245.000\n😎 2500 — 600.000 | 😎 5000 — 1.180.000",
    "st2": "🔪 **Standoff 2 Gold:**\n\n⭐️ 100G — 25.000 | ⭐️ 500G — 97.000\n⭐️ 1000G — 180.000 | ⭐️ 3000G — 390.000\n🤴 Gold Pass — 160.000",
    "roblox": "🌐 **Roblox Robux:**\n\n40 R — 10.000 | 160 R — 39.000\n400 R — 82.000 | 800 R — 160.000\n1700 R — 315.000 | 4500 R — 782.000",
    "steam": "📱 **Steam USD (ID orqali):**\n\n🪙 1$ — 15.000 | 🪙 5$ — 75.000\n🪙 10$ — 150.000 | 🪙 20$ — 295.000",
    "prem": "💎 **Telegram Premium:**\n\n1 oy — 55.000 | 3 oy — 175.000\n6 oy — 230.000 | 12 oy — 350.000"
}

def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Brawl Stars", callback_data="bs")],
        [InlineKeyboardButton(text="🔫 PUBG Mobile", callback_data="pubg")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="stars")],
        [InlineKeyboardButton(text="🔪 Standoff 2", callback_data="st2")],
        [InlineKeyboardButton(text="🌐 Roblox", callback_data="roblox")],
        [InlineKeyboardButton(text="🎮 Steam", callback_data="steam")],
        [InlineKeyboardButton(text="💎 Telegram Premium", callback_data="prem")]
    ])
    return kb

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Assalomu alaykum! Donat xizmatiga xush kelibsiz. O'yinni tanlang:", reply_markup=main_menu())

@dp.callback_query(F.data.in_(GAME_PRICES.keys()))
async def show_price(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Sotib olish", callback_data=f"buy_{callback.data}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")]
    ])
    await callback.message.edit_text(GAME_PRICES[callback.data], reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await callback.message.edit_text("O'yinni tanlang:", reply_markup=main_menu())

@dp.callback_query(F.data.startswith("buy_"))
async def buy_process(callback: types.CallbackQuery):
    game = callback.data.split("_")[1]
    await callback.message.answer(f"Siz {game.upper()} tanladingiz.\nIltimos, o'yin ID raqamingizni yuboring:")

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
    asyncio.run(main()
