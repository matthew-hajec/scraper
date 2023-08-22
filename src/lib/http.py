from urllib.parse import quote
import requests


def make_request(
        method: str,
        url: str,
        use_scrapeops=False,
        **req_kwargs
):
    if use_scrapeops:
        # Reform the URL
        scrape_ops_url = "https://proxy.scrapeops.io/v1?api_key=4bb16330-dbb0-4f26-b8e9-77f5635c0aec&url="
        encoded_url = quote(url)
        url = scrape_ops_url + encoded_url

    return requests.request(method, url, **req_kwargs)
