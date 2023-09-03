import os
import sys
import math
import logging
import threading
from dotenv import load_dotenv
from scheduling.job import RepeatableJob
from scheduling.schedulers import GroupedDelayScheduler
from utils.data_pull import create_update_partial
from models import load_tables as create_main_db_tables
from external_data.steam.models import load_tables as create_steam_db_tables
from external_data.steam.api import get_listings_page
from utils.db import init_engine
from functools import partial

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s::%(levelname)s %(asctime)s: %(message)s',
    # log to file if file provided in env, otherwise log to console
    filename=os.getenv('LOG_FILE', None)
)


logger = logging.getLogger(__name__)


def main():
    logger.info("Starting application")

    load_dotenv()

    db_engine = init_engine()
    logger.info(f'Running with database dialect: {db_engine.dialect.name}')

    create_main_db_tables(db_engine)

    sched = GroupedDelayScheduler()

    if (os.getenv('STEAM_ITEMS_APP_ID')):
        create_steam_db_tables(db_engine)

        app_id = int(os.getenv('STEAM_ITEMS_APP_ID'))
        num_items = int(os.getenv('STEAM_ITEMS_NUM_ITEMS'))
        max_fails = int(os.getenv('STEAM_ITEMS_MAX_FAILS', '9'))

        steam_listing_jobs = []

        for i in range(math.ceil(num_items / 100)):
            # Partial function which returns the data for a single page of listings
            data_part = partial(
                get_listings_page,
                app_id=app_id,
                count=100,
                start=i * 100
            )

            # Partial function which wraps the data_partial in a data_update call
            update_partial = create_update_partial(
                db_engine,
                service_name='Steam',
                title=f'{app_id} Listings ({i * 100}-{(i + 1) * 100})',
                data_partial=data_part,
                max_fails=max_fails
            )

            steam_listing_jobs.append(RepeatableJob(
                cooldown=3,
                partial=update_partial
            ))

        sched.add_job_group(steam_listing_jobs, group_delay=4)

    while True:
        job = sched.next_job()
        t = threading.Thread(target=job.execute)
        t.run()


if __name__ == '__main__':
    try:
        main()
    except:
        logger.exception(
            'Unhandled exception, application exiting...', exc_info=True)
        sys.exit(1)
