import pytest

from . import utils


@pytest.mark.parametrize(
    'request_yandex_uids, expected_state',
    [
        (['1', '2', '3'], 'ready_to_delete'),
        (['1', '2', '4'], 'ready_to_delete'),
        (['4', '5', '6'], 'empty'),
    ],
)
async def test_takeout_status(
        taxi_eats_retail_order_history,
        create_order,
        request_yandex_uids,
        expected_state,
):
    for i, yandex_uid in enumerate(['1', '2', '3']):
        create_order(order_nr=f'order_nr{i}', yandex_uid=yandex_uid)

    response = await taxi_eats_retail_order_history.post(
        '/takeout/v1/status',
        headers=utils.da_headers(),
        json={
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in request_yandex_uids
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {'data_state': expected_state}


@pytest.mark.parametrize(
    'request_yandex_uids, expected_state',
    [
        (['1', '2', '3'], 'empty'),
        (['1', '2', '4'], 'ready_to_delete'),
        (['4', '5', '6'], 'ready_to_delete'),
    ],
)
async def test_takeout_delete(
        taxi_eats_retail_order_history,
        create_order,
        create_order_item,
        request_yandex_uids,
        expected_state,
):
    for i, yandex_uid in enumerate(['1', '2', '3']):
        order_id = create_order(order_nr=f'order_nr{i}', yandex_uid=yandex_uid)
        create_order_item(
            order_id=order_id,
            name='Спички',
            origin_id='item-7',
            images=['https://yandex.ru/item-7.jpg'],
            count=1,
            cost_for_customer=10,
        )

    response = await taxi_eats_retail_order_history.post(
        '/takeout/v1/delete',
        headers=utils.da_headers(),
        json={
            'request_id': 'request_id',
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in request_yandex_uids
            ],
        },
    )
    assert response.status_code == 200

    response = await taxi_eats_retail_order_history.post(
        '/takeout/v1/status',
        headers=utils.da_headers(),
        json={
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in ['1', '2', '3']
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {'data_state': expected_state}


@pytest.mark.parametrize(
    'request_yandex_uids, expected_state',
    [
        (['1', '2', '3'], 'empty'),
        (['1', '2', '4'], 'ready_to_delete'),
        (['4', '5', '6'], 'ready_to_delete'),
    ],
)
async def test_takeout_delete_stq(
        taxi_eats_retail_order_history,
        stq_runner,
        create_order,
        create_order_item,
        request_yandex_uids,
        expected_state,
):
    for i, yandex_uid in enumerate(['1', '2', '3']):
        order_id = create_order(order_nr=f'order_nr{i}', yandex_uid=yandex_uid)
        create_order_item(
            order_id=order_id,
            name='Спички',
            origin_id='item-7',
            images=['https://yandex.ru/item-7.jpg'],
            count=1,
            cost_for_customer=10,
        )

    await stq_runner.eats_retail_order_history_takeout_delete.call(
        task_id='uuid',
        kwargs={
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in request_yandex_uids
            ],
        },
    )

    response = await taxi_eats_retail_order_history.post(
        '/takeout/v1/status',
        headers=utils.da_headers(),
        json={
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in ['1', '2', '3']
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {'data_state': expected_state}
