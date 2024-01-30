import logging
from aiogram import executor
from handlers import dp

# Enable logging
logging.basicConfig(level=logging.INFO)

# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)


