from sqlalchemy import create_engine
import os


def init_engine():
    database_url = os.getenv('DATABASE_URL')
    if database_url is None:
        raise ValueError("No database provided.")
    return create_engine(database_url)
