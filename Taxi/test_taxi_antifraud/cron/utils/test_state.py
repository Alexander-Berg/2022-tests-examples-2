import unittest.mock as mock

import pytest

from taxi_antifraud.crontasks.utils import state


async def test_empty_cursor_database():
    async def _get_cron_state(state_name: str):
        return None

    query_wrapper = mock.MagicMock()
    query_wrapper.get_cron_state = _get_cron_state
    with pytest.raises(Exception, match='Cursor state is None'):
        await state.get_int_postgresql_cursor(
            'Example cursor state', query_wrapper,
        )
