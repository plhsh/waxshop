from aiogram import Bot, Dispatcher, executor, types
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Обработчик сообщений
@dp.message_handler()
async def echo(message: types.Message):
    chat_id = message.chat.id
    await message.answer(f"Эхо: {message.text}\nID чата: {chat_id}")

if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
