# pylint: disable=redefined-outer-name
import pytest

from taxi.stq import async_worker_ng

import eats_place_groups_replica.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eats_place_groups_replica.generated.service.pytest_plugins']


@pytest.fixture
def stq_task_info():
    return async_worker_ng.TaskInfo(
        id='1', exec_tries=0, reschedule_counter=1, queue='',
    )
