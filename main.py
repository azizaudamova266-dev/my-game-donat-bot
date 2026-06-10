import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()

class OrderState(StatesGroup):
    waiting_for_info = State()

# O'yinlar ro'yxati (Stikerlar bilan bezatilgan)
GAMES = {
    "brawlstars": {"name": "🎮 Brawl Stars", "items": {"30 Gem": "18.000", "80 Gem": "40.000", "170 Gem": "75.000", "360 Gem": "150.000"}},
    "pubg": {"name": "🔫 PUBG Mobile", "items": {"60 UC": "13.000", "325 UC": "62.000", "660 UC": "125.000", "1800 UC": "299.000"}},
    "stars": {"name": "⭐ Telegram Stars", "items": {"50 Stars": "15.000", "100 Stars": "28.000", "500 Stars": "128.000", "1000 Stars": "245.000"}},
    "standoff": {"name": "🔪 Standoff 2", "items": {"100G": "25.000", "500G": "97.000", "1000G": "180.000", "Gold Pass": "160.000"}},
    "roblox": {"name": "🌐 Roblox Robux", "items": {"40 R": "10.000", "400 R": "82.000", "800 R": "160.000", "1700 R": "315.000"}},
    "steam": {"name": "🎮 Steam USD", "items": {"1$": "15.000", "5$": "75.000", "10$": "150.000", "20$": "295.000"}},
    "premium": {"name": "💎 Telegram Premium", "items": {"1 oy": "55.000", "3 oy": "175.000", "6 oy": "230.000", "12 oy": "350.000"}}
}

@dp.message(Command("start"))
async def start(message: Message):
    text = "✨ **Xush kelibsiz, qadrli mijoz!** ✨\n\nDonat xizmatlarimizdan foydalanish uchun kerakli o'yin yoki xizmatni tanlang:\n\n🚀 *Tezkor va xavfsiz donat!*"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=GAMES[g]["name"], callback_data=f"game_{g}")] for g in GAMES])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("game_"))
async def show_items(callback: types.CallbackQuery):
    game = callback.data.split("_")[1]
    text = f"📦 {GAMES[game]['name']} uchun paketlardan birini tanlang:"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"💎 {item} — {price} UZS", callback_data=f"buy_{game}_{item.replace(' ', '_')}")] for item, price in GAMES[game]["items"].items()])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Ortga", callback_data="main_menu")])
    await callback.message.edit_text(text, reply_markup=kb)

@dp.callback_query(F.data == "main_menu")
async def back_to_menu(callback: types.CallbackQuery):
    text = "✨ **Asosiy menyu:**\n\nKerakli bo'limni tanlang:"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=GAMES[g]["name"], callback_data=f"game_{g}")] for g in GAMES])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("buy_"))
async def ask_info(callback: types.CallbackQuery, state: FSMContext):
    _, game, item = callback.data.split("_", 2)
    item = item.replace("_", " ")
    await state.update_data(game=game, item=item)
    
    texts = {
        "brawlstars": "📧 *Brawl Stars* tanlandi.\n\nIltimos, **Email va Kodni** yuboring (format: `email,kod`):",
        "pubg": "🔫 *PUBG Mobile* tanlandi.\n\nIltimos, **ID raqamingizni** yuboring:",
        "stars": "⭐ *Telegram Stars* tanlandi.\n\nIltimos, **@username** yoki **ID** yuboring:",
        "standoff": "🔪 *Standoff 2* tanlandi.\n\nIltimos, **ID raqamingizni** yuboring:",
        "roblox": "🌐 *Roblox* tanlandi.\n\nIltimos, **Username'ingizni** yuboring:",
        "steam": "🎮 *Steam* tanlandi.\n\nIltimos, **ID raqamingizni** yuboring:",
        "premium": "💎 *Telegram Premium* tanlandi.\n\nIltimos, **@username** yuboring:"
    }
    await callback.message.answer(texts.get(game, "Ma'lumot yuboring:"), parse_mode="Markdown")
    await state.set_state(OrderState.waiting_for_info)

@dp.message(OrderState.waiting_for_info)
async def process_info(message: Message, state: FSMContext):
    data = await state.get_data()
    text = (f"✅ **Buyurtmangiz qabul qilindi!**\n\n"
            f"🕹 O'yin: {GAMES[data['game']]['name']}\n"
            f"📦 Paket: {data['item']}\n"
            f"📝 Ma'lumot: `{message.text}`\n\n"
            f"⏳ Admin tez orada bog'lanadi. Iltimos, kuting!")
    await message.answer(text, parse_mode="Markdown")
    await state.clear()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
