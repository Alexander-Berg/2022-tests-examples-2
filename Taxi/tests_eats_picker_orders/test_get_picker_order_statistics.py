import datetime

import pytest


async def test_get_picker_orders_statistics_400(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.get(
        '/api/v1/picker/orders/statistics',
    )
    assert response.status == 400


@pytest.mark.now('2021-05-20T00:00:00+0000')
@pytest.mark.parametrize(
    'picker_id, date_from, date_to, state, count_expected',
    [
        (
            '0',
            '2021-05-20T00:00:00+0000',
            '2021-05-20T15:00:00+0000',
            'complete',
            11,
        ),
        (
            '0',
            '2021-05-20T00:00:00+0000',
            '2021-05-20T15:00:00+0000',
            'picked_up',
            1,
        ),
        (
            '0',
            '2021-05-20T00:00:00+0000',
            '2021-05-20T15:00:00+0000',
            'cancelled',
            3,
        ),
        (
            '1',
            '2021-05-20T00:00:00+0000',
            '2021-05-20T15:00:00+0000',
            'complete',
            13,
        ),
        (
            '1',
            '2021-05-20T00:00:00+0000',
            '2021-05-20T15:00:00+0000',
            'new',
            1,
        ),
        (
            '1',
            '2021-05-20T00:00:00+0000',
            '2021-05-20T15:00:00+0000',
            'cancelled',
            1,
        ),
        (
            '0',
            '2021-05-20T00:00:00+0000',
            '2021-05-20T15:00:00+0000',
            'new',
            0,
        ),
        (
            '1',
            '2021-05-20T00:00:00+0000',
            '2021-05-20T15:00:00+0000',
            'dispatching',
            0,
        ),
        (
            '0',
            '2021-05-20T01:00:00+0000',
            '2021-05-20T04:00:00+0000',
            'complete',
            3,
        ),
        (
            '0',
            '2021-05-20T12:00:00+0000',
            '2021-05-20T14:00:00+0000',
            'cancelled',
            2,
        ),
        (
            '0',
            '2021-05-20T00:00:00+0000',
            '2021-05-20T02:00:00+0000',
            'picked_up',
            0,
        ),
    ],
)
async def test_get_picker_orders_statistics_200(
        taxi_eats_picker_orders,
        create_order,
        now,
        picker_id,
        date_from,
        date_to,
        state,
        count_expected,
):
    picker_0_states = ['complete'] * 11 + ['picked_up'] + ['cancelled'] * 3
    picker_1_states = ['complete'] * 13 + ['new', 'cancelled']
    picker_ids = ['0'] * len(picker_0_states) + ['1'] * len(picker_1_states)

    states = picker_0_states + picker_1_states
    for i, (picker_id_, state_) in enumerate(zip(picker_ids, states)):
        create_order(
            picker_id=picker_id_,
            eats_id=str(i),
            state=state_,
            created_at=now
            + datetime.timedelta(hours=i % len(picker_0_states)),
        )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/picker/orders/statistics',
        params={
            'picker_id': picker_id,
            'from': date_from,
            'to': date_to,
            'state': state,
        },
    )
    assert response.status == 200
    assert response.json()['count'] == count_expected
