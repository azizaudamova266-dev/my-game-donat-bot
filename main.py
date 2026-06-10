import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# O'z tokeningizni shu yerga yozing
TOKEN = "8711248483:AAFxH2cdU_igpYh2Dhe21-FnEDhOZg70egw"
ADMIN_ID = 7465898804 # O'z ID raqamingizni yozing

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Asosiy menyu
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🎮 O'yinlar")],
    [KeyboardButton(text="👤 Profil")]
], resize_keyboard=True)

# Admin menyusi
admin_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📊 Statistika")],
    [KeyboardButton(text="📩 Rasylka")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin panelga xush kelibsiz!", reply_markup=admin_kb)
    else:
        await message.answer("Salom! Donat botga xush kelibsiz.", reply_markup=main_kb)

@dp.message(F.text == "📊 Statistika")
async def stats(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Bot hozircha test rejimida.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
