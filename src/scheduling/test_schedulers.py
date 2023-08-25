import time
from job import RepeatableJob
from schedulers import DelayRespectingScheduler


def test_runs_one_job():
    data = {'key': 1}

    j = RepeatableJob(1, data.__setitem__, 'key', 2)
    s = DelayRespectingScheduler([j])

    s.next_job().execute()

    assert data['key'] == 2


def test_runs_initial_jobs_immediately():
    time_error = 0.25  # Maximum error in seconds the time can have from expected

    j1 = RepeatableJob(1, print, 'hello world')
    j2 = RepeatableJob(1, print, 'hello pytest')
    s = DelayRespectingScheduler([j1, j2])

    before = time.time()
    s.next_job()
    s.next_job()
    dur = time.time() - before

    assert dur <= 0 + time_error


def test_waits_before_repeat():
    time_error = 0.25  # Maximum error in seconds the time can have from expected
    wait_time = 1.25

    j1 = RepeatableJob(wait_time, print, 'hello world')
    j2 = RepeatableJob(wait_time, print, 'hello pytest')
    s = DelayRespectingScheduler([j1, j2])

    before = time.time()
    s.next_job().execute()  # Executes j1 immediately
    s.next_job().execute()  # Executes j2 immediately
    dur = time.time() - before
    assert dur <= 0 + time_error

    s.next_job().execute()  # Executes j1 after delay (1s)
    s.next_job().execute()  # Executes j2 after delay (1s)
    dur = time.time() - before
    assert dur >= wait_time
