import requests
import logging
from bs4 import BeautifulSoup
from external_data.yahoofinance.models import CurrencyRecord
from external_data.errors import MalformedContent, RateLimitException
from scheduling.job import RepeatableJob
from functools import partial
from utils.data_pull import create_update_partial


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

BASE_URL = 'https://finance.yahoo.com/currencies'

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0'
}


def create_currency_jobs(db_engine, config) -> list[RepeatableJob]:
    jobs = []

    max_fails = int(config['MaxFailures'])

    data_part = partial(
        get_currency_page,
        headers=DEFAULT_HEADERS
    )

    update_part = create_update_partial(
        db_engine,
        service_name='Yahoo Finance',
        title='Currencies',
        data_partial=data_part,
        max_fails=max_fails
    )

    jobs.append(RepeatableJob(
        partial=update_part
    ))

    return jobs


def get_currency_page(headers=DEFAULT_HEADERS):
    url = f'{BASE_URL}/currencies'

    resp = requests.get(BASE_URL, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')

    names = soup.find_all('td', attrs={'aria-label': 'Name'})
    prices = soup.find_all('td', attrs={'aria-label': 'Last Price'})

    logger.debug(f'Found {len(names)} names and {len(prices)} prices.')

    if len(names) != len(prices):
        raise MalformedContent(
            f'Number of names ({len(names)}) does not match number of prices ({len(prices)}).')

    all_records = []
    for result in zip(names, prices):
        name = result[0].text
        price = result[1].text

        record = CurrencyRecord(name=name, last_price=price)
        all_records.append(record)

    return all_records