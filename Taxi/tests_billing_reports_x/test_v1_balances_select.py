import pytest

from testsuite.utils import ordered_object

import tests_billing_reports_x.utils as utils


# Generated via `tvmknife unittest service -s 222 -d 111`
# service 'mock', added to TMV_SERVICES and TMV_RULES
# see grants section in service.yaml
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUI3gEQbw:U-L2EBkAPaw12kyO2BYKSaGLHz0Bllgmgob99WN'
    'PDMsE5WiG4LD5pMF6UpZ-IuvLOH6rE1lNmbB8cg3h8ZJaN14GoCJbgT07JLfJdswuOKwi6LH9'
    'V2hMkw7lBDEbisoc1unA2gKgP2OiLjEbQ5aAaSxKZaXfmsW8yC05yvnt4v4'
)

# Generated via `tvmknife unittest service -s 333 -d 111`
# service 'other-allowed', added to TMV_SERVICES and TMV_RULES
OTHER_ALLOWED_TICKET = (
    '3:serv:CBAQ__________9_IgUIzQIQbw:Il5LJ7JLt5JkTc2sF5NBl4ygxT0-bYXzKy4snRTy'
    '5vtCI90rPzMAZLy0ZpeQ2ZghjyS1tq8xLnVqJTEagc2hivI-qq_08rEg0aFPp_BwhjVo6VGQQE'
    'z19hyVuas_ezlQ-ANGgdRIeID2uGaVDArbo4iM_zakcZtFzecuXrWY-WA'
)

# Generated via `tvmknife unittest service -s 444 -d 111`
# not added to TMV_SERVICES and TMV_RULES
NOT_ALLOWED_TICKET = (
    '3:serv:CBAQ__________9_IgUIvAMQbw:IUfyUBJGCRcUkeOaLkNpws3LmrCYDwGKd863mUGn'
    'wQuigPAnftBTvnOXvPwALOqGcDZvTWv6q_Esdc5U09xulp5R9N3ScwHc4AEP0ozHnUXb2gk_bf'
    'oGOuLAXx4kvlR3sUopeZnw8iibFKCBImMf-_DvkfPRQRiX7m90LsJyx_E'
)


@pytest.mark.parametrize(
    'settings_path',
    [
        pytest.param('missing_required.json', id='missing required fields'),
        pytest.param('proxy_1_account_1_accrued_at.json', id='proxy 200'),
        pytest.param('proxy_error_400.json', id='proxy 400'),
        pytest.param('proxy_error_403.json', id='don\'t proxy 403'),
        pytest.param('proxy_error_429.json', id='proxy 429'),
        pytest.param('proxy_error_500.json', id='proxy 500'),
    ],
)
async def test_proxy(
        taxi_billing_reports_x, billing_reports, load_json, settings_path,
):
    billing_reports.setup(settings_path)
    settings = load_json(settings_path)
    expected = settings['expected']

    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=settings['request'],
    )

    assert response.status_code == expected['response_code']
    assert billing_reports.times_called() == expected['br_mock_times_called']
    if expected.get('response'):
        ordered_object.assert_eq(
            utils.normalize_datetimes(response.json()),
            utils.normalize_datetimes(expected['response']),
            [''],
        )


@pytest.mark.config(
    BILLING_REPORTS_X_ENABLE_FILTERS={
        '__default__': {'always_enabled': True, 'enable': [], 'compare': []},
    },
    BILLING_REPORTS_X_REPLICATION_OFFSET_HOURS={
        '__default__': 240,
        'balances_select_journals_ttl': 24,
        'balances_select_balances_ttl': 48,
    },
    BILLING_REPORTS_X_STORAGE_REQUEST_QUEUES={
        '__default__': {
            'max_request_size': 10,
            'max_simultaneous_requests': 2,
        },
        'ba-select-balances': {
            'max_request_size': 2,
            'max_simultaneous_requests': 2,
        },
    },
)
@pytest.mark.now('2022-07-04T12:00:00.000+0000')
@pytest.mark.parametrize(
    'settings_path',
    [
        pytest.param(
            'pg_1_account_1_accrued_at.json', id='PG, 1 account, 1 accrued_at',
        ),
        pytest.param(
            'pg_1_account_3_accrued_at.json', id='PG, 1 account, 3 accrued_at',
        ),
        pytest.param(
            'pg_3_account_1_accrued_at.json',
            id='PG, 3 accounts, 1 accrued_at',
        ),
        pytest.param(
            'pg_3_account_3_accrued_at.json', id='PG, 3 account, 3 accrued_at',
        ),
        pytest.param(
            'pg_3_requested_1_returned.json',
            id='PG, 3 accounts requested, 1 returned',
        ),
        pytest.param(
            'pg_3_requested_0_returned.json',
            id='PG, 3 accounts requested, 0 returned',
        ),
        pytest.param('pg_error_500.json', id='PG, 500 from billing-accounts'),
    ],
)
async def test_pg(
        taxi_billing_reports_x, billing_accounts, load_json, settings_path,
):
    billing_accounts.setup(settings_path)
    settings = load_json(settings_path)
    expected = settings['expected']

    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=settings['request'],
    )

    assert response.status_code == expected['response_code']
    assert (
        billing_accounts.times_balances_called()
        == expected['ba_balances_times_called']
    )
    assert billing_accounts.times_accounts_called() == 0
    if expected.get('response'):
        ordered_object.assert_eq(
            utils.normalize_datetimes(response.json()),
            utils.normalize_datetimes(expected['response']),
            [''],
        )


@pytest.mark.config(
    BILLING_REPORTS_X_ENABLE_FILTERS={
        '__default__': {'always_enabled': True, 'enable': [], 'compare': []},
    },
    BILLING_REPORTS_X_REPLICATION_OFFSET_HOURS={
        '__default__': 240,
        'balances_select_journals_ttl': 24,
        'balances_select_balances_ttl': 48,
    },
    BILLING_REPORTS_X_STORAGE_REQUEST_QUEUES={
        '__default__': {
            'max_request_size': 10,
            'max_simultaneous_requests': 2,
        },
        'ba-search-accounts': {
            'max_request_size': 2,
            'max_simultaneous_requests': 2,
        },
    },
)
@pytest.mark.now('2022-07-04T12:00:00.000+0000')
@pytest.mark.yt(dyn_table_data=['yt_balance_at_data.yaml'])
@pytest.mark.parametrize(
    'settings_path',
    [
        pytest.param(
            'yt_1_account_1_accrued_at.json', id='YT, 1 account, 1 accrued_at',
        ),
        pytest.param(
            'yt_1_account_5_accrued_at.json', id='YT, 1 account, 5 accrued_at',
        ),
        pytest.param(
            'yt_5_account_1_accrued_at.json',
            id='YT, 5 accounts, 1 accrued_at',
        ),
        pytest.param(
            'yt_3_account_3_accrued_at.json',
            id='YT, 3 accounts, 3 accrued_at',
        ),
    ],
)
async def test_yt(
        taxi_billing_reports_x,
        billing_accounts,
        load_json,
        settings_path,
        yt_apply,
):
    billing_accounts.setup(settings_path)
    settings = load_json(settings_path)
    expected = settings['expected']

    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=settings['request'],
    )

    assert response.status_code == expected['response_code']
    assert billing_accounts.times_balances_called() == 0
    assert (
        billing_accounts.times_accounts_called()
        == expected['ba_accounts_times_called']
    )
    if expected.get('response'):
        ordered_object.assert_eq(
            utils.normalize_datetimes(response.json()),
            utils.normalize_datetimes(expected['response']),
            [''],
        )


@pytest.mark.config(
    BILLING_REPORTS_X_ENABLE_FILTERS={
        '__default__': {'always_enabled': True, 'enable': [], 'compare': []},
    },
    BILLING_REPORTS_X_REPLICATION_OFFSET_HOURS={
        '__default__': 240,
        'balances_select_journals_ttl': 24,
        'balances_select_balances_ttl': 48,
    },
    BILLING_REPORTS_X_STORAGE_REQUEST_QUEUES={
        '__default__': {
            'max_request_size': 10,
            'max_simultaneous_requests': 2,
        },
        'ba-search-accounts': {
            'max_request_size': 2,
            'max_simultaneous_requests': 2,
        },
        'ba-select-balances': {
            'max_request_size': 2,
            'max_simultaneous_requests': 2,
        },
    },
)
@pytest.mark.now('2022-07-04T12:00:00.000+0000')
@pytest.mark.yt(dyn_table_data=['yt_balance_at_data.yaml'])
@pytest.mark.parametrize(
    'settings_path',
    [
        pytest.param(
            'mixed_1_account_2_accrued_at.json',
            id='YT, 1 account, 2 accrued_at',
        ),
    ],
)
async def test_mixed(
        taxi_billing_reports_x,
        billing_accounts,
        load_json,
        settings_path,
        yt_apply,
):
    billing_accounts.setup(settings_path)
    settings = load_json(settings_path)
    expected = settings['expected']

    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=settings['request'],
    )

    assert response.status_code == expected['response_code']
    assert (
        billing_accounts.times_balances_called()
        == expected['ba_balances_times_called']
    )
    assert (
        billing_accounts.times_accounts_called()
        == expected['ba_accounts_times_called']
    )
    ordered_object.assert_eq(
        utils.normalize_datetimes(response.json()),
        utils.normalize_datetimes(expected['response']),
        [''],
    )


@pytest.mark.config(
    BILLING_REPORTS_X_ENABLE_FILTERS={
        '__default__': {'always_enabled': True, 'enable': [], 'compare': []},
    },
    BILLING_REPORTS_X_REPLICATION_OFFSET_HOURS={
        '__default__': 240,
        'balances_select_journals_ttl': 24,
        'balances_select_balances_ttl': 48,
    },
    BILLING_AUTH_ENABLED=True,
    BILLING_AUTH_SERVICE_GROUPS={
        'mock': ['mock_group1', 'mock_group2'],
        'other-allowed': ['other_group'],
    },
    BILLING_AUTH_GROUPS_RULES={
        'mock_group1': {
            'accounts': [{'agreement': 'taxi/%', 'kind': 'driver'}],
        },
        'mock_group2': {
            'accounts': [
                {'agreement': 'drive/orders', 'kind': 'corp_client'},
                {'agreement': 'eats/%/orders', 'kind': 'corp_client_employee'},
            ],
        },
    },
    TVM_ENABLED=True,
)
@pytest.mark.now('2022-07-04T12:00:00.000+0000')
async def test_auth(taxi_billing_reports_x, billing_accounts):
    billing_accounts.setup('auth_mock_settings.json')

    acc1 = {
        'agreement_id': 'taxi/yandex_ride',
        'currency': 'RUB',
        'entity_external_id': 'taximeter_driver_id/dbid/uuid0',
        'sub_account': 'income',
    }
    acc2 = {
        'agreement_id': 'taxi/yandex_ride',
        'currency': 'RUB',
        'entity_external_id': 'taximeter_driver_id/dbid/uuid2',
        'sub_account': 'income',
    }
    request = {
        'accounts': [acc1],
        'accrued_at': ['2022-07-04T10:20:30.000+0000'],
    }

    headers = {'X-Ya-Service-Ticket': NOT_ALLOWED_TICKET}
    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=request, headers=headers,
    )
    assert response.status_code == 403

    headers = {'X-Ya-Service-Ticket': OTHER_ALLOWED_TICKET}
    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=request, headers=headers,
    )
    assert response.status_code == 403

    headers = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    # 1 request matches mock_group1
    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=request, headers=headers,
    )
    assert response.status_code == 200

    # 1 incorrect entity_external_id (don't match any kind)
    acc1['entity_external_id'] = 'unknown'
    request['accounts'] = [acc1]
    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=request, headers=headers,
    )
    assert response.status_code == 400

    # 1 request doesn't match any rule
    acc1['entity_external_id'] = 'taximeter_driver_id/dbid/uuid0'
    acc1['agreement_id'] = 'some/random/agreement'
    request['accounts'] = [acc1]
    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=request, headers=headers,
    )
    assert response.status_code == 403

    # 1 request, kind and agreement match different rules
    acc1['entity_external_id'] = 'taximeter_driver_id/dbid/uuid0'
    acc1['agreement_id'] = 'drive/orders'
    request['accounts'] = [acc1]
    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=request, headers=headers,
    )
    assert response.status_code == 403

    # 2 requests, one matches, another doesn't
    acc1['entity_external_id'] = 'corp/client/id'
    acc1['agreement_id'] = 'drive/orders'
    acc2['entity_external_id'] = 'corp/client_employee/id'
    acc2['agreement_id'] = 'drive/orders'
    request['accounts'] = [acc1, acc2]
    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=request, headers=headers,
    )
    assert response.status_code == 403

    # 2 requests, both match
    acc1['entity_external_id'] = 'corp/client/id'
    acc1['agreement_id'] = 'drive/orders'
    acc2['entity_external_id'] = 'corp/client_employee/id'
    acc2['agreement_id'] = 'eats/some/orders'
    request['accounts'] = [acc1, acc2]
    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=request, headers=headers,
    )
    assert response.status_code == 200

    # corp/client_department/ doesn't match corp/client/
    acc1['entity_external_id'] = 'corp/client_department/id'
    acc1['agreement_id'] = 'drive/orders'
    request['accounts'] = [acc1]
    response = await taxi_billing_reports_x.post(
        'v1/balances/select', json=request, headers=headers,
    )
    assert response.status_code == 403
