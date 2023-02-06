import pytest
from mock import patch

from dmp_suite.py_env.service_setup import Service
from dmp_suite.ctl.extensions.domain.task import (
    TASK_DOMAIN,
    map_task_to_storage_entity,
    TaskDomainProvider,
)
from dmp_suite.ctl.exceptions import CtlError
from dmp_suite.ctl.core import StorageEntity
from dmp_suite.task import PyTask


def load(args):
    raise RuntimeError


task = PyTask(
    "test_task",
    load,
)


def assert_map_callback(callback):
    with patch(
        'dmp_suite.ctl.extensions.domain.task.service',
        Service('test_etl', None, None, None)
    ):
        with pytest.raises(CtlError):
            callback(None)

        expected = StorageEntity(TASK_DOMAIN, 'test_etl.test_task')
        assert expected == callback(task)
        assert expected == callback('test_task')


def test_map_yt_to_storage_entity():
    assert_map_callback(map_task_to_storage_entity)


def test_yt_ctl_provider():
    assert_map_callback(TaskDomainProvider(None).to_storage_entity)
