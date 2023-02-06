from aiogram.utils import executor
from init_bot import dp, bot
import suptech
import json
from middleware import ThrottlingMiddleware

with open("/app/suptech-bot/other_bots/delivery_support_bot/testing/delivery_bot_v2/config.json", "r") as j:
    CONF = json.load(j)

if __name__ == '__main__':
    import handlers
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True)
