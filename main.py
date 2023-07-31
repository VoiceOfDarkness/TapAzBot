import asyncio
import logging
import time

import schedule

from bot.piano import main
from scraper.tap_az import parse_and_save

# def worker():
#     parse()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    # schedule.every(24).hours.do(worker)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
