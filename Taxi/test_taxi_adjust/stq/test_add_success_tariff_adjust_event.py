import datetime

import bson
import pytest


@pytest.mark.config(
    ADJUST_APPLICATIONS=['app'], ADJUST_CONFIG={'__default__': True},
)
async def test_add_success_tariff_adjust_event(stq_runner, mockserver):
    created_at = datetime.datetime(
        2020, 4, 17, 17, 13, 52, tzinfo=datetime.timezone.utc,
    ).strftime('%Y-%m-%dT%H:%M:%S%z')

    @mockserver.json_handler('/stq-agent/queues/api/add/add_adjust_event')
    async def _queue(request):
        assert request.json['args'] == []
        expected_kwargs = dict(
            application='app',
            created_at=created_at,
            currency='currency',
            event_type='success_econom_order',
            revenue=5,
            user_id='user_id',
            phone_id='123456789012345678901234',
            yandex_uid='yandex_uid',
            order_id='order_id',
            zone='zone',
        )
        assert request.json['kwargs'] == expected_kwargs
        assert request.json['task_id'] == 'order_id_econom'

    await stq_runner.add_success_tariff_adjust_event.call(
        task_id='order_id',
        args=(),
        kwargs=dict(
            order_id='order_id',
            user_id='user_id',
            phone_id=bson.ObjectId('123456789012345678901234'),
            yandex_uid='yandex_uid',
            application='app',
            tariff='econom',
            zone='zone',
            cost=5.0,
            currency='currency',
            created_at=created_at,
        ),
    )

    assert _queue.times_called
