import os
import asyncio
from aiogram import Bot, Dispatcher
from aiohttp import web

# Token va Admin ID
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Render uchun oddiy web server (bot o'chib qolmasligi uchun)
async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()

async def main():
    # Web serverni ishga tushiramiz
    await web_server()
    # Botni ishga tushiramiz
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
