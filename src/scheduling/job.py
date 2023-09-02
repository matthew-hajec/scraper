import time
import logging
from functools import partial

# <logging-setup>
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# </logging-setup>


class JobExecuteBeforeDelay(Exception):
    """Exception thrown when a job is executed before the delay time is over."""
    pass


class RepeatableJob:
    """
    Defines a repeating job with a delay before repeating. The caller needs to make sure that the
    job is not executed until {cooldown} seconds after the last execution 
    """

    def __init__(self, cooldown, partial):
        """
          cooldown:       minimum number of seconds the completion of a previous execution and the start of a new one
          partial:        partial to be executed
        """
        self.cooldown = cooldown
        self.partial = partial
        self.last_run_finish = 0

    def is_available(self) -> bool:
        """
        Returns True if the previous execution finished more than {cooldown} seconds ago, or if the job has not
        previously been executed. 
        """
        available = time.time() >= self.last_run_finish + self.cooldown
        logger.debug(
            f'time: {time.time()} last_run: {self.last_run_finish} delay: {self.cooldown} available: {available}')
        return time.time() >= self.last_run_finish + self.cooldown

    def execute(self):
        if not self.is_available():
            raise JobExecuteBeforeDelay(
                f'last_run_finish={self.last_run_finish}, cooldown={self.cooldown}, current_tm={time.time()}')
        try:
            self.partial()
        except Exception as e:
            logging.info(
                f'Job produced an exception that was not caught within it\'s function, continuing as normal, but logging. Error: {str(e)}', exc_info=True)

        self.last_run_finish = time.time()
