import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tviyastrogid_handlers import router, daily_broadcast

bot = Bot(token="7237692096:AAGh_SBPZad4zJ-wi6XNp1-UCrGLd1INnn8")
dp = Dispatcher()

def dev_give_cards_on_start(user_id: int, amount: int):
    db = sqlite3.connect("tviyastrogid.db")
    cur = db.cursor()
    cur.execute("UPDATE users SET cards = ? WHERE id = ?", (amount, user_id))
    db.commit()
    db.close()


dev_give_cards_on_start(user_id=1512807520, amount=100)

async def main():
    dp.include_router(router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_broadcast, "cron", hour=9, minute=00, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")