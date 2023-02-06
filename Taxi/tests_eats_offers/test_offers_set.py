import datetime

import pytest

import tests_eats_offers.utils as utils


@pytest.mark.parametrize(
    'request_json, response_json, db_expected_json',
    [
        pytest.param(
            {
                'session_id': 'new-session-id',
                'parameters': {
                    'location': [1.23, 2.34],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            {
                'session_id': 'new-session-id',
                'request_time': '2019-10-31T11:10:00+00:00',
                'expiration_time': '2019-10-31T11:20:00+00:00',
                'prolong_count': 0,
                'parameters': {
                    'location': [1.23, 2.34],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
                'status': 'NEW_OFFER_CREATED',
            },
            {
                'session_id': 'new-session-id',
                'location': '(1.23,2.34)',
                'delivery_time': datetime.datetime(2019, 10, 31, 12, 0),
                'request_time': datetime.datetime(2019, 10, 31, 11, 10),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 0,
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            id='create new offer',
        ),
        pytest.param(
            {
                'session_id': 'new-session-id-empty-delivery',
                'parameters': {'location': [1.23, 2.34]},
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            {
                'session_id': 'new-session-id-empty-delivery',
                'request_time': '2019-10-31T11:10:00+00:00',
                'expiration_time': '2019-10-31T11:20:00+00:00',
                'prolong_count': 0,
                'parameters': {'location': [1.23, 2.34]},
                'payload': {'surge': 100, 'name': 'my-name'},
                'status': 'NEW_OFFER_CREATED',
            },
            {
                'session_id': 'new-session-id-empty-delivery',
                'location': '(1.23,2.34)',
                'delivery_time': None,
                'request_time': datetime.datetime(2019, 10, 31, 11, 10),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 0,
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            id='create new offer (empty delivery_time)',
        ),
        pytest.param(
            {
                'session_id': 'session-id-1',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
            },
            {
                'session_id': 'session-id-1',
                'request_time': '2019-10-31T11:00:00+00:00',
                'expiration_time': '2019-10-31T11:20:00+00:00',
                'prolong_count': 1,
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
                'status': 'NO_CHANGES',
            },
            {
                'session_id': 'session-id-1',
                'location': '(1,1)',
                'delivery_time': datetime.datetime(2019, 10, 31, 12, 0),
                'request_time': datetime.datetime(2019, 10, 31, 11, 0),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 1,
                'payload': {'extra-data': 'value'},
            },
            id='fetch valid offer',
        ),
        pytest.param(
            {
                'session_id': 'session-id-5',
                'parameters': {'location': [5, 5]},
                'payload': {'extra-data': 'value'},
            },
            {
                'session_id': 'session-id-5',
                'request_time': '2019-10-31T11:00:00+00:00',
                'expiration_time': '2019-10-31T11:20:00+00:00',
                'prolong_count': 5,
                'parameters': {'location': [5, 5]},
                'payload': {'extra-data': 'value'},
                'status': 'NO_CHANGES',
            },
            {
                'session_id': 'session-id-5',
                'location': '(5,5)',
                'delivery_time': None,
                'request_time': datetime.datetime(2019, 10, 31, 11, 0),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 5,
                'payload': {'extra-data': 'value'},
            },
            id='fetch valid offer (empty delivery_time)',
        ),
        pytest.param(
            {
                'session_id': 'session-id-1',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            {
                'session_id': 'session-id-1',
                'request_time': '2019-10-31T11:00:00+00:00',
                'expiration_time': '2019-10-31T11:20:00+00:00',
                'prolong_count': 1,
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
                'status': 'PAYLOAD_UPDATED',
            },
            {
                'session_id': 'session-id-1',
                'location': '(1,1)',
                'delivery_time': datetime.datetime(2019, 10, 31, 12, 0),
                'request_time': datetime.datetime(2019, 10, 31, 11, 0),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 1,
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            id='update valid offer payload',
        ),
        pytest.param(
            {
                'session_id': 'session-id-1',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T13:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            {
                'session_id': 'session-id-1',
                'request_time': '2019-10-31T11:10:00+00:00',
                'expiration_time': '2019-10-31T11:20:00+00:00',
                'prolong_count': 0,
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T13:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
                'status': 'NEW_OFFER_CREATED',
            },
            {
                'session_id': 'session-id-1',
                'location': '(1,1)',
                'delivery_time': datetime.datetime(2019, 10, 31, 13, 0),
                'request_time': datetime.datetime(2019, 10, 31, 11, 10),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 0,
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            id='re-create offer on delivery_time changed '
            '(non-empty -> non-empty)',
        ),
        pytest.param(
            {
                'session_id': 'session-id-1',
                'parameters': {'location': [1, 1]},
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            {
                'session_id': 'session-id-1',
                'request_time': '2019-10-31T11:10:00+00:00',
                'expiration_time': '2019-10-31T11:20:00+00:00',
                'prolong_count': 0,
                'parameters': {'location': [1, 1]},
                'payload': {'surge': 100, 'name': 'my-name'},
                'status': 'NEW_OFFER_CREATED',
            },
            {
                'session_id': 'session-id-1',
                'location': '(1,1)',
                'delivery_time': None,
                'request_time': datetime.datetime(2019, 10, 31, 11, 10),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 0,
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            id='re-create offer on delivery_time changed (non-empty -> empty)',
        ),
        pytest.param(
            {
                'session_id': 'session-id-5',
                'parameters': {
                    'location': [5, 5],
                    'delivery_time': '2019-10-31T13:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            {
                'session_id': 'session-id-5',
                'request_time': '2019-10-31T11:10:00+00:00',
                'expiration_time': '2019-10-31T11:20:00+00:00',
                'prolong_count': 0,
                'parameters': {
                    'location': [5, 5],
                    'delivery_time': '2019-10-31T13:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
                'status': 'NEW_OFFER_CREATED',
            },
            {
                'session_id': 'session-id-5',
                'location': '(5,5)',
                'delivery_time': datetime.datetime(2019, 10, 31, 13, 0),
                'request_time': datetime.datetime(2019, 10, 31, 11, 10),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 0,
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            id='re-create offer on delivery_time changed (empty -> non-empty)',
        ),
        pytest.param(
            {
                'session_id': 'session-id-1',
                'parameters': {
                    'location': [1, 2],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            {
                'session_id': 'session-id-1',
                'request_time': '2019-10-31T11:10:00+00:00',
                'expiration_time': '2019-10-31T11:20:00+00:00',
                'prolong_count': 0,
                'parameters': {
                    'location': [1, 2],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
                'status': 'NEW_OFFER_CREATED',
            },
            {
                'session_id': 'session-id-1',
                'location': '(1,2)',
                'delivery_time': datetime.datetime(2019, 10, 31, 12, 0),
                'request_time': datetime.datetime(2019, 10, 31, 11, 10),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 0,
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            id='re-create offer on location changed',
        ),
        pytest.param(
            {
                'session_id': 'session-id-2',
                'parameters': {
                    'location': [2, 2],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            {
                'session_id': 'session-id-2',
                'request_time': '2019-10-31T11:10:00+00:00',
                'expiration_time': '2019-10-31T11:20:00+00:00',
                'prolong_count': 0,
                'parameters': {
                    'location': [2, 2],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'surge': 100, 'name': 'my-name'},
                'status': 'NEW_OFFER_CREATED',
            },
            {
                'session_id': 'session-id-2',
                'location': '(2,2)',
                'delivery_time': datetime.datetime(2019, 10, 31, 12, 0),
                'request_time': datetime.datetime(2019, 10, 31, 11, 10),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 0,
                'payload': {'surge': 100, 'name': 'my-name'},
            },
            id='re-create expired offer',
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
async def test_base_offer_set(
        taxi_eats_offers,
        pgsql,
        testpoint,
        request_json,
        response_json,
        db_expected_json,
):
    @testpoint('testpoint_transaction_status')
    def testpoint_transaction_status(data):
        assert data['transaction_status'] == 'commited'

    @testpoint('testpoint_db_select_by_session')
    def testpoint_db_select_by_session(data):
        assert data['db_operation'] == 'SELECT by session'

    @testpoint('testpoint_db_insert_offer')
    def testpoint_db_insert_offer(data):
        assert data['db_operation'] == 'INSERT ON CONFLICT DO UPDATE'

    response = await taxi_eats_offers.post('/v1/offer/set', json=request_json)
    assert response.status_code == 200
    assert response.json() == response_json

    assert testpoint_transaction_status.times_called == 1
    assert testpoint_db_select_by_session.times_called == 1
    assert (
        testpoint_db_insert_offer.times_called == 0
        or testpoint_db_insert_offer.times_called == 1
    )

    offer = utils.get_offer_from_pg_by_session_id(
        pgsql, request_json['session_id'],
    )
    assert (
        utils.get_subdict(offer, db_expected_json.keys()) == db_expected_json
    )


@pytest.mark.parametrize(
    'user, request_json, response_status',
    [
        pytest.param(
            'other_user',
            {
                'session_id': 'other_session',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
            },
            utils.SET_STATUS_NEW,
            id='new user, new session',
        ),
        pytest.param(
            'user-id-1',
            {
                'session_id': 'other_session',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
            },
            utils.SET_STATUS_NO_CHANGES,
            id='find freshest by user',
        ),
        pytest.param(
            'user-id-1',
            {
                'session_id': 'other_session',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:10:00+00:00',
                },
                'payload': {'extra-data': 'value'},
            },
            utils.SET_STATUS_NEW,
            id='delivery time changed',
        ),
        pytest.param(
            'user-id-1',
            {
                'session_id': 'other_session',
                'parameters': {
                    'location': [1, 2],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
            },
            utils.SET_STATUS_NEW,
            id='location changed',
        ),
        pytest.param(
            'user-id-1',
            {
                'session_id': 'other_session',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'other_value'},
            },
            utils.SET_STATUS_PAYLOAD_UPDATED,
            id='payload changed',
        ),
        pytest.param(
            'user-id-1',
            {
                'session_id': 'other_session',
                'parameters': {
                    'location': [2, 2],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
            },
            utils.SET_STATUS_NO_CHANGES,
            id='choose by location (new session)',
        ),
        pytest.param(
            'user-id-1',
            {
                'session_id': 'session-id-11',
                'parameters': {
                    'location': [2, 2],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
            },
            utils.SET_STATUS_NO_CHANGES,
            id='choose by location (old session)',
        ),
        pytest.param(
            'other_user',
            {
                'session_id': 'session-id-15',
                'parameters': {
                    'location': [3, 3],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value 2'},
            },
            utils.SET_STATUS_NO_CHANGES,
            id='find by session',
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
@pytest.mark.config(EATS_OFFERS_FEATURE_FLAGS={'use_auth_in_search': True})
async def test_loginned_offer_set(
        taxi_eats_offers, user, request_json, response_status, testpoint,
):
    @testpoint('testpoint_transaction_status')
    def testpoint_transaction_status(data):
        assert data['transaction_status'] == 'commited'

    @testpoint('testpoint_db_select_by_user')
    def testpoint_db_select_by_user(data):
        assert data['db_operation'] == 'SELECT by user'

    @testpoint('testpoint_db_insert_offer')
    def testpoint_db_insert_offer(data):
        assert data['db_operation'] == 'INSERT ON CONFLICT DO UPDATE'

    response = await taxi_eats_offers.post(
        '/v1/offer/set',
        json=request_json,
        headers=utils.get_headers_with_user_id(user),
    )
    assert response.status_code == 200
    assert response.json()['status'] == response_status

    assert testpoint_transaction_status.times_called == 1
    assert testpoint_db_select_by_user.times_called == 1
    assert (
        testpoint_db_insert_offer.times_called == 0
        or testpoint_db_insert_offer.times_called == 1
    )


@pytest.mark.now('2019-10-31T11:10:00+00:00')
@pytest.mark.config(EATS_OFFERS_FEATURE_FLAGS={'use_auth_in_search': False})
async def test_use_auth_in_search_feature_flag(taxi_eats_offers):
    response = await taxi_eats_offers.post(
        '/v1/offer/set',
        json={
            'session_id': 'other_session',
            'parameters': {
                'location': [1, 1],
                'delivery_time': '2019-10-31T12:00:00+00:00',
            },
            'payload': {'extra-data': 'value'},
        },
        headers=utils.get_headers_with_user_id('user-id-1'),
    )
    assert response.status_code == 200
    assert response.json()['status'] == utils.SET_STATUS_NEW


@pytest.mark.parametrize(
    'user, request_json',
    [
        pytest.param(
            'some_unique_user',
            {
                'session_id': 'some_unique_session_dxn73hyds7n3hx',
                'parameters': {
                    'location': [1, 2],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
            },
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
@pytest.mark.config(EATS_OFFERS_FEATURE_FLAGS={'use_auth_in_search': True})
async def test_exception_rollback(
        taxi_eats_offers, user, request_json, testpoint, pgsql,
):
    @testpoint('testpoint_db_insert_offer')
    def testpoint_db_insert_offer(data):
        assert data['db_operation'] == 'INSERT ON CONFLICT DO UPDATE'

    @testpoint('testpoint_exception_rollback')
    def testpoint_exception_rollback(data):
        pass

    offers = utils.get_offer_count_from_pg(pgsql, request_json['session_id'])
    assert offers == 0

    response = await taxi_eats_offers.post(
        '/v1/offer/set',
        json=request_json,
        headers=utils.get_headers_with_user_id(user),
    )
    assert response.status_code == 500

    assert testpoint_db_insert_offer.times_called == 1
    assert testpoint_exception_rollback.times_called == 1

    offers = utils.get_offer_count_from_pg(pgsql, request_json['session_id'])
    assert offers == 0
