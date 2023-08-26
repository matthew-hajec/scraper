import os
import time
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


def data_update(db_engine, title, data_func, *data_args, **data_kwargs):
    logger.info(f'Updating Data: {title}')

    start = time.perf_counter()

    steam_create_db_tables(db_engine)

    try:
        items = data_func(*data_args, **data_kwargs)
    except Exception as e:
        logger.error(
            f'Exception raised while trying to retreive data: {str(e)}')
        return

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

    rust_item_jobs = []
    for i in range(37):
        start = i * 100
        rust_item_jobs.append(RepeatableJob(
            delay_tm=3,
            func=data_update,
            db_engine=db_engine,
            title='Steam - Rust Market Listings',
            data_func=get_listings_page,
            app_id=252490,
            start=start,
            count=100
        ))

    rust_item_jobs2 = []
    for i in range(37):
        start = i * 100
        rust_item_jobs2.append(RepeatableJob(
            delay_tm=3,
            func=data_update,
            db_engine=db_engine,
            title='Steam - Rust Market Listings',
            data_func=get_listings_page,
            app_id=252490,
            start=start,
            count=100
        ))

    # rust_items_job = RepeatableJob(
    #     3, data_update, db_engine, 'Steam - Rust Market Listings', get_all_app_listings, 252490, max_failures=8)

    # sched = DelayRespectingScheduler([rust_items_job])
    sched = GroupedDelayScheduler()
    sched.add_job_group(rust_item_jobs, group_delay=2)
    sched.add_job_group(rust_item_jobs, group_delay=6)

    while True:
        job = sched.next_job()
        t = threading.Thread(target=job.execute)
        t.run()


#     data_update(db_engine, 'Steam - Rust Market Listings', get_all_app_listings, 252490, count=COUNT,
#                 max_failures=MAX_FAILS, use_scrapeops=USE_SCRAPEOPS)
# #    pull_steam_listings(db_engine, 252490)
s
