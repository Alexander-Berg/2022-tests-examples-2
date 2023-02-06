import datetime

import pytest

import tests_eats_offers.utils as utils


@pytest.mark.parametrize(
    'request_headers, request_json, response_json, db_expected_json',
    [
        pytest.param(
            {
                'X-YaTaxi-Bound-Sessions': (
                    'eats:bound-session-id-9,taxi:bound-session-id-9-2'
                ),
            },
            {
                'session_id': 'session-id-9',
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            {
                'session_id': 'session-id-9',
                'request_time': '2019-10-31T10:02:00+00:00',
                'expiration_time': '2019-10-31T11:25:00+00:00',
                'prolong_count': 1,
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
                'status': 'NO_CHANGES',
            },
            {
                'session_id': 'session-id-9',
                'location': '(4,4)',
                'delivery_time': datetime.datetime(2019, 10, 31, 12, 0),
                'request_time': datetime.datetime(2019, 10, 31, 10, 2),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 25),
                'prolong_count': 1,
                'payload': {'extra-data': 'value'},
            },
            id='offer matched by bound session',
        ),
        pytest.param(
            {'X-YaTaxi-Bound-Sessions': 'eats:bound-session-id-10'},
            {
                'session_id': 'session-id-10',
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            {
                'session_id': 'session-id-10',
                'request_time': '2019-10-31T10:10:00+00:00',
                'expiration_time': '2019-10-31T11:25:00+00:00',
                'prolong_count': 1,
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
                'status': 'NO_CHANGES',
            },
            {
                'session_id': 'session-id-10',
                'location': '(4,4)',
                'delivery_time': datetime.datetime(2019, 10, 31, 12, 0),
                'request_time': datetime.datetime(2019, 10, 31, 10, 10),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 25),
                'prolong_count': 1,
                'payload': {'extra-data': 'value'},
            },
            id='offer matched by session',
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
async def test_offer_matched(
        taxi_eats_offers,
        testpoint,
        pgsql,
        request_headers,
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

    @testpoint('testpoint_db_select_by_user')
    def testpoint_db_select_by_user(data):
        assert data['db_operation'] == 'SELECT by user'

    @testpoint('testpoint_db_insert_offer')
    def testpoint_db_insert_offer(data):
        assert data['db_operation'] == 'INSERT ON CONFLICT DO UPDATE'

    response = await taxi_eats_offers.post(
        '/v1/offer/match', json=request_json, headers=request_headers,
    )
    assert response.status_code == 200
    assert response.json() == response_json

    assert testpoint_transaction_status.times_called == 1
    assert testpoint_db_select_by_session.times_called == 1
    assert testpoint_db_select_by_user.times_called == 0
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
    'request_headers, request_json, response_json, db_expected_json',
    [
        pytest.param(
            {
                'X-YaTaxi-Bound-Sessions': (
                    'eats:bound-session-id-9,taxi:bound-session-id-9-2'
                ),
                'X-Eats-User': 'user_id=1',
            },
            {
                'session_id': 'session-id-9',
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            {
                'session_id': 'session-id-9',
                'request_time': '2019-10-31T10:02:00+00:00',
                'expiration_time': '2019-10-31T11:25:00+00:00',
                'prolong_count': 1,
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
                'status': 'NO_CHANGES',
            },
            {
                'session_id': 'session-id-9',
                'location': '(4,4)',
                'delivery_time': datetime.datetime(2019, 10, 31, 12, 0),
                'request_time': datetime.datetime(2019, 10, 31, 10, 2),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 25),
                'prolong_count': 1,
                'payload': {'extra-data': 'value'},
            },
            id='offer matched by bound session',
        ),
        pytest.param(
            {
                'X-YaTaxi-Bound-Sessions': 'eats:bound-session-id-10',
                'X-Eats-User': 'user_id=1',
            },
            {
                'session_id': 'session-id-10',
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            {
                'session_id': 'session-id-10',
                'request_time': '2019-10-31T10:10:00+00:00',
                'expiration_time': '2019-10-31T11:25:00+00:00',
                'prolong_count': 1,
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
                'status': 'NO_CHANGES',
            },
            {
                'session_id': 'session-id-10',
                'location': '(4,4)',
                'delivery_time': datetime.datetime(2019, 10, 31, 12, 0),
                'request_time': datetime.datetime(2019, 10, 31, 10, 10),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 25),
                'prolong_count': 1,
                'payload': {'extra-data': 'value'},
            },
            id='offer matched by session',
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
@pytest.mark.config(EATS_OFFERS_FEATURE_FLAGS={'use_auth_in_search': True})
async def test_offer_matched_with_user(
        taxi_eats_offers,
        testpoint,
        pgsql,
        request_headers,
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

    @testpoint('testpoint_db_select_by_user')
    def testpoint_db_select_by_user(data):
        assert data['db_operation'] == 'SELECT by user'

    @testpoint('testpoint_db_insert_offer')
    def testpoint_db_insert_offer(data):
        assert data['db_operation'] == 'INSERT ON CONFLICT DO UPDATE'

    response = await taxi_eats_offers.post(
        '/v1/offer/match', json=request_json, headers=request_headers,
    )
    assert response.status_code == 200
    assert response.json() == response_json

    assert testpoint_transaction_status.times_called == 1
    assert testpoint_db_select_by_session.times_called == 0
    assert testpoint_db_select_by_user.times_called == 1
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
