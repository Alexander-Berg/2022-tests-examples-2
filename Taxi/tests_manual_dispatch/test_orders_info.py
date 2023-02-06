import datetime

import pytest


def to_dt(string):
    return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%f%z')


def compare_attempts(models, response):
    for attempt in response:
        attempt[
            'performer_id'
        ] = f'{attempt.pop("park_id")}_{attempt.pop("driver_id")}'
        attempt['message'] = attempt.get('message')
        attempt['expiration_ts'] = to_dt(attempt['expiration_ts'])
        attempt['created_ts'] = to_dt(attempt['created_ts'])
    for attempt in models:
        del attempt['operator_id']
        del attempt['order_id']
        del attempt['updated_ts']
        if attempt['status'] == 'filtered' and attempt['message'] is not None:
            attempt['message'] = 'Driver filtered by: ' + attempt['message']
        elif attempt['message'] == 'phone_decline':
            attempt['message'] = 'The driver rejected the offer via phone call'
    response = sorted(response, key=lambda x: x['id'])
    assert models == response


def compare_orders(response, db):
    response['lookup_ttl'] = datetime.timedelta(seconds=response['lookup_ttl'])
    response['manual_switch_interval'] = datetime.timedelta(
        seconds=response['manual_switch_interval'],
    )
    response['corp_id'] = response.pop('corp_client_id', None)
    response['created_ts'] = to_dt(response.pop('created'))
    response['due_ts'] = to_dt(response.pop('due'))
    response['search_ts'] = to_dt(response.pop('search_start'))
    response['tag'] = response.pop('tag', None)
    response.pop('corp_client_name', None)
    db.pop('address_shortname', None)
    db.pop('country', None)
    db.pop('zone_id', None)
    assert response == db


def extract_address_name(order):
    order.pop('address_shortname')


@pytest.mark.parametrize(
    'extra_kwargs',
    [{}, {'order_type': 'c2c', 'corp_id': None, 'tag': 'tag1'}],
)
@pytest.mark.parametrize(
    'n_attempts,locked', [(0, True), (1, False), (2, True)],
)
async def test_orders_info(
        taxi_manual_dispatch,
        create_order,
        get_order,
        create_dispatch_attempt,
        headers,
        n_attempts,
        locked,
        extra_kwargs,
):
    if locked:
        create_order(
            order_id='order_id_1',
            owner_operator_id='yandex_uid_1',
            lock_expiration_ts=datetime.datetime.now()
            + datetime.timedelta(days=1),
            **extra_kwargs,
        )
    else:
        create_order(order_id='order_id_1', **extra_kwargs)

    attempts = [
        create_dispatch_attempt(
            status=status,
            order_id='order_id_1',
            performer_id=f'performer_id_{i}',
            message='phone_decline',
        )
        for i, status in zip(
            range(n_attempts), ('declined', 'declined', 'filtered'),
        )
    ]
    response = await taxi_manual_dispatch.post(
        '/v1/orders/info', json={'order_id': 'order_id_1'}, headers=headers,
    )
    assert response.status_code == 200
    response = response.json()
    response['order']['mirror_only_value'] = True
    compare_orders(
        response['order'],
        get_order(
            'order_id_1',
            excluded=[
                'updated_ts',
                'lookup_version',
                'owner_operator_id',
                'search_params',
                'lock_expiration_ts',
                'cost',
            ],
        ),
    )
    if extra_kwargs.get('order_type', 'b2b') == 'b2b':
        assert response['main_contact'] == {
            'name': 'Baz Buzz',
            'phone_id': '+7123456789012_id',
        }
        assert response['backup_contact'] == {
            'name': 'Spam Eggs',
            'phone_id': '+7123456789012_id',
        }
    assert response['locked_by_user'] == locked
    assert response['polling_delay_ms'] == 15000
    compare_attempts(attempts, response['dispatch_attempts'])


async def test_orders_info_404(taxi_manual_dispatch, headers):
    response = await taxi_manual_dispatch.post(
        '/v1/orders/info', json={'order_id': 'order_id_1'}, headers=headers,
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_not_found'
