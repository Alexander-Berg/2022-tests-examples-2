import datetime
import json

import bson
import pytest


def assert_on_phonelocks(db, now, orders, phone_id):
    phonelocks_doc = db.phonelocks.find_one({'i': phone_id})
    assert phonelocks_doc is not None
    assert phonelocks_doc['i'] == phone_id
    assert phonelocks_doc.get('x', []) == []
    assert phonelocks_doc['o'] == orders


def assert_on_devicelocks(db, now, orders, device_id):
    devicelocks_doc = db.devicelocks.find_one({'i': device_id})
    assert devicelocks_doc is not None
    assert devicelocks_doc['i'] == device_id
    assert devicelocks_doc.get('x', []) == []
    assert devicelocks_doc['o'] == orders


def assert_on_cardlocks(db, now, orders, card_id):
    cardlocks_doc = db.cardlocks.find_one({'i': card_id})
    assert cardlocks_doc is not None
    assert cardlocks_doc['i'] == card_id
    assert cardlocks_doc['o'] == orders
    assert cardlocks_doc.get('x', []) == []


@pytest.mark.now('2017-01-01T00:30:00Z')
@pytest.mark.config(
    MAX_UNFINISHED_ORDERS=1, AFS_USER_CHECK_CAN_MAKE_ORDER=True,
)
@pytest.mark.parametrize('new_flow_card_reserve_enabled', [False, True])
@pytest.mark.parametrize(
    'commit_url,concurrent_error_code,unpaid_error_code,rollback_error_code',
    [
        ('3.0/ordercommit', 429, 406, 406),
        ('internal/ordercommit', 200, 200, 200),
    ],
)
def test_card_reserve(
        taxi_protocol,
        load,
        db,
        mockserver,
        config,
        experiments3,
        now,
        new_flow_card_reserve_enabled,
        commit_url,
        concurrent_error_code,
        unpaid_error_code,
        rollback_error_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    """
    Check logic of handler:
    1. order
    2. idempotency (nothing change with the same order)
    3. concurrent order (all same, but different order_id).
    Should be failed (status == 'draft')
    4. rollback concurrent request
    5. create concurent order (same credit card, other device_id).
    Should be success on concurrent ride from other device but same credit card
    6. rollbacks in existing concurrent orders
    """

    _mock_surge(mockserver)
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='order_commit_new_flow_card_reserve',
        consumers=['protocol/ordercommit'],
        clauses=[
            {
                'title': '',
                'value': {'enabled': new_flow_card_reserve_enabled},
                'predicate': {'type': 'true'},
            },
        ],
    )

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848b',
    }

    # will be needed later in concurrent checking
    # ensure failure (status == 'draft') on 2nd order with same phone/device
    second_proc = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )
    assert second_proc is not None
    # change order_id
    second_proc['_id'] = 'bac5a147e5eca603789334cda1cbf1fa'
    second_proc['_shard_id'] = 62

    # will be needed later in concurrent order
    # ensure success on concurrent ride from other device but same credit card
    third_proc = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )
    assert third_proc is not None
    third_proc['_id'] = '31ea7cb68c0cb9af48f9efa8fda5462a'
    third_proc['_shard_id'] = 63
    third_proc['order']['device_id'] = '11111111-2222-2222-2222-A0803A68F201'
    third_proc['order']['user_id'] = 'cb18e1ec864879b06b9b0449ad16ad01'
    third_proc['order']['user_phone_id'] = bson.ObjectId(
        '123456789012345678901234',
    )

    # 1. CHECK RESPONSE
    _mock_antifraud(
        mockserver,
        '0c1dd6723153692ec43a5827e3603ac9',
        '5714f45e98956f06baaae3d4',
        '272fbd2b67b0bb9c5135d71d1d1a848b',
    )

    response = taxi_protocol.post(commit_url, request)
    assert response.status_code == 200

    # check order info

    proc = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )
    assert proc is not None

    assert proc['order']['request']['payment'] == {
        'payment_method_id': 'card-x5619',
        'type': 'card',
    }

    assert proc['status'] == 'pending'
    assert proc['commit_state'] == 'done'
    assert proc['order']['status'] == 'pending'
    assert proc['order']['user_uid'] == '4006736929'

    # check card info

    card = db.cards.find_one({'payment_id': 'card-x5619'})

    assert card is not None

    # remove non card info
    card.pop('_id', None)
    card.pop('updated', None)

    assert card == {
        'billing_id': 'x5619',
        'blocking_reason': '',
        'busy_with': [{'order_id': '272fbd2b67b0bb9c5135d71d1d1a848b'}],
        'created': datetime.datetime(2017, 1, 1, 0, 30),
        'currency': 'RUB',
        'expiration_date': datetime.datetime(2022, 11, 1, 0, 0),
        'number': '411111****1111',
        'owner_name': '',
        'owner_uid': '4006736929',
        'payment_id': 'card-x5619',
        'persistent_id': 'af5f30505fe146e38930b08889eeaa2e',
        'region_id': 225,
        'regions_checked': [{'id': 225}],
        'service_labels': [
            'taxi:persistent_id:af5f30505fe146e38930b08889eeaa2e',
        ],
        'aliases': [],
        'permanent_payment_id': '',
        'system': 'VISA',
        'type': 'card',
        'valid': True,
    }

    assert_on_phonelocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        bson.ObjectId('5714f45e98956f06baaae3d4'),
    )
    assert_on_devicelocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        '0c1dd6723153692ec43a5827e3603ac9',
    )
    assert_on_cardlocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        'af5f30505fe146e38930b08889eeaa2e',
    )

    # 2. TEST IDEMPOTENCY

    response = taxi_protocol.post(commit_url, request)
    assert response.status_code == 200

    assert_on_phonelocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        bson.ObjectId('5714f45e98956f06baaae3d4'),
    )
    assert_on_devicelocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        '0c1dd6723153692ec43a5827e3603ac9',
    )
    assert_on_cardlocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        'af5f30505fe146e38930b08889eeaa2e',
    )

    # 3. CREATE CONCURENT ORDER

    db.order_proc.insert(second_proc)

    # ensure failure (status == 'draft') on 2nd order with same phone/device
    request_2nd = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': 'bac5a147e5eca603789334cda1cbf1fa',
    }

    _mock_antifraud(
        mockserver,
        '0c1dd6723153692ec43a5827e3603ac9',
        '5714f45e98956f06baaae3d4',
        'bac5a147e5eca603789334cda1cbf1fa',
    )

    response = taxi_protocol.post(commit_url, request_2nd)
    assert response.status_code == concurrent_error_code

    proc = db.order_proc.find_one(
        {'order.user_id': request_2nd['id'], '_id': request_2nd['orderid']},
    )
    assert proc is not None
    assert proc['status'] == 'draft'
    assert proc['commit_state'] == 'init'

    assert_on_phonelocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        bson.ObjectId('5714f45e98956f06baaae3d4'),
    )
    assert_on_devicelocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        '0c1dd6723153692ec43a5827e3603ac9',
    )
    assert_on_cardlocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        'af5f30505fe146e38930b08889eeaa2e',
    )

    # 4. ROLLBACK 2nd

    db.order_proc.update(
        {'_id': 'bac5a147e5eca603789334cda1cbf1fa'},
        {'$set': {'commit_state': 'rollback'}},
    )
    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': 'bac5a147e5eca603789334cda1cbf1fa',
    }

    response = taxi_protocol.post(commit_url, request)
    assert response.status_code == rollback_error_code

    assert_on_phonelocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        bson.ObjectId('5714f45e98956f06baaae3d4'),
    )
    assert_on_devicelocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        '0c1dd6723153692ec43a5827e3603ac9',
    )
    assert_on_cardlocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        'af5f30505fe146e38930b08889eeaa2e',
    )

    # 5. CREATE CONCURENT ORDER (SAME CREDIT CARD, OTHER DEVICE_ID)

    db.order_proc.insert(third_proc)

    # ensure success on concurrent ride from other device but same credit card

    request_3rd = {
        'id': 'cb18e1ec864879b06b9b0449ad16ad01',
        'orderid': '31ea7cb68c0cb9af48f9efa8fda5462a',
    }

    _mock_antifraud(
        mockserver,
        'cb18e1ec864879b06b9b0449ad16ad01',
        '123456789012345678901234',
        '31ea7cb68c0cb9af48f9efa8fda5462a',
    )

    response = taxi_protocol.post(commit_url, request_3rd)
    assert response.status_code == 200

    assert_on_phonelocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        bson.ObjectId('5714f45e98956f06baaae3d4'),
    )
    assert_on_phonelocks(
        db,
        now,
        ['31ea7cb68c0cb9af48f9efa8fda5462a'],
        bson.ObjectId('123456789012345678901234'),
    )
    assert_on_devicelocks(
        db,
        now,
        ['272fbd2b67b0bb9c5135d71d1d1a848b'],
        '0c1dd6723153692ec43a5827e3603ac9',
    )
    assert_on_devicelocks(
        db,
        now,
        ['31ea7cb68c0cb9af48f9efa8fda5462a'],
        'cb18e1ec864879b06b9b0449ad16ad01',
    )
    assert_on_cardlocks(
        db,
        now,
        [
            '272fbd2b67b0bb9c5135d71d1d1a848b',
            '31ea7cb68c0cb9af48f9efa8fda5462a',
        ],
        'af5f30505fe146e38930b08889eeaa2e',
    )

    # 6. TEST ROLLBACK(S)
    # check orders fields are empty
    db.order_proc.update(
        {'_id': '272fbd2b67b0bb9c5135d71d1d1a848b'},
        {'$set': {'commit_state': 'rollback'}},
    )
    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848b',
    }

    response = taxi_protocol.post(commit_url, request)
    assert response.status_code == rollback_error_code

    assert_on_phonelocks(
        db, now, [], bson.ObjectId('5714f45e98956f06baaae3d4'),
    )
    assert_on_phonelocks(
        db,
        now,
        ['31ea7cb68c0cb9af48f9efa8fda5462a'],
        bson.ObjectId('123456789012345678901234'),
    )
    assert_on_devicelocks(db, now, [], '0c1dd6723153692ec43a5827e3603ac9')
    assert_on_devicelocks(
        db,
        now,
        ['31ea7cb68c0cb9af48f9efa8fda5462a'],
        'cb18e1ec864879b06b9b0449ad16ad01',
    )
    assert_on_cardlocks(
        db,
        now,
        ['31ea7cb68c0cb9af48f9efa8fda5462a'],
        'af5f30505fe146e38930b08889eeaa2e',
    )

    db.order_proc.update(
        {'_id': '31ea7cb68c0cb9af48f9efa8fda5462a'},
        {'$set': {'commit_state': 'rollback'}},
    )
    request = {
        'id': 'cb18e1ec864879b06b9b0449ad16ad01',
        'orderid': '31ea7cb68c0cb9af48f9efa8fda5462a',
    }

    response = taxi_protocol.post(commit_url, request)
    assert response.status_code == rollback_error_code

    assert_on_phonelocks(
        db, now, [], bson.ObjectId('5714f45e98956f06baaae3d4'),
    )
    assert_on_phonelocks(
        db, now, [], bson.ObjectId('123456789012345678901234'),
    )
    assert_on_devicelocks(db, now, [], '0c1dd6723153692ec43a5827e3603ac9')
    assert_on_devicelocks(db, now, [], 'cb18e1ec864879b06b9b0449ad16ad01')
    assert_on_cardlocks(db, now, [], 'af5f30505fe146e38930b08889eeaa2e')


@pytest.mark.now('2017-01-01T00:30:00Z')
@pytest.mark.filldb(phonelocks='for_concurrent_cash_order')
@pytest.mark.config(MAX_UNFINISHED_ORDERS=1)
@pytest.mark.parametrize(
    'commit_url,error_code',
    [('3.0/ordercommit', 429), ('internal/ordercommit', 200)],
)
def test_concurrent_cash_order(
        taxi_protocol, load, db, cardstorage, now, commit_url, error_code,
):
    """
    phone_id is blocked for concurrent orders
    (see DB 'db_phonelocks_for_concurrent_cash_order').
    Original commit_state is 'pending', after concurrent order is 'init'
    phone_ids should be the same in
    'db_orders' & 'db_phonelocks_for_concurrent_cash_order'
    """

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848b',
    }

    response = taxi_protocol.post(commit_url, request)

    assert response.status_code == error_code

    proc = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )
    assert proc is not None
    assert proc['status'] == 'draft'
    assert proc['commit_state'] == 'init'


@pytest.mark.now('2017-01-01T00:30:00Z')
@pytest.mark.config(MAX_UNFINISHED_ORDERS=1)
@pytest.mark.parametrize('url', ('3.0/ordercommit', 'internal/ordercommit'))
def test_second_card_reserve_svo(
        taxi_protocol, load, db, mockserver, now, url, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    _mock_surge(mockserver)

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848c',
    }

    response = taxi_protocol.post(url, request)

    assert response.status_code == 200

    proc = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )

    assert proc is not None
    assert proc['status'] == 'pending'
    assert proc['commit_state'] == 'done'


_AFS_PARAMETRIZE = [
    ('3.0/ordercommit', True, 200),
    ('3.0/ordercommit', False, 429),
    ('internal/ordercommit', True, 200),
    ('internal/ordercommit', False, 200),
    ('3.0/ordercommit', None, 200),
    ('internal/ordercommit', None, 200),
]


def _afs_check(
        taxi_protocol,
        load,
        mockserver,
        pricing_data_preparer,
        url,
        can_make_order,
        expected_code,
):
    pricing_data_preparer.set_locale('ru')

    _mock_surge(mockserver)
    if can_make_order is not None:
        _mock_antifraud(
            mockserver,
            '0c1dd6723153692ec43a5827e3603ac9',
            '5714f45e98956f06baaae3d4',
            '272fbd2b67b0bb9c5135d71d1d1a848b',
            can_make_order=can_make_order,
        )
    else:
        _mock_antifraud_fail(mockserver)

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848b',
    }

    response = taxi_protocol.post(url, request)
    assert response.status_code == expected_code


@pytest.mark.now('2017-01-01T00:30:00Z')
@pytest.mark.config(AFS_USER_CHECK_CAN_MAKE_ORDER=True)
@pytest.mark.parametrize('url,can_make_order,expected_code', _AFS_PARAMETRIZE)
def test_card_reserve_antifraud_on(
        taxi_protocol,
        load,
        mockserver,
        pricing_data_preparer,
        url,
        can_make_order,
        expected_code,
):
    _afs_check(
        taxi_protocol,
        load,
        mockserver,
        pricing_data_preparer,
        url,
        can_make_order,
        expected_code,
    )


@pytest.mark.now('2017-01-01T00:30:00Z')
@pytest.mark.config(AFS_USER_CHECK_CAN_MAKE_ORDER=False)
@pytest.mark.parametrize('url,can_make_order,expected_code', _AFS_PARAMETRIZE)
def test_card_reserve_antifraud_off(
        taxi_protocol,
        load,
        mockserver,
        pricing_data_preparer,
        url,
        can_make_order,
        expected_code,
):
    _afs_check(
        taxi_protocol,
        load,
        mockserver,
        pricing_data_preparer,
        url,
        can_make_order,
        200,
    )


@pytest.mark.now('2017-01-01T00:30:00Z')
@pytest.mark.parametrize('fallback_enabled', (True, False))
def test_card_reserve_fallback(
        taxi_protocol, db, mockserver, fallback_enabled, pricing_data_preparer,
):
    """
    Check fallback logic in card_reserve.
    If fallback is enabled, GetCardAndMarkAsBusy will return empty card
    and won't mark card as busy
    """

    pricing_data_preparer.set_locale('ru')
    fallbacks = _mock_statistics_agent_fallbacks(mockserver, fallback_enabled)
    metrics = _mock_statistics_agent_metrics(mockserver)

    request = {
        'id': '0c1dd6723153692ec43a5827e3603ac9',
        'orderid': '272fbd2b67b0bb9c5135d71d1d1a848b',
    }

    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == 200

    # check order info
    proc = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )
    assert proc is not None
    order = proc['order']
    assert order['request']['payment'] == {
        'payment_method_id': 'card-x5619',
        'type': 'card',
    }

    # check that card info in payment tech is empty (except card_id) if
    # fallback is enabled
    tech = proc['payment_tech']
    assert tech['main_card_payment_id'] == 'card-x5619'
    if fallback_enabled:
        assert not tech['main_card_billing_id']
        assert not tech['main_card_persistent_id']
    else:
        assert tech['main_card_billing_id'] == 'x5619'
        assert (
            tech['main_card_persistent_id']
            == 'af5f30505fe146e38930b08889eeaa2e'
        )

    assert proc['status'] == 'pending'
    assert proc['commit_state'] == 'done'
    assert order['status'] == 'pending'
    assert order['user_uid'] == '4006736929'

    # check card info
    card = db.cards.find_one({'payment_id': 'card-x5619'})
    assert card is not None

    # remove non card info
    card.pop('_id', None)
    card.pop('updated', None)

    # check that card isn't busy if fallback is enabled
    if fallback_enabled:
        busy_with = []
    else:
        busy_with = [{'order_id': '272fbd2b67b0bb9c5135d71d1d1a848b'}]

    assert card == {
        'billing_id': 'x5619',
        'blocking_reason': '',
        'busy_with': busy_with,
        'created': datetime.datetime(2017, 1, 1, 0, 30),
        'currency': 'RUB',
        'expiration_date': datetime.datetime(2022, 11, 1, 0, 0),
        'number': '411111****1111',
        'owner_name': '',
        'owner_uid': '4006736929',
        'payment_id': 'card-x5619',
        'persistent_id': 'af5f30505fe146e38930b08889eeaa2e',
        'region_id': 225,
        'regions_checked': [{'id': 225}],
        'service_labels': [
            'taxi:persistent_id:af5f30505fe146e38930b08889eeaa2e',
        ],
        'aliases': [],
        'permanent_payment_id': '',
        'system': 'VISA',
        'type': 'card',
        'valid': True,
    }

    assert fallbacks.times_called == 1
    assert metrics.times_called == 0 if fallback_enabled else 1


def _mock_surge(mockserver):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'value': 1.7,
                    'name': 'econom',
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }


def _mock_antifraud(
        mockserver,
        user_id,
        user_phone,
        order_id,
        initial_payment_type='card',
        application='',
        can_make_order=True,
):
    @mockserver.json_handler('/antifraud/client/user/can_make_order')
    def mock_afs(request):
        data = json.loads(request.get_data())
        assert data == {
            'user_id': user_id,
            'user_phone_id': user_phone,
            'order_id': order_id,
            'initial_payment_type': initial_payment_type,
            'application': application,
        }
        return {'can_make_order': can_make_order}


def _mock_antifraud_fail(mockserver):
    @mockserver.json_handler('/antifraud/client/user/can_make_order')
    def mock_afs(request):
        return mockserver.make_response('', 500)


def _mock_statistics_agent_fallbacks(mockserver, fallback_enabled):
    @mockserver.json_handler('/statistics_agent/v1/fallbacks/state')
    def mock_statistics_agent(request):
        data = json.loads(request.get_data())
        assert data == {
            'fallbacks': ['protocol.reserve_card.fallback'],
            'service_name': 'protocol',
        }
        return {
            'service_name': 'protocol',
            'fallbacks': [
                {
                    'name': 'protocol.reserve_card.fallback',
                    'value': fallback_enabled,
                },
            ],
        }

    return mock_statistics_agent


def _mock_statistics_agent_metrics(mockserver):
    @mockserver.json_handler('/statistics_agent/v1/metrics/store')
    def mock_statistics_agent(request):
        data = json.loads(request.get_data())
        assert data == {
            'service_name': 'protocol',
            'metrics': [{'name': 'protocol.reserve_card.success', 'value': 1}],
        }
        return {}

    return mock_statistics_agent
