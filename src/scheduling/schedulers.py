import abc
import time
import logging
from dataclasses import dataclass
from scheduling.job import RepeatableJob

logger = logging.getLogger(__name__)


class Scheduler(abc.ABC):
    """Schedulers must simply define a next_job method."""

    @abc.abstractmethod
    def next_job(self) -> RepeatableJob:
        pass


@dataclass
class _JobGroup:
    jobs: list
    job_offset: int
    last_job_start: int  # Time the last job was requested...
    delay: int

    def is_available(self) -> bool:
        return time.time() >= self.last_job_start + self.delay

    def next_job(self) -> RepeatableJob:
        if len(self.jobs) == 0:
            raise ValueError("Job list cannt be empty")

        self.last_job = time.time()
        logger.debug(
            f"Scheduling next job... (job_offset={self.job_offset}, job_count={len(self.jobs)})"
        )

        num_jobs = len(self.jobs)
        job = self.jobs[(self.job_offset) % num_jobs]
        self.job_offset += 1
        self.last_job_start = time.time()
        return job


class GroupedDelayScheduler(Scheduler):
    """
    Provides the ability to group RepeatableJobs into groups with
    individual delay times.

    This is useful for organizing the timing of jobs which make
    requests to external resources in order to prevent overloading.

    First, the scheduler will search linearly for a group which is
    not on cooldown, then it will search linearly within that group
    for a job which is not on cooldown.

    Searches for groups and jobs start at an offset. This means that
    when performing linear search for a group, the search will start
    from the offset value. In turn, each of these group also has an
    offset it uses to select jobs. The group selection offset
    increments whenever a group is selected, and the job selection
    offset increments whenever a job is selected from a group.
    """

    _groups: list[_JobGroup]
    _group_offset: int

    def __init__(self):
        self._groups = []
        self._group_offset = 0

    def add_job_group(self, jobs: list[RepeatableJob], group_delay=2):
        self._groups.append(_JobGroup(jobs, 0, 0, group_delay))

    def _next_group(self) -> _JobGroup:
        num_groups = len(self._groups)

        if num_groups == 0:
            raise ValueError("No job groups added to scheduler.")

        for i in range(num_groups):
            group_idx = (i + self._group_offset) % num_groups
            group = self._groups[(i + self._group_offset) % num_groups]

            if not group.is_available():
                continue

            logger.debug(f"Selected group idx: {group_idx}")
            return group
        time.sleep(0.1)
        return self._next_group()

    def next_job(self) -> RepeatableJob:
        logger.debug(
            f"Scheduling next group... (group_offset={self._group_offset}, group_count={len(self._groups)})"
        )

        group = self._next_group()
        return group.next_job()
