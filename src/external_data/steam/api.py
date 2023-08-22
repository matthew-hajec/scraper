from enum import Enum
from urllib.parse import urlencode
from time import sleep
import json
import logging
import requests
from lib.http import make_request
from external_data.steam.models import ItemRecord
from external_data.steam.constants import BASE_URL, DEFAULT_HEADERS


logger = logging.getLogger(__name__)


class MalformedContent(Exception):
    """Exception raised when a request is successful but did not return what was expected"""
    pass


class SortColumn(Enum):
    """Enum for the field to sort results on"""
    NAME = 'name'
    QTY = 'quantity'
    PRICE = 'price'


class SortDir(Enum):
    """Enum for the sort direction of the results"""
    ASC = 'asc'
    DESC = 'desc'


def get_listings_page(app_id: int, start=0, count=100,
                      sort_col=SortColumn.NAME, sort_dir=SortDir.ASC,
                      use_scrapeops=False, **req_kwargs) -> (int, list[ItemRecord]):

    query_str = urlencode({
        'query': '',
        'start': start,
        'count': count,
        'search_descriptions': 0,
        'sort_column': sort_col.value,
        'sort_dir': sort_dir.value,
        'appid': app_id,
        'norender': 1
    })

    url = f'{BASE_URL}/market/search/render?{query_str}'

    resp = make_request('GET', url, use_scrapeops=use_scrapeops, **req_kwargs)
    # Raise an error if the response's status code indicates an error
    resp.raise_for_status()

    data = json.loads(resp.text)

    # Response must contain these fields:
    if 'results' not in data:
        raise MalformedContent('"results" not found')
    if 'total_count' not in data:
        raise MalformedContent('"total_count" not found')
    if not isinstance(data['results'], list):
        raise MalformedContent('"results" is not a list')
    if len(data['results']) == 0:
        raise MalformedContent('"results" contained no elements')

    all_items = []
    for result in data['results']:
        all_items.append(ItemRecord(
            item_url="",
            name=result['name'],
            hash_name=result['hash_name'],
            sell_listings=result['sell_listings'],
            sell_price=result['sell_price'],
            sale_price_text=result['sale_price_text'],
        ))

    return data['total_count'], all_items


def get_all_app_listings(app_id, count=100, sort_col=SortColumn.NAME, sort_dir=SortDir.ASC, max_failures=5, default_sleep=2, use_scrapeops=False, **req_kwargs):
    """
    Scrapes all market listings for a certain app_id. Upon recieving
    a successful response this function will yield a list containing 
    all of the items returned by the steam API.
    """

    # For generating logs which include the parameters.
    params_debug_str = f'(app_id={app_id} count={count}, sort_col={sort_col.value}, sort_dir={sort_dir.value}, use_scrapeops={use_scrapeops})'

    logger.debug(
        f'Getting all app listings for {params_debug_str}')

    """Returns all listings for an application"""
    scraped_count = 0

    failures = 0  # Stores the number of CONSECUTIVE failures, reset to zero upon a successful request
    while True:
        if failures == max_failures:
            logger.error(
                f'Failed too many times ({failures}/{max_failures}) while trying to get items {params_debug_str}')
            break
        elif failures > 0:
            sleep_tm = pow(2, failures)  # 2^failures
            logger.info(
                f'Due to failure ({failures}/{max_failures}), sleeping for {sleep_tm} seconds before the next request)')
            sleep(pow(2, failures))
        else:
            sleep(default_sleep)  # Default sleep time if there are no errors

        try:
            # Attempt to fetch results from the listings page
            total_count, listings = get_listings_page(
                app_id, scraped_count, count, sort_col, sort_dir, use_scrapeops, **req_kwargs)

            # Increment scraped count
            scraped_count += len(listings)

            # Yield the listings
            yield listings

            failures = 0  # Reset Failures

            logger.info(f'Retrieved {scraped_count}/{total_count}')
        except MalformedContent as e:
            failures += 1

            logger.info(
                f'Malformed content received {params_debug_str} Error Message: {str(e)}')
            continue
        except requests.exceptions.HTTPError as e:
            failures += 1

            if e.response.status_code == 429:
                pass

            logger.info(
                f'HTTP Error {params_debug_str} Error Message: {str(e)}')
            continue

        if scraped_count >= total_count:
            logger.info(
                f'Retreived all items for app_id {app_id} ({scraped_count} items)')
            break
