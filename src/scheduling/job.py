import logging

logger = logging.getLogger(__name__)


class RepeatableJob:
    """
    Just contains a partial function
    """

    def __init__(self, partial):
        """
          partial:        partial to be executed
        """
        self.partial = partial

    def execute(self):
        try:
            self.partial()
        except Exception as e:
            logging.info(
                f'Job produced an exception that was not caught within it\'s function, continuing as normal, but logging. Error: {str(e)}', exc_info=True)
