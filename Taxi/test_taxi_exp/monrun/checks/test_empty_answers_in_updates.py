import inspect
import os

import pytest

from taxi_exp.monrun.checks import empty_answers_in_updates


@pytest.fixture
def relative_load_file():
    def _wrapper(filename):
        caller_filename = inspect.stack()[1][1]
        caller_dir = os.path.dirname(os.path.abspath(caller_filename))
        full_path = os.path.join(caller_dir, 'static', filename)
        try:
            with open(full_path) as fileobj:
                return fileobj.readlines()
        except FileNotFoundError as exc:
            raise ValueError('cannot load file from %s: %s' % (full_path, exc))

    return _wrapper


@pytest.mark.parametrize(
    'expected_answer,log_data',
    [
        ('0; No empty answers', 'with_filled_answer.txt'),
        (
            '1; Empty answer: tskv    timestamp=2020-01-21 22:52:58,048    '
            'module=taxi.util.aiohttp_kit.middleware    '
            'level=INFO    link=cbc8d02b37614fe59b869f013e9b195f    '
            '_type=response    host=exp-vla-01.taxi.dev.yandex.net    '
            'uri=/v1/experiments/updates/?limit=100&newer_than=32404    '
            'method=GET    meta_type=v1/experiments/updates    '
            'meta_code=200    parent_link=07b3097303fabe77ae96d0fe6772b2a4    '
            'span_id=09e6e95f851547d1beb8fbf7367876a3    '
            'trace_id=1579636378-3414a3a6d15dc855    stopwatch_name=api    '
            'total_time=0.006726503372192383    delay=0.006726503372192383    '
            'body=    '
            'text=GET request to /v1/experiments/updates/'
            '?limit=100&newer_than=32404 finished with 200\n',
            'with_empty_answer.txt',
        ),
    ],
)
async def test_empty_answers(
        expected_answer, log_data, patch, relative_load_file, taxi_exp_client,
):  # pylint: disable=redefined-outer-name
    taxi_exp_app = taxi_exp_client.app
    # pylint: disable=unused-variable
    @patch('taxi_exp.monrun.checks.empty_answers_in_updates.get_last_logs')
    def mockreturn(*args, **kwargs):
        return relative_load_file(log_data)

    # pylint: disable=protected-access
    answer = await empty_answers_in_updates._check(
        taxi_exp_app, empty_answers_in_updates.CHECK_NAME,
    )

    assert answer.replace('\t', '    ') == expected_answer
