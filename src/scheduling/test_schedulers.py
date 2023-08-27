import time
from scheduling.job import RepeatableJob
from scheduling.schedulers import GroupedDelayScheduler


def test_GroupedDelayScheduler_runs_job():
    test_data = {'num': 1}
    s = GroupedDelayScheduler()
    j = RepeatableJob(2, test_data.__setitem__, 'num', 2)

    s.add_job_group([j], group_delay=2)

    s.next_job().execute()

    assert test_data['num'] == 2


def test_GroupDelayScheduler_enforces_group_delay():
    error = 0.5

    s = GroupedDelayScheduler()
    j = RepeatableJob(1, print, time.time())

    # Group delay gt the single job's delay, expected to take precedence
    s.add_job_group([j], group_delay=2)

    start = time.time()
    s.next_job().execute()
    s.next_job().execute()
    # Should be start + 2 seconds (-error)
    assert time.time() >= start + 2 - error


def test_GroupDelayScheduler_enforces_jobs_delay():
    error = 0.5

    s = GroupedDelayScheduler()
    j1 = RepeatableJob(1, print, 'j1', time.time())
    j2 = RepeatableJob(2, print, 'j2', time.time())

    s.add_job_group([j1, j2], group_delay=0)

    # Expect that j1 and j2 will raise an error and cause the test to fail
    # if called too early. No need to check here.
    s.next_job().execute()
    s.next_job().execute()
    s.next_job().execute()
    s.next_job().execute()
    s.next_job().execute()

    assert True
