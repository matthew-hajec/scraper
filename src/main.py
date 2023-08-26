import os
import time
import math
import logging
import threading
from scheduling.job import RepeatableJob
from scheduling.schedulers import GroupedDelayScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from external_data.steam.models import load_tables as steam_create_db_tables
from external_data.steam.api import get_listings_page


logging.basicConfig(
    level=logging.INFO,
    format='%(name)s::%(levelname)s %(asctime)s: %(message)s'
)


logger = logging.getLogger(__name__)


def data_update(db_engine, title, data_func, max_failures=5, *data_args, **data_kwargs):
    logger.info(f'Updating Data: {title}')

    start = time.perf_counter()

    steam_create_db_tables(db_engine)

    failures = 0
    while True:
        if failures >= max_failures:
            logging.info(
                f'Max failures acheived ({failures}/{max_failures}). Exiting update.')
            return

        if failures > 0:
            # 3, 23, 43, 63, ... Sometimes, sending a request immediately after works fine, but if it doesn't, add a more significant amount of time
            sleep_time = 3 + (20 * (failures - 1))
            logger.info(
                f'Failed ({failures}/{max_failures}), sleeping for {sleep_time} seconds')
            time.sleep(sleep_time)

        try:
            items = data_func(*data_args, **data_kwargs)
            break
        except Exception as e:
            logger.info(
                f'Exception raised while trying to retreive data: {str(e)}')
            failures += 1

    if not hasattr(items, '__iter__') and not hasattr(items, '__next__'):
        raise TypeError('data_func should return an iterable.')

    for item in items:
        with Session(db_engine) as session:
            session.add(item)
            session.commit()

    logger.info(f'Rust data pull took {time.perf_counter() - start}')


if __name__ == '__main__':
    db_url = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
    db_engine = create_engine(db_url)
    logger.info(f'Running with database dialect: {db_engine.dialect.name}')

    sched = GroupedDelayScheduler()

    if (os.getenv('STEAM_ITEMS_APP_ID')):
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
