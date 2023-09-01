class MalformedContent(Exception):
    """Exception raised when a request is successful but did not return what was expected"""
    pass


class RateLimitException(Exception):
    def __init__(self, wait_for, message):
        self.wait_for = wait_for
        self.message = message
    """Exception raised when a request is rate limited"""
    pass
