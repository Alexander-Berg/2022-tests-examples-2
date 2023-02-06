# pylint: disable=import-error
from grocery_mocks.utils import stq as stq_utils

from testsuite.utils import callinfo

from . import consts
from . import models
from .plugins import configs
from .plugins import database


class _Stq:
    def __init__(self, stq_queue: callinfo.AsyncCallQueue):
        self._queue = stq_queue

    @property
    def queue(self):
        return self._queue

    def events(self):
        return stq_utils.created_events(self.queue)


class JobPipeline:
    def __init__(
            self,
            stq_runner,
            stq,
            grocery_takeout_db: database.Database,
            grocery_takeout_configs: configs.Context,
    ):
        self._stq_runner = stq_runner
        self._stq = stq
        self.db = grocery_takeout_db
        self.configs = grocery_takeout_configs

        self.stq_job_start = _Stq(stq.grocery_takeout_job_start)
        self.stq_job_finalize = _Stq(stq.grocery_takeout_job_finalize)
        self.stq_entity_post_load = _Stq(stq.grocery_takeout_entity_post_load)
        self.stq_entity_load_ids = _Stq(stq.grocery_takeout_entity_load_ids)
        self.stq_entity_load_by_id = _Stq(
            stq.grocery_takeout_entity_load_by_id,
        )
        self.stq_entity_delete_by_id = _Stq(
            stq.grocery_takeout_entity_delete_by_id,
        )

    def set_graph(self, graph: models.EntityGraph):
        self.configs.entity_graph(graph)

    async def run_start(
            self,
            job_id=consts.JOB_ID,
            job_type=models.JobType.load,
            yandex_uids=None,
            till_dt=consts.NOW,
            expect_fail: bool = False,
            **kwargs,
    ):
        if yandex_uids is None:
            yandex_uids = [consts.YANDEX_UID]

        kwargs = {
            'job_id': job_id,
            'job_type': job_type,
            'yandex_uids': yandex_uids,
            'till_dt': till_dt,
            **kwargs,
        }

        await self._stq_runner.grocery_takeout_job_start.call(
            task_id=job_id, kwargs=kwargs, expect_fail=expect_fail,
        )

    async def run_finalize(
            self, job_id=consts.JOB_ID, expect_fail: bool = False,
    ):
        kwargs = {'job_id': job_id}

        await self._stq_runner.grocery_takeout_job_finalize.call(
            task_id=job_id, kwargs=kwargs, expect_fail=expect_fail,
        )

    async def run_entity_post_load(
            self,
            task_id='task_id',
            job_id=consts.JOB_ID,
            entity_type=consts.ENTITY_TYPE,
            expect_fail: bool = False,
    ):
        kwargs = {'job_id': job_id, 'entity_type': entity_type}

        await self._stq_runner.grocery_takeout_entity_post_load.call(
            task_id=task_id, kwargs=kwargs, expect_fail=expect_fail,
        )

    async def run_entity_load_ids(
            self,
            task_id='task_id',
            job_id=consts.JOB_ID,
            entity_type=consts.ENTITY_TYPE,
            request_entity_type=consts.ENTITY_TYPE,
            request_entity_index: int = 0,
            iteration_number: int = 0,
            cursor: dict = None,
            expect_fail: bool = False,
    ):
        kwargs = {
            'job_id': job_id,
            'entity_type': entity_type,
            'request_entity_type': request_entity_type,
            'request_entity_index': request_entity_index,
            'iteration_number': iteration_number,
            'cursor': cursor,
        }

        await self._stq_runner.grocery_takeout_entity_load_ids.call(
            task_id=task_id, kwargs=kwargs, expect_fail=expect_fail,
        )

    async def run_entity_load_by_id(
            self,
            task_id='task_id',
            job_id=consts.JOB_ID,
            entity_type=consts.ENTITY_TYPE,
            request_entity_type=consts.ENTITY_TYPE,
            request_entity_index: int = 0,
            expect_fail: bool = False,
    ):
        kwargs = {
            'job_id': job_id,
            'entity_type': entity_type,
            'request_entity_type': request_entity_type,
            'request_entity_index': request_entity_index,
        }

        await self._stq_runner.grocery_takeout_entity_load_by_id.call(
            task_id=task_id, kwargs=kwargs, expect_fail=expect_fail,
        )

    async def run_entity_delete_by_id(
            self,
            task_id='task_id',
            job_id=consts.JOB_ID,
            entity_type=consts.ENTITY_TYPE,
            request_entity_type=consts.ENTITY_TYPE,
            request_entity_index: int = 0,
            expect_fail: bool = False,
    ):
        kwargs = {
            'job_id': job_id,
            'entity_type': entity_type,
            'request_entity_type': request_entity_type,
            'request_entity_index': request_entity_index,
        }

        await self._stq_runner.grocery_takeout_entity_delete_by_id.call(
            task_id=task_id, kwargs=kwargs, expect_fail=expect_fail,
        )

    async def process(self):
        await stq_utils.gather(
            self._stq_runner,
            self.stq_job_start.queue,
            self.stq_job_finalize.queue,
            self.stq_entity_post_load.queue,
            self.stq_entity_load_ids.queue,
            self.stq_entity_load_by_id.queue,
            self.stq_entity_delete_by_id.queue,
        )
