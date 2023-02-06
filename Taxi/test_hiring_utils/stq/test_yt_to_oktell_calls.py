# pylint: disable=unused-variable
import pytest

from hiring_utils.stq import yt_to_oktell_calls
from test_hiring_utils import conftest


@conftest.main_configuration
@pytest.mark.now('2020-02-07T00:00:00')
@pytest.mark.config(OKTELL_YT_CALLS_CHUNK_SIZE=1)
async def test_yt_to_oktell_calls(stq3_context, patch):

    call_counter = 0

    @patch('hiring_utils.internal.oktell_manager.execute_operation')
    def patched(*args, **kwargs):
        nonlocal call_counter
        call_counter += 1
        return (True,)

    @patch('hiring_utils.stq.yt_to_oktell_calls.get_table_data')
    async def patched_get_table_data(*args, **kwargs):
        return [
            {
                'id': '12313213',
                'phone': '+79859594523',
                'phone_id': 'a0fe0298b6cf4b7c95f26a8b34e756ee',
                'url': 'https://example.com',
                'process': 'test',
            },
            {
                'id': '12313214',
                'phone': '+79859594524',
                'url': 'https://example.com',
                'process': 'test',
            },
            {
                'id': '12313214',
                'url': 'https://example.com',
                'process': 'test',
            },
        ]

    await yt_to_oktell_calls.task(stq3_context, '12', '2020-02-07T00:00:00')
    assert call_counter == 2
