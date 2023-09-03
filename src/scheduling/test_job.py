from scheduling.job import RepeatableJob
from functools import partial


def test_runs_job():
    """
    Test that the function provided runs with the arguements provided by
    modifying an existing dict within the job and then seeing if the dict
    was updated (meaning the function ran).
    """
    state = {'num': 1}

    p = partial(state.__setitem__, 'num', 2)

    j = RepeatableJob(p)
    j.execute()
    assert state['num'] == 2
