import abc
import time
import logging
from dataclasses import dataclass
from scheduling.job import RepeatableJob

# <logging-setup>
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# </logging-setup>


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
            raise ValueError('Job list cannt be empty')

        self.last_job = time.time()
        logger.debug(
            f'Scheduling next job... (job_offset={self.job_offset}, job_count={len(self.jobs)})')

        num_jobs = len(self.jobs)
        for i in range(num_jobs):
            job = self.jobs[(i + self.job_offset) % num_jobs]
            if job.is_available():
                self.job_offset += 1
                self.last_job_start = time.time()
                return job
        time.sleep(1)
        return self.next_job()


class GroupedDelayScheduler(Scheduler):
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
            raise ValueError('No job groups added to scheduler.')

        for i in range(num_groups):
            group_idx = (i + self._group_offset) % num_groups
            group = self._groups[(i + self._group_offset) % num_groups]

            if not group.is_available():
                continue

            logger.debug(f'Selected group idx: {group_idx}')
            return group
        time.sleep(1)
        return self._next_group()

    def next_job(self) -> RepeatableJob:
        logger.debug(
            f'Scheduling next group... (group_offset={self._group_offset}, group_count={len(self._groups)})')

        group = self._next_group()
        return group.next_job()
