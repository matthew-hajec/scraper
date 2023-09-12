import time
from scheduling.job import RepeatableJob
from scheduling.schedulers import GroupedDelayScheduler
from functools import partial


def test_GroupedDelayScheduler_runs_job():
    test_data = {"num": 1}
    s = GroupedDelayScheduler()
    p = partial(test_data.__setitem__, "num", 2)
    j = RepeatableJob(p)

    s.add_job_group([j], group_delay=2)

    s.next_job().execute()

    assert test_data["num"] == 2


def test_GroupDelayScheduler_enforces_group_delay():
    error = 0.5

    s = GroupedDelayScheduler()
    p = partial(print, "hello")
    j = RepeatableJob(p)

    # Group delay gt the single job's delay, expected to take precedence
    s.add_job_group([j], group_delay=2)

    start = time.time()
    s.next_job().execute()
    s.next_job().execute()
    # Should be start + 2 seconds (-error)
    assert time.time() >= start + 2 - error


def test_GroupDelayScheduler_rotates_groups():
    group1_state = {"key": 10}
    group2_state = {"key": 20}

    s = GroupedDelayScheduler()
    p1 = partial(group1_state.__setitem__, "key", 11)
    j1 = RepeatableJob(p1)
    p2 = partial(group2_state.__setitem__, "key", 21)
    j2 = RepeatableJob(p2)
    group1 = [j1]
    group2 = [j2]
    s.add_job_group(group1, group_delay=2)
    s.add_job_group(group2, group_delay=2)

    s.next_job().execute()
    s.next_job().execute()

    assert group1_state["key"] == 11
    assert group2_state["key"] == 21


def test_GroupScheduler_respects_group_delay():
    error = 0.5

    s = GroupedDelayScheduler()

    p = partial(print, "hello")

    group1 = [RepeatableJob(p), RepeatableJob(p)]

    group2 = [RepeatableJob(p), RepeatableJob(p)]

    s.add_job_group(group1, group_delay=5)
    s.add_job_group(group2, group_delay=5)

    start = time.time()
    s.next_job().execute()
    s.next_job().execute()
    s.next_job().execute()
    s.next_job().execute()

    assert time.time() >= start + 5 - error
