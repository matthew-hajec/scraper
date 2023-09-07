import os
import sys
import math
import logging
import threading
from dotenv import load_dotenv
from scheduling.schedulers import GroupedDelayScheduler
from models import load_tables as init_main_db_tables
from utils.db import init_engine
from config.config import create_config

from external_data.steam.models import load_tables as init_steam_db_tables
from external_data.steam.api import create_steam_jobs
from external_data.yahoofinance.models import load_tables as init_yahoofinance_db_tables
from external_data.yahoofinance.api import create_currency_jobs


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

    config = create_config(os.environ['CONFIG_FILE'])

    db_engine = init_engine()
    logger.info(f'Running with database dialect: {db_engine.dialect.name}')

    # Initialize database tables if they do not exist
    init_main_db_tables(db_engine)

    # Create the scheduler
    sched = GroupedDelayScheduler()

    print(config['YahooFinance.Currency']['Enabled'].lower())

    # Add the jobs to the scheduler...
    if config['YahooFinance.Currency']['Enabled'].lower() == 'true':
        init_yahoofinance_db_tables(db_engine)

        sched.add_job_group(create_currency_jobs(
            db_engine, config['YahooFinance.Currency']), group_delay=int(config['YahooFinance']['GroupDelay']))

    if config['Steam.ItemListings']['Enabled'].lower() == 'true':
        # Initialize database tables if they do not exist
        init_steam_db_tables(db_engine)

        # Add the jobs to the scheduler
        sched.add_job_group(create_steam_jobs(
            db_engine, config['Steam.ItemListings']), group_delay=int(config['Steam']['GroupDelay']))

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

    # if os.getenv('YAHOOFINANCE_CURRENCY'):
    #     init_yahoofinance_db_tables(db_engine)

    #     group_delay = int(os.getenv('YAHOO_GROUP_DELAY', '100'))

    #     data_part = partial(get_currency_page)

    #     update_part = create_update_partial(
    #         db_engine,
    #         service_name='Yahoo Finance',
    #         title='Currency',
    #         data_partial=data_part,
    #         max_fails=9
    #     )

    #     sched.add_job_group([
    #         RepeatableJob(partial=update_part)
    #     ], group_delay=group_delay)

        # app_id = int(config['Steam']['app_id'])
        # num_items = int(os.getenv('STEAM_ITEMS_NUM_ITEMS'))
        # max_fails = int(os.getenv('STEAM_ITEMS_MAX_FAILS', '9'))
        # group_delay = int(os.getenv('STEAM_GROUP_DELAY', '6'))

        # steam_listing_jobs = []

        # for i in range(math.ceil(num_items / 100)):
        #     # Partial function which returns the data for a single page of listings
        #     data_part = partial(
        #         get_listings_page,
        #         app_id=app_id,
        #         count=100,
        #         start=i * 100
        #     )

        #     # Partial function which wraps the data_partial in a data_update call
        #     update_part = create_update_partial(
        #         db_engine,
        #         service_name='Steam',
        #         title=f'{app_id} Listings ({i * 100}-{(i + 1) * 100})',
        #         data_partial=data_part,
        #         max_fails=max_fails
        #     )

        #     steam_listing_jobs.append(RepeatableJob(
        #         partial=update_part
        #     ))

        # sched.add_job_group(steam_listing_jobs, group_delay=group_delay)
