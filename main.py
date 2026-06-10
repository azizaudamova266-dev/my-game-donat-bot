async def main():
    # 1. Webhook'ni o'chirib tashlash (xatoni yo'qotadi)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # 2. Web serverni ishga tushiramiz (Render uchun)
    await web_server()
    
    # 3. Botni polling rejimida ishga tushiramiz
    print("Bot ishga tushdi!")
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
