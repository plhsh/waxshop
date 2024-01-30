from aiogram import Bot, Dispatcher
from config import Config

BOT_TOKEN = Config.BOT_TOKEN

# Initialize the bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

