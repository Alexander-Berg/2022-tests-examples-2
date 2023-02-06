import asyncio
import functools
from typing import List
import unittest.mock as mock

import pytest

from taxi_antifraud.generated.cron.yt_wrapper import plugin as yt_plugin
from taxi_antifraud.yt import common

YT_TABLE_PATH = '//test_table'


async def _executor(func, *args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(
        None, functools.partial(func, *args, **kwargs),
    )


def _prepare_data_and_table(data_size: int, yt_client) -> List[dict]:
    data = [{'abc': 123}] * data_size
    yt_client.write_table(YT_TABLE_PATH, data)
    return data


async def _read_data_and_check(
        data: List[dict], yt_client, buffer_size, cursors_to_check,
) -> None:
    async_yt_client = yt_plugin.AsyncYTClient(yt_client, _executor)
    received_data: List[dict] = []
    received_cursors = []
    start_cursor = 0
    mocked_stats = mock.Mock()
    async for (row, new_cursor) in common.iterate_yt_table_row_batches(
            YT_TABLE_PATH,
            start_cursor,
            buffer_size,
            async_yt_client,
            mocked_stats,
    ):
        received_data.append(row)
        assert new_cursor == len(received_data)
        received_cursors.append(new_cursor)
    assert received_data == data
    assert received_cursors == cursors_to_check


@pytest.mark.parametrize(
    'comment,data_size,buffer_size,cursors_to_check',
    [
        ('buffer_size equals one', 5, 1, list(range(1, 6))),
        ('buffer is greater than data', 650, 4000, list(range(1, 651))),
        ('empty table', 0, 500, []),
        ('one element in table', 1, 500, [1]),
        ('negative buffer', 14, -2, list(range(1, 15))),
        ('zero buffer', 14, 0, list(range(1, 15))),
        ('buffer is smaller than data', 10, 3, list(range(1, 11))),
        ('buffer is bigger than data', 10, 15, list(range(1, 11))),
        ('buffer and data are very big', 10000, 333, list(range(1, 10001))),
    ],
)
async def test_common(
        yt_apply,
        yt_client,
        comment,
        data_size: int,
        buffer_size: int,
        cursors_to_check: List[int],
):
    data = _prepare_data_and_table(data_size, yt_client)
    await _read_data_and_check(data, yt_client, buffer_size, cursors_to_check)
