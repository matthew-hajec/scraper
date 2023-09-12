from schema import Schema, Use

# Define the schema for the root config file
root_config_schema = Schema(
    {
        "Steam": {"groupdelay": Use(int)},
        "Steam.ItemListings": {
            "enabled": Use(bool),
            "appid": Use(int),
            "numitems": Use(int),
            "maxfailures": Use(int),
            "overloaddelay": Use(int),
        },
        "YahooFinance": {"groupdelay": Use(int)},
        "YahooFinance.Currency": {
            "enabled": Use(bool),
            "maxfailures": Use(int),
            "overloaddelay": Use(int),
        },
    }
)
