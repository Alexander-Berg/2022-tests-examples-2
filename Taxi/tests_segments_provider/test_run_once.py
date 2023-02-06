import datetime as dt

import pytest
import pytz

from tests_segments_provider import shipment_tools


_TZ_MOSCOW = pytz.timezone('Europe/Moscow')

_CREATED_AT = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 15, 0, 0))
_NOW = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 16, 0, 0))
_START_AT_1 = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 17, 0, 0))

# sha256(tags.shipment_name)
_TASK_ID = '85335d4133d28c3b1b163aac8387bae71c4ff0d7c957216332b050cec58c8bf0'


def normalized_datetime(value: dt.datetime):
    return value.astimezone(pytz.UTC)


def get_shipment(is_relaunch_requested: bool):
    return shipment_tools.DbShipment(
        name='shipment_name',
        ticket='A-1',
        maintainers=['loginef'],
        is_enabled=True,
        labels=['SQLv1', 'tags', 'unimportant'],
        schedule=shipment_tools.Schedule(
            start_at=_START_AT_1,
            unit=shipment_tools.UnitOfTime.HOURS,
            count=2,
        ),
        source=shipment_tools.YqlQuery(
            shipment_tools.YqlSyntax.SQLv1, 'SELECT \'1\' as tag;',
        ),
        consumer=shipment_tools.TagsConsumerSettings(['tag1', 'tag2'], 'udid'),
        created_at=_CREATED_AT,
        updated_at=_CREATED_AT,
        status=shipment_tools.Status.READY,
        last_modifier='developer',
        is_relaunch_requested=is_relaunch_requested,
    )


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags', get_shipment(is_relaunch_requested=False),
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_run_once(taxi_segments_provider, pgsql, stq):

    response = await taxi_segments_provider.post(
        f'/admin/v1/shipment/run-once',
        json={},
        params={'consumer': 'tags', 'shipment': 'shipment_name'},
        headers={'X-Yandex-Login': 'loginef'},
    )
    assert response.status_code == 200

    assert shipment_tools.find_shipment(
        pgsql, 'tags', 'shipment_name',
    ) == get_shipment(is_relaunch_requested=True)

    assert stq.segments_shipment.has_calls
    stq_args = stq.segments_shipment.next_call()
    del stq_args['kwargs']['log_extra']
    assert stq_args == {
        'args': [],
        'eta': _NOW.astimezone(pytz.UTC).replace(tzinfo=None),
        'kwargs': {'consumer_name': 'tags', 'shipment_name': 'shipment_name'},
        'queue': 'segments_shipment',
        'id': _TASK_ID,
    }
