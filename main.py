import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

# Loglarni yoqish
logging.basicConfig(level=logging.INFO)

# Botni ishga tushirish
TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Holatlar
class OrderState(StatesGroup):
    waiting_for_info = State()

# Barcha narxlar ro'yxati
GAMES = {
    "brawlstars": {
        "name": "🎮 Brawl Stars", 
        "items": {"30 Gem": "18.000", "80 Gem": "40.000", "170 Gem": "75.000", "360 Gem": "150.000", "950 Gem": "359.000", "2000 Gem": "710.000", "Brawl Pass": "66.000", "Brawl Pass+": "99.000", "PRO PASS": "179.000"}
    },
    "pubg": {
        "name": "🔫 PUBG Mobile", 
        "items": {"60 UC": "13.000", "120 UC": "26.000", "180 UC": "38.000", "325 UC": "62.000", "385 UC": "73.000", "660 UC": "125.000", "720 UC": "137.000", "985 UC": "185.000", "1320 UC": "245.000", "1800 UC": "299.000", "2125 UC": "360.000", "3120 UC": "540.000", "3850 UC": "585.000", "5170 UC": "825.000", "5650 UC": "880.000", "8100 UC": "1.150.000", "12010 UC": "1.725.000", "16200 UC": "2.280.000", "20050 UC": "2.860.000", "24300 UC": "3.400.000", "32400 UC": "4.530.000", "40500 UC": "5.660.000", "50400 UC": "7.100.000", "81000 UC": "11.300.000"}
    },
    "stars": {
        "name": "⭐ Telegram Stars", 
        "items": {"50 Stars": "15.000", "75 Stars": "23.000", "100 Stars": "28.000", "150 Stars": "40.000", "200 Stars": "54.000", "250 Stars": "67.000", "350 Stars": "93.000", "500 Stars": "128.000", "750 Stars": "189.000", "1000 Stars": "245.000", "2500 Stars": "600.000", "5000 Stars": "1.180.000"}
    },
    "standoff": {
        "name": "🔪 Standoff 2", 
        "items": {"100G": "25.000", "500G": "97.000", "1000G": "180.000", "3000G": "390.000", "6000G": "780.000", "9000G": "1.150.000", "GOLD PASS": "160.000", "GOLD PASS +10lvl": "250.000"}
    },
    "roblox": {
        "name": "🌐 Roblox Robux", 
        "items": {"40 Robux": "10.000", "80 Robux": "19.000", "120 Robux": "29.000", "160 Robux": "39.000", "200 Robux": "49.000", "500 Robux": "82.000", "1000 Robux": "160.000", "2000 Robux": "315.000", "5250 Robux": "782.000", "11000 Robux": "1.639.000"}
    },
    "steam": {
        "name": "🎮 Steam USD", 
        "items": {"1$": "15.000", "2.5$": "37.500", "5$": "75.000", "10$": "150.000", "15$": "225.000", "20$": "295.000"}
    },
    "premium": {
        "name": "💎 Telegram Premium", 
        "items": {"1 oy": "55.000", "3 oy": "175.000", "6 oy": "230.000", "12 oy": "350.000"}
    }
}

@dp.message(Command("start"))
async def start(message: Message):
    text = "✨ **Xush kelibsiz!** \n\nDonat xizmatini tanlang:"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=GAMES[g]["name"], callback_data=f"game_{g}")] for g in GAMES])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("game_"))
async def show_items(callback: types.CallbackQuery):
    game = callback.data.split("_")[1]
    buttons = [[InlineKeyboardButton(text=f"{item} — {price} UZS", callback_data=f"buy_{game}_{item.replace(' ', '_')}")] for item, price in GAMES[game]["items"].items()]
    buttons.append([InlineKeyboardButton(text="🔙 Ortga", callback_data="main_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(f"{GAMES[game]['name']} narxlari:", reply_markup=kb)

@dp.callback_query(F.data == "main_menu")
async def back_to_menu(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=GAMES[g]["name"], callback_data=f"game_{g}")] for g in GAMES])
    await callback.message.edit_text("Donat xizmatini tanlang:", reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_"))
async def ask_info(callback: types.CallbackQuery, state: FSMContext):
    _, game, item = callback.data.split("_", 2)
    item = item.replace("_", " ")
    await state.update_data(game=game, item=item)
    
    texts = {
        "brawlstars": "📧 Email va Kodni yuboring (format: `email,kod`):",
        "pubg": "🆔 PUBG ID raqamingizni yuboring:",
        "stars": "👤 Telegram @username yoki ID yuboring:",
        "standoff": "🆔 Standoff 2 ID raqamingizni yuboring:",
        "roblox": "👤 Roblox Username yuboring:",
        "steam": "🆔 Steam ID raqamingizni yuboring:",
        "premium": "👤 Telegram @username yuboring:"
    }
    await callback.message.answer(texts.get(game, "Iltimos, kerakli ma'lumotni yuboring:"), parse_mode="Markdown")
    await state.set_state(OrderState.waiting_for_info)

@dp.message(OrderState.waiting_for_info)
async def process_info(message: Message, state: FSMContext):
    data = await state.get_data()
    # Adminga xabar yuborish
    admin_text = (f"🔔 **YANGI BUYURTMA KELDI!**\n\n"
                  f"👤 Mijoz: {message.from_user.full_name}\n"
                  f"🆔 Username: @{message.from_user.username or 'Mavjud emas'}\n"
                  f"🔗 Link: tg://user?id={message.from_user.id}\n\n"
                  f"🕹 O'yin: {GAMES[data['game']]['name']}\n"
                  f"📦 Paket: {data['item']}\n"
                  f"📝 Ma'lumot: `{message.text}`")
    
    await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    await message.answer("✅ Buyurtmangiz qabul qilindi! Admin tez orada siz bilan bog'lanadi.")
    await state.clear()

async def main():
    # Menyu tugmasi (Menu)
    await bot.set_my_commands([types.BotCommand(command="start", description="Botni ishga tushirish")])
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
