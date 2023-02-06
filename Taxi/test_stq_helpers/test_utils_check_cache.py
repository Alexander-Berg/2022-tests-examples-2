import dataclasses

import pytest

from taxi.stq import async_worker_ng

from stq_helpers import utils


@dataclasses.dataclass
class Component:
    loaded: bool = True

    @property
    def cache_loaded(self):
        return self.loaded


class Queue:
    async def call(self, *args, **kwargs):
        pass


class Stq:
    some_queue = Queue()


@dataclasses.dataclass
class Context:
    component: Component = Component()
    not_loaded_component: Component = Component(False)
    wrong_component: Stq = Stq()  # has no member "cache_loaded"
    stq: Stq = Stq()


async def task(context, task_info, *args, **kwargs):
    return 1


TASK_INFO = async_worker_ng.TaskInfo(
    id='123', exec_tries=0, reschedule_counter=0, queue='some_queue',
)


@pytest.mark.parametrize(
    'components_to_check, expected_res',
    [(['component'], 1), (['not_loaded_component'], None)],
)
async def test_base(components_to_check, expected_res):
    assert (
        await utils.check_cache_ready(components_to_check)(task)(
            Context(), TASK_INFO,
        )
        == expected_res
    )


@pytest.mark.parametrize(
    'components_to_check, task_info',
    [
        (['wrong_component'], TASK_INFO),
        (['non_existing_component'], TASK_INFO),
        (
            ['non_existing_component'],
            async_worker_ng.TaskInfo(
                id='123',
                exec_tries=0,
                reschedule_counter=0,
                queue='wrong_queue',
            ),
        ),
    ],
)
async def test_wrong_attributes(components_to_check, task_info):
    with pytest.raises(ValueError):
        await utils.check_cache_ready(components_to_check)(task)(
            Context(), task_info,
        )
