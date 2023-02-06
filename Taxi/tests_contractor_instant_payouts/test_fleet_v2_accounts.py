import decimal

import dateutil
import pytest


NOW = '2020-01-01T20:00:00+03:00'


async def test_get_account_list__empty(fleet_v2, mock_api):
    response = await fleet_v2.get_account_list(park_id='PARK-XX')
    assert response.status_code == 200, response.text
    assert response.json() == {'items': []}


async def test_get_account_list__1st_park(fleet_v2, mock_api):
    response = await fleet_v2.get_account_list(park_id='PARK-01')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'items': [
            {
                'id': '00000000-0000-0000-0000-000000000003',
                'created_at': '2020-01-01T13:00:00+00:00',
                'updated_at': '2020-01-01T13:00:00+00:00',
                'is_enabled': True,
                'name': 'Account 3',
                'kind': 'modulbank',
                'balance': '5555.55',
                'notification_settings': {'is_enabled': False},
            },
            {
                'id': '00000000-0000-0000-0000-000000000001',
                'created_at': '2020-01-01T09:00:00+00:00',
                'updated_at': '2020-01-01T09:00:00+00:00',
                'is_enabled': False,
                'name': 'Account 1',
                'kind': 'modulbank',
                'balance': '1111.11',
                'notification_settings': {'is_enabled': False},
            },
        ],
    }

    mock_modulbank = mock_api['contractor-instant-payouts-modulbank']

    # Fetch 1st account
    mock = mock_modulbank['/api/accounts/a0000000-0000-0000-0000-000000000001']
    assert mock.times_called == 1
    headers = mock.next_call()['request'].headers
    assert headers['Authorization'] == 'f0000000-0000-0000-0000-000000000001'

    # Fetch 2nd account
    mock = mock_modulbank['/api/accounts/a0000000-0000-0000-0000-000000000005']
    assert mock.times_called == 1
    headers = mock.next_call()['request'].headers
    assert headers['Authorization'] == 'f0000000-0000-0000-0000-000000000005'


async def test_get_account_list__2nd_park(fleet_v2, mock_api):
    response = await fleet_v2.get_account_list(park_id='PARK-02')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'items': [
            {
                'id': '00000000-0000-0000-0000-000000000001',
                'created_at': '2020-01-01T10:00:00+00:00',
                'updated_at': '2020-01-01T10:00:00+00:00',
                'is_enabled': True,
                'name': 'Account 1',
                'kind': 'modulbank',
                'balance': '2222.22',
                'notification_settings': {
                    'is_enabled': True,
                    'balance_threshold': '1000.05',
                    'recipient_user_ids': ['user1', 'user2'],
                },
            },
        ],
    }

    mock_modulbank = mock_api['contractor-instant-payouts-modulbank']

    # Fetch account
    mock = mock_modulbank['/api/accounts/a0000000-0000-0000-0000-000000000002']
    assert mock.times_called == 1
    headers = mock.next_call()['request'].headers
    assert headers['Authorization'] == 'f0000000-0000-0000-0000-000000000002'


TEST_BALANCE_NOT_AVAILABLE_PARAMS = [
    (
        'PARK-WITH-ALFABANK-ACCOUNT',
        'alfabank',
        '/contractor-instant-payouts-mozen/api/public/payout/credentials',
    ),
    (
        'PARK-WITH-MODULBANK-ACCOUNT',
        'modulbank',
        '/contractor-instant-payouts-modulbank'
        '/api/accounts/a0000000-0000-0000-0000-000000000002',
    ),
    (
        'PARK-WITH-QIWI-ACCOUNT',
        'qiwi',
        '/contractor-instant-payouts-qiwi'
        '/partner/payout/v1/agents/agent/points/point/balance',
    ),
    (
        'PARK-WITH-TINKOFF-ACCOUNT',
        'tinkoff',
        '/tinkoff-securepay/e2c/v2/GetAccountInfo',
    ),
    (
        'PARK-WITH-INTERPAY-ACCOUNT',
        'interpay',
        '/interpay/v1/emoney/contracts/agent/balance',
    ),
]


@pytest.mark.parametrize(
    ('park_id', 'account_kind', 'external_balance_uri'),
    TEST_BALANCE_NOT_AVAILABLE_PARAMS,
)
async def test_get_account_list__balance_not_available(
        mockserver,
        fleet_v2,
        mock_api,
        park_id,
        account_kind,
        external_balance_uri,
):
    @mockserver.json_handler(external_balance_uri)
    def external_balance_handler(request):
        return mockserver.make_response(status=500)

    response = await fleet_v2.get_account_list(park_id=park_id)

    assert external_balance_handler.has_calls

    assert response.status_code == 200, response.text
    assert response.json() == {
        'items': [
            {
                'id': '00000000-0000-0000-0000-000000000001',
                'created_at': '2020-01-01T10:00:00+00:00',
                'updated_at': '2020-01-01T10:00:00+00:00',
                'is_enabled': True,
                'name': 'Account 1',
                'kind': account_kind,
                'notification_settings': {'is_enabled': False},
            },
        ],
    }


@pytest.mark.now(NOW)
async def test_create_account__success(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.create_account(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-00000000000f',
            'name': 'New Account',
            'kind': 'modulbank',
            'credentials': {
                'modulbank_auth_token': 'f0000000-0000-0000-0000-000000000003',
            },
        },
    )
    assert response.status_code == 204, response.text

    # Check account
    mock = mock_api['contractor-instant-payouts-modulbank']['/api/accounts']
    assert mock.times_called == 1
    headers = mock.next_call()['request'].headers
    assert headers['Authorization'] == 'f0000000-0000-0000-0000-000000000003'

    # Check INN
    mock = mock_api['fleet-parks']['/v1/parks/list']
    assert mock.times_called == 1
    mock = mock_api['parks-replica']['/v1/parks/billing_client_id/retrieve']
    assert mock.times_called == 1
    mock = mock_api['billing-replication']['/contract']
    assert mock.times_called == 1
    mock = mock_api['billing-replication']['/person']
    assert mock.times_called == 1

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'create_account',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'account': {
            **pg_initial['account'],
            1: (
                0,
                1,
                dateutil.parser.parse(NOW),
                1,
                dateutil.parser.parse(NOW),
                'modulbank',
                'PARK-01',
                '00000000-0000-0000-0000-00000000000f',
                False,
                False,
                'New Account',
                'f0000000-0000-0000-0000-000000000003',
                'a0000000-0000-0000-0000-000000000003',
                None,
                False,
                decimal.Decimal('0.0000'),
                [],
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
        },
        'account_change_log': {
            **pg_initial['account_change_log'],
            (1, 0): (
                1,
                dateutil.parser.parse(NOW),
                None,
                False,
                None,
                False,
                None,
                'New Account',
                None,
                False,
                None,
                decimal.Decimal('0.0000'),
                None,
                [],
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_create_account_qiwi_success(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.create_account(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-00000000000f',
            'name': 'New Account',
            'kind': 'qiwi',
            'credentials': {
                'qiwi_agent_id': 'agent',
                'qiwi_point_id': 'point',
                'qiwi_bearer_token': 'f0000000-0000-0000-0000-000000000003',
            },
        },
    )
    assert response.status_code == 204, response.text

    # Check account
    mock = mock_api['contractor-instant-payouts-qiwi'][
        '/partner/payout/v1/agents/agent/points/point/balance'
    ]
    assert mock.times_called == 1
    headers = mock.next_call()['request'].headers
    assert (
        headers['Authorization']
        == 'Bearer f0000000-0000-0000-0000-000000000003'
    )

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'create_account',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'account': {
            **pg_initial['account'],
            1: (
                0,
                1,
                dateutil.parser.parse(NOW),
                1,
                dateutil.parser.parse(NOW),
                'qiwi',
                'PARK-01',
                '00000000-0000-0000-0000-00000000000f',
                False,
                False,
                'New Account',
                None,
                None,
                None,
                False,
                decimal.Decimal('0.0000'),
                [],
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                None,
                None,
                'agent',
                'point',
                'f0000000-0000-0000-0000-000000000003',
                None,
                None,
                None,
            ),
        },
        'account_change_log': {
            **pg_initial['account_change_log'],
            (1, 0): (
                1,
                dateutil.parser.parse(NOW),
                None,
                False,
                None,
                False,
                None,
                'New Account',
                None,
                False,
                None,
                decimal.Decimal('0.0000'),
                None,
                [],
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_create_account_interpay_success(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.create_account(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-00000000000f',
            'name': 'New Account',
            'kind': 'interpay',
            'credentials': {
                'interpay_auth_token': 'auth_token1',
                'interpay_contract_source_id': 1,
                'interpay_contract_origin_id': 2,
            },
        },
    )
    assert response.status_code == 204, response.text

    # Check account
    mock = mock_api['interpay']['/v1/emoney/contracts/1/balance']
    assert mock.times_called == 1
    headers = mock.next_call()['request'].headers
    assert headers['Authorization'] == 'Bearer auth_token1'

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'create_account',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'account': {
            **pg_initial['account'],
            1: (
                0,
                1,
                dateutil.parser.parse(NOW),
                1,
                dateutil.parser.parse(NOW),
                'interpay',
                'PARK-01',
                '00000000-0000-0000-0000-00000000000f',
                False,
                False,
                'New Account',
                None,
                None,
                None,
                False,
                decimal.Decimal('0.0000'),
                [],
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                None,
                None,
                None,
                None,
                None,
                'auth_token1',
                '1',
                '2',
            ),
        },
        'account_change_log': {
            **pg_initial['account_change_log'],
            (1, 0): (
                1,
                dateutil.parser.parse(NOW),
                None,
                False,
                None,
                False,
                None,
                'New Account',
                None,
                False,
                None,
                decimal.Decimal('0.0000'),
                None,
                [],
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_create_account_notification__success(
        fleet_v2, mock_api, pg_dump,
):
    pg_initial = pg_dump()

    response = await fleet_v2.create_account(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-00000000000f',
            'name': 'New Account',
            'kind': 'modulbank',
            'notification_settings': {
                'is_enabled': True,
                'balance_threshold': '5000',
                'recipient_user_ids': ['user1'],
            },
            'credentials': {
                'modulbank_auth_token': 'f0000000-0000-0000-0000-000000000003',
            },
        },
    )
    assert response.status_code == 204, response.text

    # Check account
    mock = mock_api['contractor-instant-payouts-modulbank']['/api/accounts']
    assert mock.times_called == 1
    headers = mock.next_call()['request'].headers
    assert headers['Authorization'] == 'f0000000-0000-0000-0000-000000000003'

    # Check INN
    mock = mock_api['fleet-parks']['/v1/parks/list']
    assert mock.times_called == 1
    mock = mock_api['parks-replica']['/v1/parks/billing_client_id/retrieve']
    assert mock.times_called == 1
    mock = mock_api['billing-replication']['/contract']
    assert mock.times_called == 1
    mock = mock_api['billing-replication']['/person']
    assert mock.times_called == 1

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'create_account',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'account': {
            **pg_initial['account'],
            1: (
                0,
                1,
                dateutil.parser.parse(NOW),
                1,
                dateutil.parser.parse(NOW),
                'modulbank',
                'PARK-01',
                '00000000-0000-0000-0000-00000000000f',
                False,
                False,
                'New Account',
                'f0000000-0000-0000-0000-000000000003',
                'a0000000-0000-0000-0000-000000000003',
                None,
                True,
                decimal.Decimal('5000.0000'),
                ['user1'],
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
        },
        'account_change_log': {
            **pg_initial['account_change_log'],
            (1, 0): (
                1,
                dateutil.parser.parse(NOW),
                None,
                False,
                None,
                False,
                None,
                'New Account',
                None,
                True,
                None,
                decimal.Decimal('5000.0000'),
                None,
                ['user1'],
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_create_account__idempotency(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.create_account(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-000000000001',
            'name': 'Account 1',
            'kind': 'modulbank',
            'credentials': {
                'modulbank_auth_token': 'f0000000-0000-0000-0000-000000000001',
            },
        },
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


@pytest.mark.now(NOW)
async def test_create_account__already_exists(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.create_account(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-000000000001',
            'name': 'Account 1',
            'kind': 'modulbank',
            'credentials': {
                'modulbank_auth_token': 'f0000000-0000-0000-0000-000000000003',
            },
        },
    )
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': 'duplicate_id',
        'message': (
            'Another account has already been created with the specified '
            'identifier.'
        ),
    }

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


@pytest.mark.now(NOW)
async def test_create_account__invalid_modulbank_account__01(
        fleet_v2, mock_api, pg_dump,
):
    pg_initial = pg_dump()

    response = await fleet_v2.create_account(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-00000000000f',
            'name': 'New Account',
            'kind': 'modulbank',
            'credentials': {'modulbank_auth_token': 'NOT_MATCHING_REGEX'},
        },
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'invalid_modulbank_auth_token',
        'message': 'The specified Modulbank authorization token is malformed.',
    }

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


@pytest.mark.now(NOW)
async def test_create_account__invalid_modulbank_account__02(
        fleet_v2, mock_api, pg_dump,
):
    pg_initial = pg_dump()

    response = await fleet_v2.create_account(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-00000000000f',
            'name': 'New Account',
            'kind': 'modulbank',
            'credentials': {
                'modulbank_auth_token': 'ffffffff-ffff-ffff-ffff-000000000401',
            },
        },
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'invalid_modulbank_auth_token',
        'message': 'The specified Modulbank authorization token is invalid.',
    }

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


@pytest.mark.now(NOW)
async def test_create_account__invalid_qiwi_account__01(
        fleet_v2, mock_api, pg_dump,
):
    pg_initial = pg_dump()

    response = await fleet_v2.create_account(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-00000000000f',
            'name': 'New Account',
            'kind': 'qiwi',
            'credentials': {
                'qiwi_bearer_token': 'ffffffff-ffff-ffff-ffff-000000000401',
                'qiwi_agent_id': 'agent',
                'qiwi_point_id': 'point',
            },
        },
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'invalid_qiwi_credentials',
        'message': 'The specified Qiwi credentials are invalid.',
    }

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


@pytest.mark.now(NOW)
async def test_create_account__invalid_interpay_account__01(
        fleet_v2, mock_api, pg_dump,
):
    pg_initial = pg_dump()

    response = await fleet_v2.create_account(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-00000000000f',
            'name': 'New Account',
            'kind': 'interpay',
            'credentials': {
                'interpay_auth_token': 'bad_token',
                'interpay_contract_source_id': 1,
            },
        },
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'invalid_interpay_credentials',
        'message': 'The specified Interpay credentials are invalid.',
    }

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


@pytest.mark.now(NOW)
async def test_create_account__inn_mismatch(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.create_account(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-00000000000f',
            'name': 'New Account',
            'kind': 'modulbank',
            'credentials': {
                'modulbank_auth_token': 'f0000000-0000-0000-0000-000000000002',
            },
        },
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'inn_mismatch',
        'message': (
            'The INN of the account does not match the INN of the park.'
        ),
    }

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


@pytest.mark.now(NOW)
async def test_update_account__success(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.update_account(
        park_id='PARK-01',
        account_id='00000000-0000-0000-0000-000000000001',
        json={'is_enabled': True, 'name': 'Updated Account'},
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'update_account',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'account': {
            **pg_initial['account'],
            101: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'modulbank',
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                False,
                True,
                'Updated Account',
                'f0000000-0000-0000-0000-000000000001',
                'a0000000-0000-0000-0000-000000000001',
                None,
                False,
                decimal.Decimal('0.0000'),
                [],
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
            105: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T16:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'modulbank',
                'PARK-01',
                '00000000-0000-0000-0000-000000000003',
                False,
                False,
                'Account 3',
                'f0000000-0000-0000-0000-000000000005',
                'a0000000-0000-0000-0000-000000000005',
                None,
                False,
                decimal.Decimal('0.0000'),
                [],
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
        },
        'account_change_log': {
            **pg_initial['account_change_log'],
            (101, 1): (
                1,
                dateutil.parser.parse(NOW),
                None,
                None,
                False,
                True,
                'Account 1',
                'Updated Account',
                None,
                None,
                None,
                None,
                None,
                None,
            ),
            (105, 1): (
                1,
                dateutil.parser.parse(NOW),
                None,
                None,
                True,
                False,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_update_account__idempotency(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.update_account(
        park_id='PARK-01',
        account_id='00000000-0000-0000-0000-000000000001',
        json={'is_enabled': False, 'name': 'Account 1'},
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


@pytest.mark.now(NOW)
async def test_delete_account__success(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.delete_account(
        park_id='PARK-01', account_id='00000000-0000-0000-0000-000000000003',
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'delete_account',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'account': {
            **pg_initial['account'],
            105: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T16:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'modulbank',
                'PARK-01',
                '00000000-0000-0000-0000-000000000003',
                True,
                False,
                'Account 3',
                'f0000000-0000-0000-0000-000000000005',
                'a0000000-0000-0000-0000-000000000005',
                None,
                False,
                decimal.Decimal('0.0000'),
                [],
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
        },
        'account_change_log': {
            **pg_initial['account_change_log'],
            (105, 1): (
                1,
                dateutil.parser.parse(NOW),
                False,
                True,
                True,
                False,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_delete_account__idempotency(fleet_v2, mock_api, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.delete_account(
        park_id='PARK-01', account_id='00000000-0000-0000-0000-000000000002',
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == pg_initial, 'Nothing was expected to change'
