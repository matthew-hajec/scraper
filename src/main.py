import os
import math
import logging
import threading
from dotenv import load_dotenv
from scheduling.job import RepeatableJob
from scheduling.schedulers import GroupedDelayScheduler
from utils.data_pull import data_update
from external_data.steam.models import load_tables as steam_create_db_tables
from external_data.steam.api import get_listings_page
from utils.db import init_engine
import requests


logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s::%(levelname)s %(asctime)s: %(message)s',
    # log to file if file provided in env, otherwise log to console
    filename=os.getenv('LOG_FILE', None)
)


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logger.info("Starting application")

    load_dotenv()

    db_engine = init_engine()
    logger.info(f'Running with database dialect: {db_engine.dialect.name}')

    sched = GroupedDelayScheduler()

    if (os.getenv('STEAM_ITEMS_APP_ID')):
        steam_create_db_tables(db_engine)

        app_id = int(os.getenv('STEAM_ITEMS_APP_ID'))
        num_items = int(os.getenv('STEAM_ITEMS_NUM_ITEMS'))
        max_fails = int(os.getenv('STEAM_ITEMS_MAX_FAILS', '9'))

        steam_listing_jobs = []

        for i in range(math.ceil(num_items / 100)):
            start = i * 100
            steam_listing_jobs.append(RepeatableJob(
                delay_tm=4,
                func=data_update,
                db_engine=db_engine,
                title=f'Steam - {app_id} Market Listings (start={start}, count=100)',
                data_func=get_listings_page,
                max_failures=max_fails,
                app_id=app_id,
                count=100
            ))

        sched.add_job_group(steam_listing_jobs, group_delay=2)

    while True:
        job = sched.next_job()
        t = threading.Thread(target=job.execute)
        t.run()
