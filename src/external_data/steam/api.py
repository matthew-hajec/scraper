from enum import Enum
from urllib.parse import urlencode
import time
import json
import logging
import requests
from utils.http import make_request
from external_data.steam.models import ItemRecord
from external_data.steam.constants import BASE_URL, DEFAULT_HEADERS
from external_data.errors import MalformedContent, ExceededMaxFailures


logger = logging.getLogger(__name__)


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

    return all_items
