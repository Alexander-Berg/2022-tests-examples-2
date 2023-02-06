import datetime

import bson
import pytest


@pytest.mark.config(
    ADJUST_APPLICATIONS=['app'], ADJUST_CONFIG={'__default__': True},
)
@pytest.mark.parametrize('coop_type', ['business', 'family', 'invalid'])
async def test_add_success_coop_adjust_event(
        coop_type, stq_runner, mockserver,
):
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
            event_type=f'success_order_{coop_type}_account',
            revenue=5,
            user_id='user_id',
            phone_id='123456789012345678901234',
            yandex_uid='yandex_uid',
            order_id='order_id',
            zone='zone',
        )
        assert request.json['kwargs'] == expected_kwargs
        assert request.json['task_id'] == 'order_id_coop'

    await stq_runner.add_success_coop_adjust_event.call(
        task_id='order_id',
        args=(),
        kwargs=dict(
            payment_type='coop_account',
            main_card_payment_id=(
                f'{coop_type}-6fcb514b-b878-4c9d-95b7-8dc3a7ce6fd8'
            ),
            phone_id=bson.ObjectId('123456789012345678901234'),
            user_id='user_id',
            yandex_uid='yandex_uid',
            order_id='order_id',
            zone='zone',
            cost=5.0,
            currency='currency',
            application='app',
            created_at=created_at,
        ),
    )

    if coop_type != 'invalid':
        assert _queue.times_called
