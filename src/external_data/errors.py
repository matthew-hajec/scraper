class MalformedContent(Exception):
    """Exception raised when a request is successful but did not return what was expected"""
    pass


class ExceededMaxFailures(Exception):
    """Exception raised when an external data source fails too many times."""
    pass
