from job import RepeatableJob
from schedulers import GroupedDelayScheduler


def test_GroupedDelayScheduler_runs_job():
    test_data = {'num': 1}
    s = GroupedDelayScheduler()
    j = RepeatableJob(2, test_data.__setitem__, 'num', 2)

    s.add_job_group([j], group_delay=2)

    s.next_job().execute()

    assert test_data['num'] == 2
