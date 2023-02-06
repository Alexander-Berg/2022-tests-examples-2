import datetime

import pytest

from replication.common import source_stamp
from replication.plugins.last_replicated_ignore_shards import base_stamp_getter

_DELTA_SECONDS = 600
_PLUGIN = [
    {
        'name': 'last_replicated_ignore_shards',
        'parameters': {
            'source_unit_names': ['shard0'],
            'default_lag_seconds': _DELTA_SECONDS,
        },
    },
]

_NOW = datetime.datetime(2022, 1, 15, 8)


@pytest.mark.parametrize(
    'plugin_parameters, last_synced, stamp, expected_base_stamp',
    [
        ([], None, source_stamp.StampObject('unit', None), None),
        (
            _PLUGIN,
            datetime.datetime(2022, 1, 1, 1),
            source_stamp.StampObject(
                'shard0', datetime.datetime(2020, 1, 1, 1),
            ),
            _NOW - datetime.timedelta(seconds=_DELTA_SECONDS),
        ),
        (
            _PLUGIN,
            datetime.datetime(2022, 1, 1, 1),
            source_stamp.StampObject(
                'shard1', datetime.datetime(2020, 1, 1, 1),
            ),
            datetime.datetime(2020, 1, 1, 1),
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.nofilldb
def test_get_base_stamp_getter(
        plugin_parameters, last_synced, stamp, expected_base_stamp,
):
    stamp_getter = base_stamp_getter.get_base_stamp_getter(
        plugin_parameters, last_synced,
    )
    base_stamp_datetime = stamp_getter(stamp)
    assert base_stamp_datetime == expected_base_stamp
