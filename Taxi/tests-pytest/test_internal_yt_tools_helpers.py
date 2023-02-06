import contextlib

import pytest

from taxi.internal.yt_tools import helpers
from taxi.util import threadpool

YT_CLIENTS = {
    'one': 'first_client',
    'two': 'second_client',
}


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('calls,expected_state', [
    (
        ['one', 'two', 'one', 'one', 'two'],
        {'first_client': 3, 'second_client': 2},
    ),
    (
        ['one'] * 20, {'first_client': 20},
    ),
])
def test_performer(patch, calls, expected_state):
    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(name, *args, **kwargs):
        return YT_CLIENTS[name]

    def func(yt_client, local_state):
        local_state.append(yt_client)
        return yt_client

    performer_client = helpers.YTEnvPerformer(func)
    state = []

    with contextlib.closing(threadpool.Pool(2)) as pool:
        pool.start()
        num_tasks = 0
        for client_name in calls:
            pool.put(
                client_name,
                performer_client.perform,
                client_name,
                state,
            )
            num_tasks += 1

        for name, task_status, result_or_exc in pool.get_results(len(calls)):
            assert task_status
            assert YT_CLIENTS[name] == result_or_exc

    state_dict = {key: 0 for key in expected_state.keys()}
    for key in state:
        state_dict[key] += 1
    assert state_dict == expected_state
