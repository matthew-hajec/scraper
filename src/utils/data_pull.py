import logging
import time
from sqlalchemy.orm import Session
from external_data.errors import RateLimitException

logger = logging.getLogger(__name__)


def data_update(db_engine, title, data_partial, max_fails):
    start = time.perf_counter()

    logger.info(
        f'[{title}] Starting data update... (max_fails={max_fails})')

    failures = 0
    while True:
        if failures >= max_fails:
            logger.info(
                f'[{title}] Max failures acheived ({failures}/{max_fails}). Exiting update.')
            return

        if failures > 0:
            # 5, 25, 45, 65, ... Sometimes, sending a request immediately after works fine, but if it doesn't, add a more significant amount of time
            sleep_time = 5 + (20 * (failures - 1))
            logger.info(
                f'[{title}] Failed ({failures}/{max_fails}), sleeping for {sleep_time} seconds')
            time.sleep(sleep_time)

        try:
            items = data_partial()
            break
        except RateLimitException as e:
            logger.info(
                f'[{title}] Rate limit exceeded... Waiting {e.wait_for} seconds before trying again.')
            time.sleep(e.wait_for)
        except Exception as e:
            logger.info(
                f'[{title}] Exception raised while trying to retreive data: {str(e)}')
            failures += 1

    if not hasattr(items, '__iter__') and not hasattr(items, '__next__'):
        raise TypeError('[{title}] data_func should return an iterable.')

    for item in items:
        with Session(db_engine) as session:
            session.add(item)
            session.commit()

    logger.info(
        f'[{title}] Data update took {time.perf_counter() - start}')
