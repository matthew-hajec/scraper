import os
import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from external_data.steam.models import load_tables
from external_data.steam.api import get_all_app_listings


logging.basicConfig(
    level=logging.INFO,
    format='%(name)s::%(levelname)s %(asctime)s: %(message)s'
)


logger = logging.getLogger(__name__)


MAX_FAILS = int(os.getenv('MAX_FAILS', '9'))
USE_SCRAPEOPS = False
COUNT = 100


def save_steam_listings(db_engine, app_id):
    logger.info(f'Getting listings for {app_id}...')

    load_tables(db_engine)

    start = time.perf_counter()

    for item_batch in get_all_app_listings(app_id, count=COUNT, max_failures=MAX_FAILS, use_scrapeops=USE_SCRAPEOPS):
        with Session(db_engine) as session:
            session.add_all(item_batch)
            session.commit()

    logger.info(f'Rust data pull took {time.perf_counter() - start}')


if __name__ == '__main__':
    db_url = os.getenv('DATABASE_URL', 'sqlite:///:memory:')

    db_engine = create_engine(db_url)
    # db_engine = create_engine('postgresql://user:password@127.0.0.1/postgres')

    logger.info(f'Running with database dialect: {db_engine.dialect.name}')

    save_steam_listings(db_engine)
