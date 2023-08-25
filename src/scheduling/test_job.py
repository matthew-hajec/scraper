import pytest
import time
from job import RepeatableJob, JobExecuteBeforeDelay


def test_runs_job():
    """
    Test that the function provided runs with the arguements provided by
    modifying an existing dict within the job and then seeing if the dict
    was updated (meaning the function ran).
    """
    state = {'num': 1}

    j = RepeatableJob(1, state.__setitem__, 'num', 2)
    j.execute()
    assert state['num'] == 2


def test_raises_for_delay():
    """
    Test that the job will raise an JobExecuteBeforeDelay error if tried to call before the delay is 
    finished
    """
    j = RepeatableJob(100, print, 'hello')
    j.execute()
    with pytest.raises(JobExecuteBeforeDelay):
        j.execute()


def test_updates_last_run_finish():
    error = 0.5  # Seconds for error

    j = RepeatableJob(2, print, 'hello')
    j.execute()
    now = time.time()
    assert (now - error) <= j.last_run_finish <= (now + error)

    time.sleep(2)
    j.execute()
    now = time.time()
    assert (now - error) <= j.last_run_finish <= (now + error)
