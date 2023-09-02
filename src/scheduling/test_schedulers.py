import time
from scheduling.job import RepeatableJob
from scheduling.schedulers import GroupedDelayScheduler
from functools import partial


def test_GroupedDelayScheduler_runs_job():
    test_data = {'num': 1}
    s = GroupedDelayScheduler()
    p = partial(test_data.__setitem__, 'num', 2)
    j = RepeatableJob(2, p)

    s.add_job_group([j], group_delay=2)

    s.next_job().execute()

    assert test_data['num'] == 2


def test_GroupDelayScheduler_enforces_group_delay():
    error = 0.5

    s = GroupedDelayScheduler()
    p = partial(print, 'hello')
    j = RepeatableJob(1, p)

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
    p1 = partial(print, 'hello 1')
    j1 = RepeatableJob(1, p1)
    p2 = partial(print, 'hello 2')
    j2 = RepeatableJob(2, p2)

    s.add_job_group([j1, j2], group_delay=0)

    # Expect that j1 and j2 will raise an error and cause the test to fail
    # if called too early. No need to check here.
    s.next_job().execute()
    s.next_job().execute()
    s.next_job().execute()
    s.next_job().execute()
    s.next_job().execute()

    assert True


def test_GroupDelayScheduler_rotates_groups():
    group1_state = {'key': 10}
    group2_state = {'key': 20}

    s = GroupedDelayScheduler()
    p1 = partial(group1_state.__setitem__, 'key', 11)
    j1 = RepeatableJob(1, p1)
    p2 = partial(group2_state.__setitem__, 'key', 21)
    j2 = RepeatableJob(1, p2)
    group1 = [j1]
    group2 = [j2]
    s.add_job_group(group1, group_delay=2)
    s.add_job_group(group2, group_delay=2)

    s.next_job().execute()
    s.next_job().execute()

    assert group1_state['key'] == 11
    assert group2_state['key'] == 21


# def test_GroupDelayScheduler_rotates_groups_even_if_jobs_available():
#     s = GroupedDelayScheduler()

#     group1 = [RepeatableJob(1, print, 'group 1, job 1'),
#               RepeatableJob(1, print, 'group 1, job 2')]

#     group2 = [RepeatableJob(1, print, 'group 2, job 1'),
#               RepeatableJob(1, print, 'group 2, job 2')]

#     s.add_job_group(group1, group_delay=2)
#     s.add_job_group(group2, group_delay=2)

#     s.next_job().execute()
#     s.next_job().execute()
#     s.next_job().execute()
#     s.next_job().execute()

#     raise ValueError()


def test_GroupScheduler_respects_group_delay():
    error = 0.5

    s = GroupedDelayScheduler()

    p = partial(print, 'hello')

    group1 = [RepeatableJob(5, p),
              RepeatableJob(5, p)]

    group2 = [RepeatableJob(1, p),
              RepeatableJob(1, p)]

    s.add_job_group(group1, group_delay=5)
    s.add_job_group(group2, group_delay=5)

    start = time.time()
    s.next_job().execute()
    s.next_job().execute()
    s.next_job().execute()
    s.next_job().execute()

    assert time.time() >= start + 5 - error
