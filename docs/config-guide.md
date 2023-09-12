# Configuration

For non-secret information, an ini file is used containing configuration for the whole
application. This file will be validated when loaded.

The application will attempt to load a configuration file from serveral locations. The application
will use the first configuration file it finds, searching in the following locations (in order):

1. The value of the "CONFIG_FILE" environment variable
2. /scraper_config.ini

## Application Configuration Options
| SECTION | KEY       | DATATYPE                                                 | DEFAULT                  | DESCRIPTION                                                       | Nullable? |
|---------|-----------|----------------------------------------------------------|--------------------------|-------------------------------------------------------------------|-----------|
| Logging | Level | "NOTSET", "DEBUG", "INFO",   "WARN", "ERROR", "CRITICAL" | INFO                     | Default logging level (may be overridden by source configs)       | NO        |
| Logging | File  | string                                                   | /var/log/scraper/app.log | Filepath of log file. If not set, the application logs to console | YES       |

## Scraper Configuration Options

Each scraper will have it's own configuration options