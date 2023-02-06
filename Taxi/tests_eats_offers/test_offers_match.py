import datetime

import pytest

import tests_eats_offers.utils as utils


@pytest.mark.parametrize(
    'request_json, response_code',
    [
        pytest.param(
            {
                'session_id': 'session-id-7',
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'need_prolong': False,
            },
            404,
            id='dont prolong expired offer',
        ),
        pytest.param(
            {
                'session_id': 'session-id-8',
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'need_prolong': True,
            },
            200,
            id='prolong expired offer',
        ),
        pytest.param(
            {
                'session_id': 'unknown-session-id',
                'parameters': {
                    'location': [1, 2],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            404,
            id='offer not found',
        ),
        pytest.param(
            {
                'session_id': 'session-id-2',
                'parameters': {
                    'location': [2, 2],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            404,
            id='offer expired and cannot be prolonged by time',
        ),
        pytest.param(
            {
                'session_id': 'session-id-3',
                'parameters': {
                    'location': [3, 3],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            404,
            id='offer expired and cannot be prolonged by prolongations count',
        ),
        pytest.param(
            {
                'session_id': 'session-id-1',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T13:00:00+00:00',
                },
            },
            400,
            id='offer param delivery_time changed (non-empty -> non-empty)',
        ),
        pytest.param(
            {'session_id': 'session-id-1', 'parameters': {'location': [1, 1]}},
            400,
            id='offer param delivery_time changed (non-empty -> empty)',
        ),
        pytest.param(
            {
                'session_id': 'session-id-5',
                'parameters': {
                    'location': [5, 5],
                    'delivery_time': '2019-10-31T13:00:00+00:00',
                },
            },
            400,
            id='offer param delivery_time changed (empty -> non-empty)',
        ),
        pytest.param(
            {
                'session_id': 'session-id-1',
                'parameters': {
                    'location': [2, 2],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            400,
            id='offer param location changed',
        ),
        pytest.param(
            {
                'session_id': 'session-id-1',
                'parameters': {
                    'location': [1.0004, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            400,
            id='offer param location changed for minimum step',
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
async def test_offer_not_matched(
        taxi_eats_offers, testpoint, request_json, response_code,
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

    response = await taxi_eats_offers.post(
        '/v1/offer/match', json=request_json,
    )
    assert response.status_code == response_code

    assert testpoint_transaction_status.times_called == 1
    assert testpoint_db_select_by_session.times_called == 1
    assert (
        testpoint_db_insert_offer.times_called == 0
        or testpoint_db_insert_offer.times_called == 1
    )


@pytest.mark.parametrize(
    'request_json, response_json, db_expected_json',
    [
        pytest.param(
            {
                'session_id': 'session-id-1',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
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
                'request_time': datetime.datetime(2019, 10, 31, 11, 00),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 1,
                'payload': {'extra-data': 'value'},
            },
            id='offer matched',
        ),
        pytest.param(
            {'session_id': 'session-id-5', 'parameters': {'location': [5, 5]}},
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
                'request_time': datetime.datetime(2019, 10, 31, 11, 00),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 5,
                'payload': {'extra-data': 'value'},
            },
            id='offer matched (empty delivery_time)',
        ),
        pytest.param(
            {
                'session_id': 'session-id-1',
                'parameters': {
                    'location': [1.0003, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
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
                'request_time': datetime.datetime(2019, 10, 31, 11, 00),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 20),
                'prolong_count': 1,
                'payload': {'extra-data': 'value'},
            },
            id='offer matched (location changed less than precision)',
        ),
        pytest.param(
            {
                'session_id': 'session-id-4',
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'need_prolong': True,
            },
            {
                'session_id': 'session-id-4',
                'request_time': '2019-10-31T10:00:00+00:00',
                'expiration_time': '2019-10-31T11:19:30+00:00',
                'prolong_count': 6,
                'parameters': {
                    'location': [4, 4],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'payload': {'extra-data': 'value'},
                'status': 'OFFER_PROLONGED',
            },
            {
                'session_id': 'session-id-4',
                'location': '(4,4)',
                'delivery_time': datetime.datetime(2019, 10, 31, 12, 0),
                'request_time': datetime.datetime(2019, 10, 31, 10, 0),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 19, 30),
                'prolong_count': 6,
                'payload': {'extra-data': 'value'},
            },
            id='prolong expired offer',
        ),
        pytest.param(
            {
                'session_id': 'session-id-6',
                'parameters': {'location': [6, 6]},
                'need_prolong': True,
            },
            {
                'session_id': 'session-id-6',
                'request_time': '2019-10-31T10:00:00+00:00',
                'expiration_time': '2019-10-31T11:19:30+00:00',
                'prolong_count': 7,
                'parameters': {'location': [6, 6]},
                'payload': {'extra-data': 'value'},
                'status': 'OFFER_PROLONGED',
            },
            {
                'session_id': 'session-id-6',
                'location': '(6,6)',
                'delivery_time': None,
                'request_time': datetime.datetime(2019, 10, 31, 10, 0),
                'expiration_time': datetime.datetime(2019, 10, 31, 11, 19, 30),
                'prolong_count': 7,
                'payload': {'extra-data': 'value'},
            },
            id='prolong expired offer (empty delivery_time)',
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
async def test_offer_matched(
        taxi_eats_offers,
        testpoint,
        pgsql,
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

    response = await taxi_eats_offers.post(
        '/v1/offer/match', json=request_json,
    )
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
    'user, request_json, response_code',
    [
        pytest.param(
            'other_user',
            {
                'session_id': 'other_session',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T11:00:00+00:00',
                },
            },
            404,
            id='not found',
        ),
        pytest.param(
            'user-id-3',
            {
                'session_id': 'other_session',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T11:00:00+00:00',
                },
            },
            400,
            id='parameters changed (found by user)',
        ),
        pytest.param(
            'other_user',
            {
                'session_id': 'session-id-16',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T11:00:00+00:00',
                },
            },
            400,
            id='parameters changed (found by session)',
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
@pytest.mark.config(EATS_OFFERS_FEATURE_FLAGS={'use_auth_in_search': True})
async def test_loginned_offer_not_matched(
        taxi_eats_offers, testpoint, user, request_json, response_code,
):
    @testpoint('testpoint_transaction_status')
    def testpoint_transaction_status(data):
        assert data['transaction_status'] == 'commited'

    @testpoint('testpoint_db_select_by_user')
    def testpoint_db_select_by_user(data):
        assert data['db_operation'] == 'SELECT by user'

    @testpoint('testpoint_db_select_by_session')
    def testpoint_db_select_by_session(data):
        assert data['db_operation'] == 'SELECT by session'

    @testpoint('testpoint_db_insert_offer')
    def testpoint_db_insert_offer(data):
        assert data['db_operation'] == 'INSERT ON CONFLICT DO UPDATE'

    response = await taxi_eats_offers.post(
        '/v1/offer/match',
        json=request_json,
        headers=utils.get_headers_with_user_id(user),
    )
    assert response.status_code == response_code

    assert testpoint_transaction_status.times_called == 1
    if (
            'parameters' in request_json
            and 'location' in request_json['parameters']
    ):
        assert testpoint_db_select_by_user.times_called == 1
    else:
        assert testpoint_db_select_by_session.times_called == 1
    assert (
        testpoint_db_insert_offer.times_called == 0
        or testpoint_db_insert_offer.times_called == 1
    )


@pytest.mark.parametrize(
    'user, request_json, response_status',
    [
        pytest.param(
            'other_user',
            {
                'session_id': 'session-id-11',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            utils.MATCH_STATUS_NO_CHANGES,
            id='offer matched by session',
        ),
        pytest.param(
            'user-id-3',
            {
                'session_id': 'session-id-17',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'need_prolong': True,
            },
            utils.MATCH_STATUS_NO_CHANGES,
            id='offer matched by session (freshest)',
        ),
        pytest.param(
            'other_user',
            {
                'session_id': 'session-id-16',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'need_prolong': True,
            },
            utils.MATCH_STATUS_PROLONGED,
            id='offer prolonged(found by session)',
        ),
        pytest.param(
            'user-id-3',
            {
                'session_id': 'session-id-18',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'need_prolong': True,
            },
            utils.MATCH_STATUS_PROLONGED,
            id='offer prolonged(found by session, freshest)',
        ),
        pytest.param(
            'user-id-2',
            {
                'session_id': 'session-id-11',
                'parameters': {
                    'location': [3, 3],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            utils.MATCH_STATUS_NO_CHANGES,
            id='offer matched by user',
        ),
        pytest.param(
            'user-id-3',
            {
                'session_id': 'other_session',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'need_prolong': True,
            },
            utils.MATCH_STATUS_PROLONGED,
            id='offer prolonged(found by user)',
        ),
        pytest.param(
            'user-id-3',
            {
                'session_id': 'session-id-11',
                'parameters': {
                    'location': [1, 1],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
                'need_prolong': True,
            },
            utils.MATCH_STATUS_PROLONGED,
            id='offer prolonged(preffer user)',
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
@pytest.mark.config(EATS_OFFERS_FEATURE_FLAGS={'use_auth_in_search': True})
async def test_loginned_offer_matched(
        taxi_eats_offers, testpoint, user, request_json, response_status,
):
    @testpoint('testpoint_transaction_status')
    def testpoint_transaction_status(data):
        assert data['transaction_status'] == 'commited'

    @testpoint('testpoint_db_select_by_user')
    def testpoint_db_select_by_user(data):
        assert data['db_operation'] == 'SELECT by user'

    @testpoint('testpoint_db_select_by_session')
    def testpoint_db_select_by_session(data):
        assert data['db_operation'] == 'SELECT by session'

    @testpoint('testpoint_db_insert_offer')
    def testpoint_db_insert_offer(data):
        assert data['db_operation'] == 'INSERT ON CONFLICT DO UPDATE'

    response = await taxi_eats_offers.post(
        '/v1/offer/match',
        json=request_json,
        headers=utils.get_headers_with_user_id(user),
    )
    assert response.status_code == 200
    assert response.json()['status'] == response_status

    assert testpoint_transaction_status.times_called == 1
    if (
            'parameters' in request_json
            and 'location' in request_json['parameters']
    ):
        assert testpoint_db_select_by_user.times_called == 1
    else:
        assert testpoint_db_select_by_session.times_called == 1
    assert (
        testpoint_db_insert_offer.times_called == 0
        or testpoint_db_insert_offer.times_called == 1
    )


@pytest.mark.parametrize(
    'user, request_json, response_status',
    [
        pytest.param(
            'user-id-2',
            {
                'session_id': 'session-id-11',
                'parameters': {
                    'location': [3, 3],
                    'delivery_time': '2019-10-31T12:00:00+00:00',
                },
            },
            utils.MATCH_STATUS_NO_CHANGES,
            id='offer matched by user',
        ),
    ],
)
@pytest.mark.now('2019-10-31T11:10:00+00:00')
@pytest.mark.config(EATS_OFFERS_FEATURE_FLAGS={'use_auth_in_search': True})
async def test_loginned_offer_matched_partner(
        taxi_eats_offers, testpoint, user, request_json, response_status,
):
    @testpoint('testpoint_transaction_status')
    def testpoint_transaction_status(data):
        assert data['transaction_status'] == 'commited'

    @testpoint('testpoint_db_select_by_user')
    def testpoint_db_select_by_user(data):
        assert data['db_operation'] == 'SELECT by user'

    @testpoint('testpoint_db_select_by_session')
    def testpoint_db_select_by_session(data):
        assert data['db_operation'] == 'SELECT by session'

    @testpoint('testpoint_db_insert_offer')
    def testpoint_db_insert_offer(data):
        assert data['db_operation'] == 'INSERT ON CONFLICT DO UPDATE'

    response = await taxi_eats_offers.post(
        '/v1/offer/match',
        json=request_json,
        headers=utils.get_headers_with_partner_id(user),
    )
    assert response.status_code == 200
    assert response.json()['status'] == response_status

    assert testpoint_transaction_status.times_called == 1
    if (
            'parameters' in request_json
            and 'location' in request_json['parameters']
    ):
        assert testpoint_db_select_by_user.times_called == 1
    else:
        assert testpoint_db_select_by_session.times_called == 1
    assert (
        testpoint_db_insert_offer.times_called == 0
        or testpoint_db_insert_offer.times_called == 1
    )
