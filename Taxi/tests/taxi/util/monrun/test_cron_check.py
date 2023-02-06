import os

import aiohttp
import pytest

from taxi.util.monrun import runner
from tests.taxi.util.monrun import checks


async def _create_context(*args, **kwargs):
    class Context:
        def __init__(self, session):
            self.session = session

    async with aiohttp.ClientSession() as sess:
        yield Context(sess)


async def _create_context_no_session(*args, **kwargs):
    class Context:
        pass

    return Context()


def _run(argv, context_with_session: bool):
    parser = runner.register_checks(
        os.path.dirname(checks.__file__), use_cron_check=True,
    )
    args = parser.parse_args(argv)
    return runner.run(
        (
            _create_context
            if context_with_session
            else _create_context_no_session
        ),
        args,
    )


@pytest.mark.parametrize('context_with_session', [True, False])
@pytest.mark.parametrize(
    'task_name, expected_result',
    [
        pytest.param('some-task-name', '0; OK', id='existing finished task'),
        pytest.param(
            'non-existing-task',
            (
                '2; Problem: no successful launches of '
                '/dev/cron/non-existing-task '
                'in the last 100 seconds'
            ),
            id='non-existing task',
        ),
    ],
)
def test_cron_check(
        patch, response_mock, context_with_session, task_name, expected_result,
):
    @patch('taxi.clients.crons.CronsClient._request')
    async def _request(url: str, method: str, *args, **kwargs):
        assert url == '/utils/v1/get-finished-tasks-count/'
        assert method == 'POST'
        data = kwargs['json']
        if data['task_name'] == 'some-task-name':
            return response_mock(json={'count': 1})
        return response_mock(json={'count': 0})

    result = _run(
        f'cron_job --period 100 {task_name} --force-name'.split(),
        context_with_session=context_with_session,
    )
    assert result == expected_result
