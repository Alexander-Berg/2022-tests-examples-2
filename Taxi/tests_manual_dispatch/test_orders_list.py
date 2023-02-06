# pylint: disable=redefined-outer-name
import datetime

import pytest

NOW_MINUS_HOUR = datetime.datetime.now(
    tz=datetime.timezone.utc,
) - datetime.timedelta(hours=1)
LOCK_EXPIRATION = NOW_MINUS_HOUR + datetime.timedelta(days=1)


@pytest.fixture()
def create_orders(create_order):
    def wrapped(with_c2c):
        create_order(
            corp_id='client_id_1',
            due_ts=NOW_MINUS_HOUR + datetime.timedelta(minutes=10),
            manual_switch_interval=datetime.timedelta(minutes=5),
            created_ts=NOW_MINUS_HOUR,
            search_ts=NOW_MINUS_HOUR,
            lookup_ttl=datetime.timedelta(minutes=15),
            order_id='order_id_1',
            address_shortname='улица Льва Толстова, 16',
            claim_id='claim_id_2',
            tariff='courier',
            country='rus',
        )
        create_order(
            corp_id='client_id_1',
            due_ts=NOW_MINUS_HOUR + datetime.timedelta(minutes=15),
            search_ts=NOW_MINUS_HOUR + datetime.timedelta(minutes=1),
            lookup_ttl=datetime.timedelta(minutes=5),
            order_id='order_id_2',
            claim_id='claim_id_1',
            tariff='express',
            address_shortname='улица Льва Толстова, 16',
            zone_id='moscow',
        )
        create_order(
            corp_id='client_id_1',
            created_ts=NOW_MINUS_HOUR + datetime.timedelta(minutes=-5),
            due_ts=None,
            lock_expiration_ts=LOCK_EXPIRATION,
            lookup_ttl=datetime.timedelta(minutes=30),
            order_id='order_id_3',
            owner_operator_id='yandex_uid_1',
            search_ts=NOW_MINUS_HOUR + datetime.timedelta(minutes=-5),
        )
        create_order(
            corp_id='client_id_2',
            created_ts=NOW_MINUS_HOUR,
            due_ts=None,
            lock_expiration_ts=LOCK_EXPIRATION,
            lookup_ttl=datetime.timedelta(minutes=15),
            order_id='order_id_4',
            owner_operator_id='yandex_uid_2',
            search_ts=NOW_MINUS_HOUR,
        )
        create_order(
            corp_id='client_id_3',
            status='search_failed',
            order_id='order_id_5',
            address_shortname='Проспект Мира, 12с2',
        )
        create_order(
            corp_id='client_id_3',
            status='finished',
            order_id='order_id_6',
            address_shortname='Проспект Мира, 12с2',
        )
        if with_c2c:
            create_order(
                corp_id=None,
                order_type='c2c',
                tag='tag1',
                order_id='order_id_7',
                search_ts=NOW_MINUS_HOUR,
                manual_switch_interval=datetime.timedelta(minutes=5),
            )
            create_order(
                corp_id=None,
                order_type='c2c',
                tag='tag2',
                order_id='order_id_8',
                search_ts=NOW_MINUS_HOUR,
                manual_switch_interval=datetime.timedelta(minutes=5),
            )
        create_order(
            status='finished',
            order_id='order_id_9',
            address_shortname='Проспект Мира, 12с2',
        )
        create_order(status='finished', order_id='order_id_10')
        create_order(
            corp_id='client_id_1',
            due_ts=NOW_MINUS_HOUR + datetime.timedelta(minutes=20),
            manual_switch_interval=datetime.timedelta(minutes=5),
            created_ts=NOW_MINUS_HOUR,
            search_ts=NOW_MINUS_HOUR + datetime.timedelta(minutes=65),
            lookup_ttl=datetime.timedelta(minutes=15),
            order_id='order_id_11',
            address_shortname='улица Льва Толстова, 16',
            claim_id='claim_id_3',
            tariff='courier',
            new_list_hit_flow=True,
            country='isr',
        )
        create_order(
            corp_id='client_id_1',
            due_ts=NOW_MINUS_HOUR + datetime.timedelta(minutes=60),
            manual_switch_interval=datetime.timedelta(minutes=5),
            created_ts=NOW_MINUS_HOUR,
            search_ts=NOW_MINUS_HOUR + datetime.timedelta(minutes=65),
            lookup_ttl=datetime.timedelta(minutes=15),
            order_id='order_id_12',
            address_shortname='улица Льва Толстова, 16',
            claim_id='claim_id_3',
            tariff='courier',
            new_list_hit_flow=True,
        )

    return wrapped


@pytest.mark.config(
    MANUAL_DISPATCH_COUNTRIES_TRANSLATIONS={
        'Belarus': 'blr',
        'Chile': 'chl',
        'Israel': 'isr',
        'Kazakhstan': 'kaz',
        'Russia': 'rus',
        '__default__': '__Not_Found__',
    },
)
@pytest.mark.parametrize(
    'filter_,ids',
    [
        (
            {'corp_client_id': 'client_id_1', 'state': 'pending'},
            ['order_id_1', 'order_id_2', 'order_id_11'],
        ),
        ({'state': 'locked'}, ['order_id_3']),
        ({'state': 'locked', 'operator_id': 'yandex_uid_2'}, ['order_id_4']),
        ({'state': 'search_failed'}, ['order_id_5']),
        ({'state': 'finished'}, ['order_id_6', 'order_id_9', 'order_id_10']),
        (
            {'state': 'pending', 'order_type': 'b2b'},
            ['order_id_1', 'order_id_2', 'order_id_11'],
        ),
        (
            {'state': 'pending', 'order_type': 'c2c'},
            ['order_id_7', 'order_id_8'],
        ),
        ({'state': 'pending', 'tag': 'tag1'}, ['order_id_7']),
        (
            {
                'state': 'pending',
                'address_shortname': 'улица Льва Толстова, 16',
            },
            ['order_id_1', 'order_id_2', 'order_id_11'],
        ),
        (
            {'state': 'finished', 'address_shortname': 'Проспект Мира, 12с2'},
            ['order_id_6', 'order_id_9'],
        ),
        ({'claim_id': 'claim_id_2', 'state': 'pending'}, ['order_id_1']),
        ({'countries': ['rus'], 'state': 'pending'}, ['order_id_1']),
        ({'countries': ['foo'], 'state': 'pending'}, []),
        ({'zone_ids': ['moscow'], 'state': 'pending'}, ['order_id_2']),
        (
            {'countries': ['rus', 'isr'], 'state': 'pending'},
            ['order_id_1', 'order_id_11'],
        ),
    ],
)
async def test_filters(
        taxi_manual_dispatch, create_orders, headers, filter_, ids,
):
    create_orders(True)

    response = await taxi_manual_dispatch.post(
        '/v1/orders/list',
        headers=headers,
        json={
            'meta': {'offset': 0, 'limit': 5},
            'filter': filter_,
            'order': {'field': 'search_start_ts', 'sequence': 'asc'},
        },
    )
    assert response.status_code == 200
    assert set([x['order_id'] for x in response.json()['orders']]) == set(ids)


@pytest.mark.parametrize('reverse', [True, False])
@pytest.mark.parametrize(
    'field,ids',
    [
        ('search_start_ts', ['order_id_1', 'order_id_2', 'order_id_11']),
        ('search_end_ts', ['order_id_2', 'order_id_1', 'order_id_11']),
        ('order_time', ['order_id_1', 'order_id_2', 'order_id_11']),
    ],
)
async def test_order(
        taxi_manual_dispatch, create_orders, headers, reverse, field, ids,
):
    create_orders(False)
    sequence = 'asc' if not reverse else 'desc'
    ids = ids if not reverse else list(reversed(ids))
    response = await taxi_manual_dispatch.post(
        '/v1/orders/list',
        headers=headers,
        json={
            'meta': {'offset': 0, 'limit': 5},
            'filter': {'state': 'pending'},
            'order': {'field': field, 'sequence': sequence},
        },
    )
    assert response.status_code == 200
    assert response.json()['polling_delay_ms'] == 15000
    assert [x['order_id'] for x in response.json()['orders']] == ids
