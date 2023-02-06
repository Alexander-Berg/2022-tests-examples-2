import dataclasses
import datetime as dt
from typing import Any
from typing import Dict

import pytest

from taxi_billing_subventions import config
from taxi_billing_subventions.process_doc import subscriptions


class _Config:
    BILLING_DRIVER_MODE_SETTINGS = {
        'driver_fix': [
            {
                'value': {
                    'additional_profile_tags': ['tag'],
                    'commission_enabled': False,
                    'promocode_compensation_enabled': False,
                },
                'start': '2019-01-01T00:00:00+00:00',
            },
        ],
        'driver_fix_extra': [
            {
                'value': {
                    'additional_profile_tags': [],
                    'commission_enabled': True,
                    'promocode_compensation_enabled': True,
                },
                'start': '2019-01-01T00:00:00+00:00',
            },
        ],
    }
    BILLING_DRIVER_MODES_ENABLED = True
    BILLING_DRIVER_MODES_SCOPE: Dict[str, Any] = {}


@dataclasses.dataclass
class _ReportsClient:
    topic: list = dataclasses.field(default_factory=list)

    async def select_docs(self, *args, **kwargs):
        return self.topic


class _GeoBookingRulesCache:
    def items(self):
        return []


class _ZonesCache:
    def __init__(self):
        self.tzinfo_by_zone = {}


class _ContextData:
    def __init__(self, db):
        self.db = db
        self.reports_client = _ReportsClient()
        self.geo_booking_rules_cache = _GeoBookingRulesCache()
        self.config = _Config()
        self.zones_cache = _ZonesCache()


@pytest.mark.parametrize(
    'db_id, uuid, as_of, topic, expected',
    [
        (
            'cdd018511aa84639a7defe170f892e60',
            'e74b88cd64d84ccbb53834aa723b8f44',
            dt.datetime(2019, 11, 26, tzinfo=dt.timezone.utc),
            [
                {
                    'event_at': '2019-11-25T20:13:02.832000+00:00',
                    'doc_id': 1,
                    'data': {
                        'mode': 'driver_fix',
                        'driver': {
                            'park_id': 'cdd018511aa84639a7defe170f892e60',
                            'driver_id': 'e74b88cd64d84ccbb53834aa723b8f44',
                        },
                        'settings': {
                            'rule_id': '_id/5dca7801935ea04415ccc21f',
                            'shift_close_time': '00:00:00+03:00',
                        },
                    },
                },
            ],
            {
                'mode': 'driver_fix',
                'subscription_ref': 'subscription/doc_id/1',
                'shift_close_time': '00:00:00+0300',
                'start': dt.datetime(
                    2019, 11, 25, 20, 13, 2, 832000, tzinfo=dt.timezone.utc,
                ),
            },
        ),
        (
            'cdd018511aa84639a7defe170f892e60',
            'e74b88cd64d84ccbb53834aa723b8f44',
            dt.datetime(2019, 11, 26, tzinfo=dt.timezone.utc),
            [
                {
                    'event_at': '2019-11-25T20:13:02.832000+00:00',
                    'doc_id': 2,
                    'data': {
                        'mode': 'driver_fix',
                        'mode_rule': 'driver_fix_extra',
                        'driver': {
                            'park_id': 'cdd018511aa84639a7defe170f892e60',
                            'driver_id': 'e74b88cd64d84ccbb53834aa723b8f44',
                        },
                        'settings': {
                            'rule_id': '_id/5dca7801935ea04415ccc21f',
                            'shift_close_time': '00:00:00+03:00',
                        },
                    },
                },
            ],
            {
                'mode': 'driver_fix',
                'subscription_ref': 'subscription/doc_id/2',
                'shift_close_time': '00:00:00+0300',
                'start': dt.datetime(
                    2019, 11, 25, 20, 13, 2, 832000, tzinfo=dt.timezone.utc,
                ),
            },
        ),
        (
            'cdd018511aa84639a7defe170f892e60',
            'e74b88cd64d84ccbb53834aa723b8f44',
            dt.datetime(2019, 11, 26, tzinfo=dt.timezone.utc),
            [],
            {
                'mode': 'orders',
                'subscription_ref': None,
                'shift_close_time': None,
            },
        ),
    ],
)
async def test_get_driver_mode(db, db_id, uuid, as_of, topic, expected):
    reports_client = _ReportsClient(topic=topic)
    ctx = _ContextData(db)
    ctx.reports_client = reports_client
    actual_mode = await subscriptions.get_driver_mode(
        data=ctx, db_id=db_id, uuid=uuid, as_of=as_of,
    )
    assert actual_mode.name == expected['mode']
    assert bool(actual_mode.subscription) == bool(expected['subscription_ref'])
    if actual_mode.subscription:
        assert actual_mode.subscription.ref == expected['subscription_ref']
        assert (
            actual_mode.subscription.shift_close_time.strftime('%H:%M:%S%z')
            if actual_mode.subscription.shift_close_time
            else None
        ) == expected['shift_close_time']
        assert actual_mode.subscription.start == expected['start']


@pytest.mark.parametrize(
    'db_id, cfg, expected',
    [
        ('id1', {'db_id': {'include': []}}, False),
        ('id1', {'db_id': {'include': ['id1']}}, True),
        ('id1', {}, True),
        ('id1', {'db_id': {}}, True),
        ('id2', {'db_id': {'include': ['id1', 'id3']}}, False),
    ],
)
@pytest.mark.nofilldb
def test_is_in_scope(monkeypatch, db_id, cfg, expected):
    monkeypatch.setattr(config.Config, 'BILLING_DRIVER_MODES_SCOPE', cfg)
    actual = subscriptions.is_in_scope(config.Config(), db_id)
    assert actual == expected
