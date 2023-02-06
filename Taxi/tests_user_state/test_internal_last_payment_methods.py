import pytest


ORDER_FLOW = 'order'
TIPS_FLOW = 'tips'

CASH = 'cash'

TAXI_SERVICE = 'taxi'

DEFAULT_UID = 'uid'
BOTH_FLOWS_UID = 'bound-uid1, bound-uid2'
UNKNOWN_UID = 'unknown_uid'


def build_payment_type(
        payment_type=None, payment_type_id=None, payment_meta=None,
):
    result = {'type': payment_type or CASH}
    if payment_type_id:
        result['id'] = payment_type_id
    if payment_meta:
        result['meta'] = payment_meta
    return result


def build_flow(flow_type=None, main=None, complements=None):
    result = {
        'flow_type': flow_type or ORDER_FLOW,
        'payment_method': main or build_payment_type(),
    }
    if complements:
        result['complements'] = complements
    return result


def check_db_entry(pgsql, uid, service, flow, expected):
    db = pgsql['user_state'].cursor()
    query = f"""
        select yandex_uid, service, flow, payment_info
        from last_payment_methods.flows
        where yandex_uid = '{uid}'
        and flow = '{flow}';
        """
    db.execute(query)
    rows = [row for row in db]
    assert len(rows) == 1
    assert rows[0] == (uid, service, flow, expected)


async def test_put_and_get(taxi_user_state, pgsql):
    main = build_payment_type('card', 'card:123')
    complements = [
        build_payment_type('personal_wallet', 'card:123', payment_meta={}),
    ]
    payload = {'flows': [build_flow(ORDER_FLOW, main, complements)]}

    response = await taxi_user_state.put(
        '/internal/v1/last-payment-methods',
        params={'service': TAXI_SERVICE},
        json=payload,
        headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status == 200
    assert response.json() == {}

    get_response = await taxi_user_state.get(
        '/internal/v1/last-payment-methods',
        params={'service': TAXI_SERVICE},
        headers={'X-Yandex-UID': DEFAULT_UID},
    )

    assert response.status == 200
    assert get_response.json() == payload


@pytest.mark.pgsql('user_state', files=['flows.sql'])
async def test_update(taxi_user_state, pgsql):
    expected_before_update = {'payment_method': build_payment_type()}
    check_db_entry(
        pgsql, DEFAULT_UID, TAXI_SERVICE, ORDER_FLOW, expected_before_update,
    )

    payment_type = build_payment_type('card', 'card:123')
    response = await taxi_user_state.put(
        '/internal/v1/last-payment-methods',
        params={'service': 'taxi'},
        json={'flows': [build_flow(ORDER_FLOW, payment_type)]},
        headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status == 200
    assert response.json() == {}

    expected = {'payment_method': payment_type}
    check_db_entry(pgsql, DEFAULT_UID, TAXI_SERVICE, ORDER_FLOW, expected)


@pytest.mark.pgsql('user_state', files=['flows.sql'])
async def test_get_last_bound(taxi_user_state, pgsql):
    response = await taxi_user_state.get(
        '/internal/v1/last-payment-methods',
        params={'service': 'taxi'},
        headers={
            'X-Yandex-UID': UNKNOWN_UID,
            'X-YaTaxi-Bound-Uids': BOTH_FLOWS_UID,
        },
    )
    assert response.status == 200
    assert response.json() == {
        'flows': [
            {
                'flow_type': 'order',
                'payment_method': {'type': 'card', 'id': 'card:123'},
            },
            {'flow_type': 'tips', 'payment_method': {'type': 'cash'}},
        ],
    }


@pytest.mark.pgsql('user_state', files=['flows.sql'])
async def test_get(taxi_user_state):
    response = await taxi_user_state.get(
        '/internal/v1/last-payment-methods',
        params={'service': 'taxi'},
        headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status == 200
    assert response.json() == {
        'flows': [{'flow_type': 'order', 'payment_method': {'type': 'cash'}}],
    }


async def test_get_empty(taxi_user_state):
    response = await taxi_user_state.get(
        '/internal/v1/last-payment-methods',
        params={'service': 'taxi'},
        headers={'X-Yandex-UID': DEFAULT_UID},
    )
    assert response.status == 200
    assert response.json() == {'flows': []}
