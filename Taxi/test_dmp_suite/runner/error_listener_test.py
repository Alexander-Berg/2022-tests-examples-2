import mock
import pytest

from collections import namedtuple
import dmp_suite.datetime_utils as dtu
from dmp_suite.maintenance.accident import Accident, ExecutionType
from dmp_suite.runner import DefaultErrorListener, _AfterCallContext, \
    ScriptCallResult, ExecutionState

TAXIDWH_RUN_ID = 'f02ba147'
ERROR_STRING = 'Script "error" (taxidwh_run_id={}) ' \
               'is finished with exit code -1'.format(TAXIDWH_RUN_ID)


@pytest.mark.parametrize(
    'script_name, script_stderr, return_code, expected_message', [
        ('script_name', 'hello world', 0, 'hello world'),
        ('script_name', 'hello world', 1, 'hello world'),
        ('error', '', -1, ERROR_STRING),
    ])
def test_default_error_listener(capsys, script_name, script_stderr, return_code,
                                expected_message):
    utc_now_dttm = dtu.utcnow()
    accident_client = mock.MagicMock()
    listener = DefaultErrorListener(accident_client, False)

    with mock.patch('dmp_suite.datetime_utils.utcnow', return_value=utc_now_dttm):
        # Для теста нам важно только чтобы в объекте скрипта было имя:
        TestScript = namedtuple('TestScript', ['name', 'execution_type'])
        script = TestScript(name=script_name, execution_type=ExecutionType.SH)

        listener(_AfterCallContext(
            script,
            ScriptCallResult(
                run_id=TAXIDWH_RUN_ID,
                returncode=return_code,
                stderr_string=script_stderr),
            ExecutionState()
        ))
    captured_sys = capsys.readouterr()
    assert expected_message == captured_sys.err

    if return_code == 0:
        accident_client.save.assert_not_called()
    else:
        accident_client.save.assert_called_once_with(Accident(
            script_name, utc_now_dttm, expected_message, TAXIDWH_RUN_ID
        ))
