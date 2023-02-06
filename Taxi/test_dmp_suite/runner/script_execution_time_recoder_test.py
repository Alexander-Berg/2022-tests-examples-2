from datetime import timedelta

import mock
import pytest

import dmp_suite.datetime_utils as dtu
from dmp_suite.exceptions import DWHError
from dmp_suite.execution_utils import create_task_monitoring
from dmp_suite.runner import (
    _AfterCallContext,
    _BeforeCallContext,
    ScriptExecutionTimeRecoder,
    ScriptCallResult)
from init_py_env import service
from collections import namedtuple


FakeScript = namedtuple('FakeScript', ['name'])


def test_invalid_call():
    recoder = ScriptExecutionTimeRecoder(create_task_monitoring())

    with pytest.raises(DWHError):
        recoder.after_call(_AfterCallContext(
            FakeScript('script_name'),
            ScriptCallResult('', 0, ''),
            None,
        ))

    with pytest.raises(DWHError):
        recoder.before_call(_BeforeCallContext(FakeScript('script_name_1')))
        recoder.after_call(_AfterCallContext(
            FakeScript('script_name_2'),
            ScriptCallResult('', 0, ''),
            None,
        ))


@pytest.mark.parametrize(
    'script_name, script_stderr, return_code', [
        ('script_name', '', 0),
        ('script_name', '', 1),
    ])
def test_valid_call(script_name, script_stderr, return_code):
    solomon_patch = mock.patch('dmp_suite.execution_utils.get_solomon_client')

    with solomon_patch as solomon_mock:
        recoder = ScriptExecutionTimeRecoder(create_task_monitoring())
        utc_now_dttm = dtu.utcnow()
        duration = 2
        with mock.patch('dmp_suite.datetime_utils.utcnow',
                        return_value=utc_now_dttm):
            recoder.before_call(_BeforeCallContext(FakeScript(script_name)))

        with mock.patch('dmp_suite.datetime_utils.utcnow',
                        return_value=utc_now_dttm + timedelta(seconds=duration)):
            recoder.after_call(_AfterCallContext(
                FakeScript(script_name),
                ScriptCallResult(
                    run_id='',
                    returncode=return_code,
                    stderr_string=script_stderr
                ),
                None
            ))
        solomon_mock().send.assert_called_once_with(
            value=duration,
            dttm=utc_now_dttm,
            sensor='task.duration',
            task='script_name',
            etl_service=service.name,
        )
