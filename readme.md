# Steam Market Item Scraper.

## Howto:

There are few environmental variables that this application will accept, they are:

* DATABASE_URL (str, default='sqlite:///:memory:'):  Database URL to store records
* LOG_FILE     (str, default=None (log to console)): Log filenamme, to persist logs in docker make sure this is in a volume.

### Built-in Scrapers

There are a bunch of built in scrapers. Each scraper slowly pulls information from it's source, and there can only
ever be a single active instance of any single source. However, by having one machine manage plenty of sources, we 
can keep the IO busy (aka, have a high volume of data dripping in) while not overloading sites.

To enable, simply set the required properties for a source.

#### Steam Items

Set ENV Variables:

* STEAM_GROUP_DELAY     (int): the group delay for visiting steam, this property is the same for all steam sources
* STEAM_ITEMS_APP_ID    (int): app id for the items you want to scrape
* STEAM_ITEMS_NUM_ITEMS (int): number of items to fetch
* STEAM_ITEMS_MAX_FAILS (int): maximum number of times a request to the steam API can fail before exitting (default=9)

### Yahoo Finance Currencies

Set ENV Variable:

* YAHOOFINANCE_CURRENCY (any): runs the yahoo finance currency scraper if set to any value