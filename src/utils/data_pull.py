import logging
import time
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


def data_update(db_engine, title, data_func, max_failures=5, *data_args, **data_kwargs):
    logger.info(f'Updating Data: {title}')

    start = time.perf_counter()

    failures = 0
    while True:
        if failures >= max_failures:
            logging.info(
                f'Max failures acheived ({failures}/{max_failures}). Exiting update.')
            return

        if failures > 0:
            # 5, 25, 45, 65, ... Sometimes, sending a request immediately after works fine, but if it doesn't, add a more significant amount of time
            sleep_time = 5 + (20 * (failures - 1))
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

    logger.info(f'Data update ({title}) took {time.perf_counter() - start}')
