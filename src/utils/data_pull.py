import logging
import time
from sqlalchemy.orm import Session
from external_data.errors import RateLimitException
from functools import partial
from models import DataUpdateRecord

logger = logging.getLogger(__name__)


class TooManyFailuresError(Exception):
    pass


def create_update_partial(db_engine, service_name, title, data_partial, max_fails):
    """
      Wrap a data_partial in a data_update call, and return the partial.
    """
    return partial(
        data_update,
        db_engine=db_engine,
        service_name=service_name,
        title=title,
        data_partial=data_partial,
        max_fails=max_fails
    )


# Returns a tuple of (number of attempts, list of items)
def _pull_external_data(data_partial, log_pref, max_fails) -> (int, list):
    for i in range(max_fails):
        logger.info(
            f'{log_pref} Pulling data... ({i + 1}/{max_fails})')
        try:
            return (i + 1, data_partial())
        except RateLimitException as e:
            # Rate limit exceptions should contain a wait_for field, which is the number of seconds to wait before trying again
            logger.info(
                f'{log_pref} Rate limit exceeded... Waiting {e.wait_for} seconds before trying again.')
            time.sleep(e.wait_for)
        except Exception as e:
            # 5 seconds, 15 seconds, 25 seconds, ....
            sleep_time = (10 * i) + 5
            logger.info(
                f'{log_pref} Exception raised while trying to retreive date (sleeping for {sleep_time}): {str(e)}')
            time.sleep(sleep_time)
            continue
    raise TooManyFailuresError()


def data_update(db_engine, service_name, title, data_partial, max_fails):
    """Calls data_partial, and then updates the database with the results. Retries up to max_fails times."""

    log_prefix = f'{service_name} -> [{title}]'  # Prefix for logging

    # Start timer for logging total time taken
    start = time.perf_counter()

    # Create a record of the data update, we will update this record with a message when the update is complete, or if it fails
    data_update_record = DataUpdateRecord(
        service_name=service_name,
        title=title
    )

    # Create a list to store the items returned by data_partial
    items = []

    try:
        n_attempts, items = _pull_external_data(
            data_partial, log_prefix, max_fails)

        # Update the data_update_record
        data_update_record.success = True
        data_update_record.attempts = n_attempts
        data_update_record.run_time = time.perf_counter() - start
    except TooManyFailuresError:
        logger.info(f'{log_prefix} Failed too many times... ({max_fails})')

        # Update the data_update_record
        data_update_record.success = False
        data_update_record.attempts = max_fails
        data_update_record.run_time = time.perf_counter() - start
        return

    # Update the database with the results
    with Session(db_engine) as session:
        session.add(data_update_record)
        session.add_all(items)
        session.commit()

    logger.info(
        f'{log_prefix} Data update took {time.perf_counter() - start}s')
