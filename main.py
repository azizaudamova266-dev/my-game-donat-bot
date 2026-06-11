import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
bot = Bot(token=TOKEN)
dp = Dispatcher()

class OrderState(StatesGroup):
    waiting_for_payment_proof = State()
    waiting_for_info = State()

GAMES = {
    "brawlstars": {"name": "🎮 Brawl Stars", "items": {"30 Gem": "18.000", "80 Gem": "40.000", "170 Gem": "75.000", "360 Gem": "150.000", "950 Gem": "359.000", "2000 Gem": "710.000", "Brawl Pass": "66.000", "Brawl Pass+": "99.000", "PRO PASS": "179.000"}},
    "pubg": {"name": "🔫 PUBG Mobile", "items": {"60 UC": "13.000", "120 UC": "26.000", "180 UC": "38.000", "325 UC": "62.000", "385 UC": "73.000", "660 UC": "125.000", "720 UC": "137.000", "985 UC": "185.000", "1320 UC": "245.000", "1800 UC": "299.000", "2125 UC": "360.000", "3120 UC": "540.000", "3850 UC": "585.000", "5170 UC": "825.000", "5650 UC": "880.000", "8100 UC": "1.150.000", "12010 UC": "1.725.000", "16200 UC": "2.280.000", "20050 UC": "2.860.000", "24300 UC": "3.400.000", "32400 UC": "4.530.000", "40500 UC": "5.660.000", "50400 UC": "7.100.000", "81000 UC": "11.300.000"}},
    "stars": {"name": "⭐ Telegram Stars", "items": {"50 Stars": "15.000", "75 Stars": "23.000", "100 Stars": "28.000", "150 Stars": "40.000", "200 Stars": "54.000", "250 Stars": "67.000", "350 Stars": "93.000", "500 Stars": "128.000", "750 Stars": "189.000", "1000 Stars": "245.000", "2500 Stars": "600.000", "5000 Stars": "1.180.000"}},
    "standoff": {"name": "🔪 Standoff 2", "items": {"100G": "25.000", "500G": "97.000", "1000G": "180.000", "3000G": "390.000", "6000G": "780.000", "9000G": "1.150.000", "GOLD PASS": "160.000", "GOLD PASS +10lvl": "250.000"}},
    "roblox": {"name": "🌐 Roblox Robux", "items": {"40 Robux": "10.000", "80 Robux": "19.000", "120 Robux": "29.000", "160 Robux": "39.000", "200 Robux": "49.000", "500 Robux": "82.000", "1000 Robux": "160.000", "2000 Robux": "315.000", "5250 Robux": "782.000", "11000 Robux": "1.639.000"}},
    "steam": {"name": "🎮 Steam USD", "items": {"1$": "15.000", "2.5$": "37.500", "5$": "75.000", "10$": "150.000", "15$": "225.000", "20$": "295.000"}},
    "premium": {"name": "💎 Telegram Premium", "items": {"1 oy": "55.000", "3 oy": "175.000", "6 oy": "230.000", "12 oy": "350.000"}}
}

@dp.message(Command("start"))
async def start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=GAMES[g]["name"], callback_data=f"game_{g}")] for g in GAMES])
    await message.answer("✨ **Xush kelibsiz!** Kerakli xizmatni tanlang:", reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("game_"))
async def show_items(callback: types.CallbackQuery):
    game = callback.data.split("_")[1]
    buttons = [[InlineKeyboardButton(text=f"{item} — {price} UZS", callback_data=f"buy_{game}_{item.replace(' ', '_')}")] for item, price in GAMES[game]["items"].items()]
    buttons.append([InlineKeyboardButton(text="🔙 Ortga", callback_data="main_menu")])
    await callback.message.edit_text(f"{GAMES[game]['name']} narxlari:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data == "main_menu")
async def back_to_menu(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=GAMES[g]["name"], callback_data=f"game_{g}")] for g in GAMES])
    await callback.message.edit_text("Kerakli xizmatni tanlang:", reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_"))
async def ask_payment(callback: types.CallbackQuery, state: FSMContext):
    _, game, item = callback.data.split("_", 2)
    item = item.replace("_", " ")
    await state.update_data(game=game, item=item)
    text = (f"💳 **To'lov jarayoni**\n\nSiz tanladingiz: {item}\nNarxi: {GAMES[game]['items'][item]} UZS\n\n"
            f"To'lov uchun karta ma'lumotlari:\n💳 Karta: `8600 0000 0000 0000`\n👤 Ism: **Aziza Udamova** (A.U)\n\n"
            f"To'lov qilgan bo'lsangiz tugmani bosing:")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ To'lov qildim", callback_data="confirm_payment")], [InlineKeyboardButton(text="🔙 Ortga", callback_data=f"game_{game}")]])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "confirm_payment")
async def request_proof(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📸 Iltimos, **to'lov chekini (rasm)** yuboring:")
    await state.set_state(OrderState.waiting_for_payment_proof)

@dp.message(OrderState.waiting_for_payment_proof, F.photo)
async def process_proof(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    data = await state.get_data()
    texts = {"brawlstars": "📧 Email va Kodni yuboring:", "pubg": "🆔 PUBG ID yuboring:", "stars": "👤 Username yoki ID:", "standoff": "🆔 Standoff ID:", "roblox": "👤 Roblox Username:", "steam": "🆔 Steam ID:", "premium": "👤 Telegram Username:"}
    await message.answer(texts.get(data['game'], "Ma'lumotni yuboring:"))
    await state.set_state(OrderState.waiting_for_info)

@dp.message(OrderState.waiting_for_info)
async def process_info(message: Message, state: FSMContext):
    data = await state.get_data()
    admin_text = (f"🔔 **YANGI BUYURTMA!**\n\n👤 Mijoz: {message.from_user.full_name}\n🆔 Username: @{message.from_user.username or 'Yo\'q'}\n"
                  f"🕹 O'yin: {GAMES[data['game']]['name']}\n📦 Paket: {data['item']}\n📝 Info: `{message.text}`")
    await bot.send_photo(chat_id=ADMIN_ID, photo=data['photo'], caption=admin_text, parse_mode="Markdown")
    await message.answer("✅ Buyurtmangiz va chek qabul qilindi! Admin tez orada bog'lanadi.")
    await state.clear()

async def main():
    await bot.set_my_commands([types.BotCommand(command="start", description="Botni ishga tushirish")])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
