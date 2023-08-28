import logging
import json
from utils.http import make_request
from external_data.amazon.constants import BASE_URL, DEFAULT_HEADERS

logger = logging.getLogger(__name__)


def get_listing_info(item_path: str, headers=DEFAULT_HEADERS, **req_kwargs):
    url = f'{BASE_URL}{item_path}'
    logger.info(f'Getting listing info for {url}')

    resp = make_request('GET', url, headers=DEFAULT_HEADERS, **req_kwargs)

    with open('test.html', 'w', encoding='utf-8') as f:
        f.write(resp.text)

    resp.raise_for_status()
