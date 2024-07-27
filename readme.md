# Steam Market Item Scraper.


## Configuration

### Non-Secret

For non-secret information, a simple "ini" file is used containing configuration for the whole
application. 

The application will attempt to load a configuration file from serveral locations. The application
will use the first configuration file it finds, searching in the following locations (in order):

1. The value of the "SCRAPER_CONFIG" environment variable
2. /scraper_config 

### Secret

For secret information, 

## Howto:

There are few environmental variables that this application will accept, they are:

* DATABASE_URL (str, default='sqlite:///:memory:'):  Database URL to store records
* LOG_FILE     (str, default=None (log to console)): Log filenamme, to persist logs in docker make sure this is in a volume.
* CONFIG_FILE  (str, default=None):                  Config ini filepath




### Built-in Scrapers

Each scraper slowly pulls information from it's source, and there can only
ever be a single active instance of any single source. However, by having one machine manage plenty of sources, we 
can keep the IO busy (aka, have a high volume of data dripping in) while not overloading sites.

To enable, simply set the required properties for a source.

#### Steam Items

Set config variables 

* STEAM_GROUP_DELAY     (int): the group delay for visiting steam, this property is the same for all steam sources
* STEAM_ITEMS_APP_ID    (int): app id for the items you want to scrape
* STEAM_ITEMS_NUM_ITEMS (int): number of items to fetch
* STEAM_ITEMS_MAX_FAILS (int): maximum number of times a request to the steam API can fail before exitting (default=9)

### Yahoo Finance Currencies

Set ENV Variable:

* YAHOOFINANCE_CURRENCY (any): runs the yahoo finance currency scraper if set to any value


- Please don't use this without permission -
- https://news.bloomberglaw.com/litigation/ryanair-wins-jury-verdict-in-scraping-case-against-booking-com
