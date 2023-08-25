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
    Defines a repeatable job with a delay before repeating. The caller needs to make sure that the
    job is not executed until {delay_tm} seconds after the last execution 
    """

    def __init__(self, delay_tm, func, *func_args, **func_kwargs):
        """
          delay_tm:       minimum number of seconds the completion of a previous execution and the start of a new one
          func:           the function to be executed when the job is executed
          *func_args:     arguements passed to func
          **func_kwargs:  keyword arguments passed to func
        """
        # Create function with arguments already supplied
        self._func = partial(func, *func_args, **func_kwargs)
        self.last_run_finish = 0
        self.delay_tm = delay_tm

    def is_available(self) -> bool:
        """
        Returns True if the previous execution finished more than {delay_tm} seconds ago, or if the job has not
        previously been executed. 
        """
        return time.time() >= self.last_run_finish + self.delay_tm

    def execute(self, err_cb=None):
        if not self.is_available():
            raise JobExecuteBeforeDelay(
                f'last_run_finish={self.last_run_finish}, delay_tm={self.delay_tm}, current_tm={time.time()}')
        try:
            self._func()
        except Exception as e:
            # Either handle the error with a callback, or by default just log.
            if err_cb == None:
                logging.info(
                    f'Failed to execute job, continuing as normal. Error: {str(e)}', exc_info=True)
            else:
                err_cb(e)
        self.last_run_finish = time.time()
