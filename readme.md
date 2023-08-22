# Steam Market Item Scraper.

## Howto:

There are few environmental variables that this application will accept, they are:

* MAX_FAILS (int, default=9): Maximum number of times a request to the steam API can fail before exitting
* DATABASE_URL (str, default='sqlite:///:memory:'): Database URL to store records