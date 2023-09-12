import os
import sys
import threading
import logging
from schema import Schema, Use
from dotenv import load_dotenv
from scheduling.schedulers import GroupedDelayScheduler
from models import load_tables as init_main_db_tables
from utils.db import init_engine
from config.config import Config

from logs import init_logger
from external_data.steam.models import load_tables as init_steam_db_tables
from external_data.steam.api import create_steam_jobs
from external_data.yahoofinance.models import load_tables as init_yahoofinance_db_tables
from external_data.yahoofinance.api import create_currency_jobs

# Read the .env file
load_dotenv()

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
    db_engine = init_engine()
    logger.info(f"Running with database dialect: {db_engine.dialect.name}")

    # Initialize the main database tables if they do not exist
    init_main_db_tables(db_engine)

    # Create the scheduler
    sched = GroupedDelayScheduler()

    # Add the jobs to the scheduler...
    # if config["YahooFinance.Currency"]["enabled"].lower() == "true":
    #     init_yahoofinance_db_tables(db_engine)

    #     sched.add_job_group(
    #         create_currency_jobs(db_engine, config["YahooFinance.Currency"]),
    #         group_delay=int(config["YahooFinance"]["groupDelay"]),
    #     )

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
        if config_file is None and os.path.isfile("/scraper_config.ini"):
            config_file = "/scraper_config.ini"

        root_config_schema = Schema(
            {
                "Logging": {"level": str, "file": str},
                "Steam": {"groupdelay": Use(int)},
                "Steam.ItemListings": {
                    "enabled": Use(bool),
                    "appid": Use(int),
                    "numitems": Use(int),
                    "maxfailures": Use(int),
                    "overloaddelay": Use(int),
                },
            }
        )

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
