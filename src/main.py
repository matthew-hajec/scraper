import os
import time
import sys
import threading
import logging
from scheduling.schedulers import GroupedDelayScheduler
from models import load_tables as init_main_db_tables
from utils.db import init_engine
from config.config import Config
from root_conf_schema import root_config_schema

from data_sources.steam.models import load_tables as init_steam_db_tables
from data_sources.steam.api import create_steam_jobs
from data_sources.yahoofinance.models import load_tables as init_yahoofinance_db_tables
from data_sources.yahoofinance.api import create_currency_jobs

# Initialize the logger
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=os.getenv("LOG_FILE", None),
)
logger = logging.getLogger(__name__)


def main(config: Config):
    logger.info("Starting application")

    # Create the database engine
    db_engine = None

    # Handle transient database connection errors
    for i in range(5):
        try:
            db_engine = init_engine()
            db_engine.connect()
            break
        except:
            logger.warning(f"Failed to connect to database. Retrying... ({i}/5)")
            time.sleep(5)
            continue

    if db_engine is None:
        logger.critical("Failed to connect to database. Exiting...")
        sys.exit(1)

    logger.info(f"Running with database dialect: {db_engine.dialect.name}")

    # Initialize the main database tables if they do not exist
    init_main_db_tables(db_engine)

    # Create the scheduler
    sched = GroupedDelayScheduler()

    # Add the jobs to the scheduler...
    if config["YahooFinance.Currency"]["enabled"]:
        init_yahoofinance_db_tables(db_engine)

        sched.add_job_group(
            create_currency_jobs(db_engine, config["YahooFinance.Currency"]),
            group_delay=int(config["YahooFinance"]["groupdelay"]),
        )

    if config["Steam.ItemListings"]["enabled"]:
        # Initialize database tables if they do not exist
        init_steam_db_tables(db_engine)

        # Add the jobs to the scheduler
        sched.add_job_group(
            create_steam_jobs(db_engine, config["Steam.ItemListings"]),
            group_delay=int(config["Steam"]["groupdelay"]),
        )

    while True:
        job = sched.next_job()
        t = threading.Thread(target=job.execute)
        t.run()


if __name__ == "__main__":
    # Attempt to load the configuration
    try:
        # 1: Check if the config file is provided in the environment
        config_file = os.getenv("CONFIG_FILE", None)

        # 2: If not, check if /scraper_config.ini exists
        if config_file is None and os.path.isfile("/scraper_config"):
            config_file = "/scraper_config"

        config = Config(config_file, root_config_schema)
    except:
        logger.critical(f"Failed to load config file: {config_file}", exc_info=True)
        sys.exit(1)

    # Start the application
    try:
        main(config)
    except:
        logger.critical("Unhandled exception, application exiting...", exc_info=True)
        sys.exit(1)
