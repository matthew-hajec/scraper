import math
from enum import Enum
from urllib.parse import urlencode
import requests
import json
import logging
from external_data.steam.models import ItemRecord
from external_data.errors import MalformedContent, RateLimitException
from scheduling.job import RepeatableJob
from functools import partial
from utils.data_pull import create_update_partial


logger = logging.getLogger(__name__)

BASE_URL = "https://steamcommunity.com"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"
}


class SortColumn(Enum):
    """Enum for the field to sort results on"""

    NAME = "name"
    QTY = "quantity"
    PRICE = "price"


class SortDir(Enum):
    """Enum for the sort direction of the results"""

    ASC = "asc"
    DESC = "desc"


def create_steam_jobs(db_engine, config) -> list[RepeatableJob]:
    if "appid" not in config:
        raise ValueError('Config must contain an "appid" field.')
    if "numitems" not in config:
        raise ValueError('Config must contain an "numitems" field.')

    app_id = int(config["appid"])
    num_items = int(config["numitems"])
    max_fails = int(config["maxfailures"])

    jobs = []

    for i in range(math.ceil(num_items / 100)):
        data_part = partial(
            get_listings_page, config, app_id=app_id, count=100, start=i * 100
        )

        update_part = create_update_partial(
            db_engine,
            service_name="Steam",
            title=f"{app_id} Item Listings ({i * 100}-{(i + 1) * 100})",
            data_partial=data_part,
            max_fails=max_fails,
        )

        jobs.append(RepeatableJob(partial=update_part))

    return jobs


def get_listings_page(
    config,
    app_id: int,
    start=0,
    count=100,
    sort_col=SortColumn.NAME,
    sort_dir=SortDir.ASC,
    use_scrapeops=False,
    headers=DEFAULT_HEADERS,
    **req_kwargs,
) -> (int, list[ItemRecord]):
    query_str = urlencode(
        {
            "query": "",
            "start": start,
            "count": count,
            "search_descriptions": 0,
            "sort_column": sort_col.value,
            "sort_dir": sort_dir.value,
            "appid": app_id,
            "norender": 1,
        }
    )

    url = f"{BASE_URL}/market/search/render?{query_str}"

    resp = requests.get(url, headers=headers)

    if resp.status_code == 429:
        # 120 is a somewhat arbitrary constant. It could be worth it to read this from  an environmental variable.
        wait_for = float(config["overloadsleeptime"].replace(",", ""))
        raise RateLimitException(
            wait_for,
            f"Rate limit exceeded for {url}. Wait {wait_for} seconds before trying again.",
        )
    elif resp.status_code != 200:
        resp.raise_for_status()

    data = json.loads(resp.text)

    # Response must contain these fields:
    if "results" not in data:
        raise MalformedContent('"results" not found')
    if "total_count" not in data:
        raise MalformedContent('"total_count" not found')
    if not isinstance(data["results"], list):
        raise MalformedContent('"results" is not a list')
    if len(data["results"]) == 0:
        raise MalformedContent('"results" contained no elements')

    all_records = []
    for result in data["results"]:
        all_records.append(
            ItemRecord(
                item_url="",
                name=result["name"],
                hash_name=result["hash_name"],
                sell_listings=result["sell_listings"],
                sell_price=result["sell_price"],
                sale_price_text=result["sale_price_text"],
            )
        )

    return all_records
