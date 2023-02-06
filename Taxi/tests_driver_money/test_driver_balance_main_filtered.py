# pylint: disable=C0302
import copy
import typing

import pytest

ENDPOINT = '/v1/driver/balance/main/filtered'

PARKS_REQUEST = {
    'fields': {
        'account': ['balance', 'currency'],
        'park': [
            'country_id',
            'tz',
            'city',
            'driver_partner_source',
            'provider_config',
        ],
        'driver_profile': [
            'created_date',
            'first_name',
            'last_name',
            'payment_service_id',
        ],
    },
    'query': {
        'park': {'driver_profile': {'id': ['driver']}, 'id': 'park_id_0'},
    },
    'limit': 1,
    'offset': 0,
}

PARKS_RESPONSE = {
    'driver_profiles': [
        {
            'accounts': [
                {'balance': '2444216.6162', 'currency': 'RUB', 'id': 'driver'},
            ],
            'driver_profile': {
                'id': 'driver',
                'created_date': '2020-12-12T22:22:00.1231Z',
                'first_name': 'Ivan',
                'last_name': 'Ivanov',
                'payment_service_id': '123456',
            },
        },
    ],
    'offset': 0,
    'parks': [
        {
            'id': 'park_id_0',
            'country_id': 'rus',
            'city': 'Москва',
            'tz': 3,
            'driver_partner_source': 'yandex',
            'provider_config': {'yandex': {'clid': 'clid_0'}},
        },
    ],
    'total': 1,
    'limit': 1,
}

CORRECTION_NOTIFICATION_FILES_DOWNLOAD_MATCHED = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'name': 'balance_correction_notification_files_download',
    'consumers': ['driver_money/v1_driver_balance_main_filtered'],
    'clauses': [
        {
            'value': {
                'title_key': 'DriverMoney_Correction_Notification_To_Download',
                'support_title_key': (
                    'DriverMoney_Correction_Notification_Download_Support'
                ),
                'support_deeplink_url': 'taximeter://screen/support',
                'files': [
                    {
                        'title_key': (
                            'DriverMoney_Correction_Notification_PDF_Download'
                        ),
                        'url': 'dir/{park_id}_{uuid}.pdf',
                        'ttl_in_minutes': 20,
                    },
                    {
                        'title_key': (
                            'DriverMoney_Correction_Notification_XLSX_Download'
                        ),
                        'url': 'dir/{park_id}_{uuid}.xlsx',
                        'ttl_in_minutes': 20,
                    },
                ],
            },
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'driver',
                    'arg_name': 'driver_id',
                    'arg_type': 'string',
                },
            },
        },
    ],
}

CORRECTION_NOTIFICATION_FILES_DOWNLOAD_NOT_MATCHED: typing.Dict[
    str, typing.Any,
] = copy.deepcopy(CORRECTION_NOTIFICATION_FILES_DOWNLOAD_MATCHED)
CORRECTION_NOTIFICATION_FILES_DOWNLOAD_NOT_MATCHED['clauses'][0]['predicate'][
    'init'
]['value'] = 'driver_other'

BALANCE_PARKS_SERVICES_SHOW_WITH_BALANCE = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'is_config': False,
    'name': 'balance_parks_services',
    'consumers': ['driver_money/v1_driver_balance_main_filtered'],
    'clauses': [],
    'default_value': {
        'show_parks_services': True,
        'show_parks_services_balance': True,
    },
}

BALANCE_PARKS_SERVICES_SHOW_WITHOUT_BALANCE = copy.deepcopy(
    BALANCE_PARKS_SERVICES_SHOW_WITH_BALANCE,
)
BALANCE_PARKS_SERVICES_SHOW_WITHOUT_BALANCE['default_value'] = {
    'show_parks_services': True,
    'show_parks_services_balance': False,
}

BALANCE_PARKS_SERVICES_NO_SHOWING = copy.deepcopy(
    BALANCE_PARKS_SERVICES_SHOW_WITH_BALANCE,
)
BALANCE_PARKS_SERVICES_NO_SHOWING['default_value'] = {
    'show_parks_services': False,
    'show_parks_services_balance': True,
}

EXPECTED_PARKS_SERVICES_WITH_BALANCE = {
    'accent': True,
    'accent_title': False,
    'detail': '65,11 ₽',
    'horizontal_divider_type': 'top_gap',
    'title': 'Услуги парков',
    'type': 'tip_detail',
    'right_icon': 'navigate',
    'payload': {'type': 'navigate_to_periodic_payments'},
}
EXPECTED_PARKS_SERVICES_WITHOUT_BALANCE = {
    'accent': True,
    'accent_title': False,
    'horizontal_divider_type': 'top_gap',
    'title': 'Услуги парков',
    'type': 'tip_detail',
    'right_icon': 'navigate',
    'payload': {'type': 'navigate_to_periodic_payments'},
}

EXPECTED_CORRECTION_NOTIFICATION_FILES = [
    {
        'horizontal_divider_type': 'top_gap',
        'max_lines': 3,
        'padding': 'small_top_bottom',
        'text': 'Файлы по корректировке баланса',
        'type': 'text',
    },
    {
        'horizontal_divider_type': 'top_gap',
        'payload': {'is_external': True, 'type': 'navigate_url', 'url': ''},
        'right_icon': 'navigate',
        'title': 'Загрузить PDF',
        'type': 'detail',
    },
    {
        'horizontal_divider_type': 'top_gap',
        'payload': {'is_external': True, 'type': 'navigate_url', 'url': ''},
        'right_icon': 'navigate',
        'title': 'Загрузить XLSX',
        'type': 'detail',
    },
    {
        'horizontal_divider_type': 'top_gap',
        'title': 'Поддержка',
        'payload': {'type': 'deeplink', 'url': 'taximeter://screen/support'},
        'right_icon': 'navigate',
        'type': 'detail',
    },
]

EXPECTED_BALANCE_DEPOSIT = {
    'accent': True,
    'accent_title': False,
    'detail': '65,11 ₽',
    'horizontal_divider_type': 'top_gap',
    'payload': {
        'items': [
            {
                'horizontal_divider_type': 'bottom_gap',
                'hint': 'Удержим на депозит 85,11 ₽',
                'subtitle': '65,11 ₽',
                'type': 'header',
            },
            {
                'horizontal_divider_type': 'none',
                'text': (
                    '**150,22 ₽** - размер депозита в Заправках, поэтому они '
                    'остаются на вашем балансе. Так вы сможете заправляться '
                    'всегда, когда нужно.'
                ),
                'markdown': True,
                'type': 'text',
            },
        ],
        'title': 'Депозит Я.Заправки',
        'type': 'constructor',
    },
    'right_icon': 'navigate',
    'title': 'Депозит Я.Заправки',
    'type': 'tip_detail',
}


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.parametrize(
    'folder_name,expected_parks_services_block',
    [
        ('no_data', None),
        ('subventions', None),
        ('payments', None),
        pytest.param(
            'all',
            EXPECTED_PARKS_SERVICES_WITH_BALANCE,
            id='balance_parks_services show with balance',
            marks=pytest.mark.experiments3(
                **BALANCE_PARKS_SERVICES_SHOW_WITH_BALANCE,
            ),
        ),
        pytest.param(
            'all',
            EXPECTED_PARKS_SERVICES_WITHOUT_BALANCE,
            id='balance_parks_services show without balance',
            marks=pytest.mark.experiments3(
                **BALANCE_PARKS_SERVICES_SHOW_WITHOUT_BALANCE,
            ),
        ),
        pytest.param(
            'all',
            None,
            id='balance_parks_services does not show',
            marks=pytest.mark.experiments3(
                **BALANCE_PARKS_SERVICES_NO_SHOWING,
            ),
        ),
    ],
)
async def test_balance_filtered_self_signed(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        fleet_transactions_api,
        billing_reports,
        folder_name,
        expected_parks_services_block,
        taxi_config,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == PARKS_REQUEST
        return PARKS_RESPONSE

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(
        load_json(f'{folder_name}/br_response_balance.json'),
    )
    fleet_transactions_api.set_folder(folder_name)

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json(f'{folder_name}/service_request.json'),
    )
    assert response.status_code == 200

    expected_json = load_json(f'{folder_name}/service_response.json')
    if expected_parks_services_block is not None:
        expected_json['ui'][1] = expected_parks_services_block
    else:
        expected_json['ui'].pop(1)

    assert response.json() == expected_json


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.parametrize('folder_name', ['subventions', 'all', 'no_data'])
async def test_balance_filtered_not_self_signed(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        fleet_transactions_api,
        billing_reports,
        folder_name,
        taxi_config,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == PARKS_REQUEST
        response = copy.deepcopy(PARKS_RESPONSE)
        response['parks'][0].pop('driver_partner_source')
        return response

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(
        load_json(f'{folder_name}/br_response_balance.json'),
    )
    fleet_transactions_api.set_folder(folder_name)

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json(f'{folder_name}/service_request.json'),
    )

    assert response.status_code == 200
    assert response.json() == load_json(f'{folder_name}/service_response.json')


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.config(DRIVER_BALANCE_QUERY_LIMIT=5)
@pytest.mark.parametrize(
    'folder_name,matched_correction_files',
    [
        ('all', True),
        ('no_data', True),
        ('subventions', True),
        pytest.param(
            'all',
            False,
            id='all - not matched in experiment',
            marks=pytest.mark.experiments3(
                **CORRECTION_NOTIFICATION_FILES_DOWNLOAD_NOT_MATCHED,
            ),
        ),
        pytest.param(
            'no_data',
            False,
            id='no_data - not matched in experiment',
            marks=pytest.mark.experiments3(
                **CORRECTION_NOTIFICATION_FILES_DOWNLOAD_NOT_MATCHED,
            ),
        ),
        pytest.param(
            'subventions',
            False,
            id='subventions - not matched in experiment',
            marks=pytest.mark.experiments3(
                **CORRECTION_NOTIFICATION_FILES_DOWNLOAD_NOT_MATCHED,
            ),
        ),
    ],
)
@pytest.mark.experiments3(**CORRECTION_NOTIFICATION_FILES_DOWNLOAD_MATCHED)
async def test_balance_correction_notification_files_download(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        fleet_transactions_api,
        billing_reports,
        folder_name,
        matched_correction_files,
        taxi_config,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == PARKS_REQUEST
        return PARKS_RESPONSE

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(
        load_json(f'{folder_name}/br_response_balance.json'),
    )
    fleet_transactions_api.set_folder(folder_name)

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json(f'{folder_name}/service_request.json'),
    )
    assert response.status_code == 200

    expected_json = load_json(f'{folder_name}/service_response.json')
    actual_json = response.json()
    if matched_correction_files:
        # mds_client генерирует каждый раз новую подпись,
        # поэтому проверять на совпадение не получится
        assert actual_json['ui'][2]['payload']['url'].startswith(
            'https://driver-money.'
            + mockserver.url('/mds-s3')
            + '/dir/park_id_0_driver.pdf',
        )
        assert actual_json['ui'][3]['payload']['url'].startswith(
            'https://driver-money.'
            + mockserver.url('/mds-s3')
            + '/dir/park_id_0_driver.xlsx',
        )
        actual_json['ui'][2]['payload']['url'] = ''
        actual_json['ui'][3]['payload']['url'] = ''
        expected_json['ui'][1:2] = EXPECTED_CORRECTION_NOTIFICATION_FILES
    else:
        expected_json['ui'].pop(1)

    assert actual_json == expected_json


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.config(DRIVER_BALANCE_QUERY_LIMIT=5)
async def test_balance_payments_statuses(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        fleet_transactions_api,
        billing_reports,
        taxi_config,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == PARKS_REQUEST
        return PARKS_RESPONSE

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/search')
    def _mock_payments(request):
        return {
            'payments': [
                {
                    'payment_id': '123',
                    'status': 'TRANSMITTED',
                    'creation_date': '2020-09-04T18:00:00+00:00',
                    'bank_account_number': '123',
                    'payee_name': 'some_smz',
                    'payment_target': 'some_account',
                    'amount': '300.00',
                    'currency': 'RUB',
                },
                {
                    'payment_id': '123',
                    'status': 'CREATED',
                    'creation_date': '2020-09-04T17:00:00+00:00',
                    'bank_account_number': '123',
                    'payee_name': 'some_smz',
                    'payment_target': 'some_account',
                    'amount': '200.00',
                    'currency': 'RUB',
                },
                {
                    'payment_id': '1595',
                    'status': 'CONFIRMED',
                    'creation_date': '2020-09-04T17:00:00+00:00',
                    'bank_account_number': '123',
                    'payee_name': 'some_smz',
                    'payment_target': 'some_account',
                    'amount': '200.00',
                    'currency': 'RUB',
                },
            ],
            'cursor': {},
        }

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(load_json('all/br_response_balance.json'))
    fleet_transactions_api.set_folder('all')

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json('all/service_request.json'),
    )
    assert response.status_code == 200

    expected_json = load_json('all/service_response_payments_statuses.json')

    assert response.json() == expected_json


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.config(DRIVER_BALANCE_QUERY_LIMIT=5)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='instant_payouts',
    consumers=['driver_money/v1_driver_balance_main_filtered'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.parametrize(
    'instant_payouts_status,expected_response',
    [
        (
            {
                'status': 'ready',
                'amount_minimum': '100',
                'amount_maximum': '500',
                'fee_percent': '5',
                'fee_minimum': '50',
            },
            'service_response_instant_ready.json',
        ),
        (
            {
                'status': 'not_available',
                'amount_minimum': '0',
                'amount_maximum': '0',
                'fee_percent': '0',
                'fee_minimum': '0',
            },
            'service_response_instant_disabled.json',
        ),
        (
            {
                'status': 'already_in_progress',
                'amount_minimum': '0',
                'amount_maximum': '0',
                'fee_percent': '0',
                'fee_minimum': '0',
            },
            'service_response_instant_already_in_progress.json',
        ),
    ],
)
async def test_balance_instant_payout(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        fleet_transactions_api,
        billing_reports,
        instant_payouts_status,
        expected_response,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == PARKS_REQUEST
        response = copy.deepcopy(PARKS_RESPONSE)
        response['parks'][0].pop('driver_partner_source')
        return response

    @mockserver.json_handler(
        '/contractor-instant-payouts/v1/contractors/payouts/options',
    )
    def _mock_instant_payouts_options(_):
        return instant_payouts_status

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(load_json('all/br_response_balance.json'))
    fleet_transactions_api.set_folder('all')

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json('all/service_request.json'),
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.config(DRIVER_BALANCE_QUERY_LIMIT=5)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='instant_payouts',
    consumers=['driver_money/v1_driver_balance_main_filtered'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='instant_payouts_button',
    consumers=['driver_money/v1_driver_balance_main_filtered'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.parametrize(
    'instant_payouts_status,expected_response',
    [
        (
            {
                'status': 'ready',
                'amount_minimum': '100',
                'amount_maximum': '500',
                'fee_percent': '5',
                'fee_minimum': '50',
            },
            'service_response_instant_ready_with_button.json',
        ),
        (
            {
                'status': 'not_available',
                'amount_minimum': '0',
                'amount_maximum': '0',
                'fee_percent': '0',
                'fee_minimum': '0',
            },
            'service_response_instant_disabled_with_button.json',
        ),
        (
            {
                'status': 'already_in_progress',
                'amount_minimum': '0',
                'amount_maximum': '0',
                'fee_percent': '0',
                'fee_minimum': '0',
            },
            'service_response_instant_already_in_progress_with_button.json',
        ),
    ],
)
async def test_balance_instant_payout_withdrawal_button(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        fleet_transactions_api,
        billing_reports,
        instant_payouts_status,
        expected_response,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == PARKS_REQUEST
        response = copy.deepcopy(PARKS_RESPONSE)
        response['parks'][0].pop('driver_partner_source')
        return response

    @mockserver.json_handler(
        '/contractor-instant-payouts/v1/contractors/payouts/options',
    )
    def _mock_instant_payouts_options(_):
        return instant_payouts_status

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(load_json('all/br_response_balance.json'))
    fleet_transactions_api.set_folder('all')

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json('all/service_request.json'),
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.config(DRIVER_BALANCE_QUERY_LIMIT=5)
@pytest.mark.parametrize('folder_name', ['all', 'no_data', 'subventions'])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='balance_deposit',
    consumers=['driver_money/v1_driver_balance_main_filtered'],
    clauses=[],
    default_value=True,
)
async def test_balance_deposit(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        fleet_transactions_api,
        billing_reports,
        folder_name,
        taxi_config,
):
    @mockserver.json_handler('/app-tanker/api/corporation/balance/taxi')
    def _mock_app_tanker(request):
        assert request.query['dbId'] == 'park_id_0'
        return {'balance': 65.11, 'limit': 150.22}

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == PARKS_REQUEST
        return PARKS_RESPONSE

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(
        load_json(f'{folder_name}/br_response_balance.json'),
    )
    fleet_transactions_api.set_folder(folder_name)

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json(f'{folder_name}/service_request.json'),
    )
    assert response.status_code == 200

    expected_json = load_json(f'{folder_name}/service_response.json')
    expected_json['ui'][1] = EXPECTED_BALANCE_DEPOSIT
    assert response.json() == expected_json


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='balance_oebs',
    consumers=['driver_money/v1_driver_balance_main_filtered'],
    clauses=[
        {
            'value': {'enabled': True},
            'is_signal': False,
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'set': ['driver'],
                                'arg_name': 'driver_id',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                        {
                            'init': {
                                'value': '2020-04-01T12:00:00.000Z',
                                'arg_name': 'created_date',
                                'arg_type': 'datetime',
                            },
                            'type': 'gte',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'is_paired_signal': False,
        },
    ],
)
@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.parametrize(
    'folder_name,is_newbie,is_created_date_exists,is_self_signed',
    [
        ('subventions', True, True, True),
        ('no_data', True, True, True),
        ('all', True, True, True),
        ('all', False, True, True),
        ('all', False, False, True),
        ('all', True, True, False),
    ],
)
async def test_oebs_balance(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        fleet_transactions_api,
        billing_reports,
        folder_name,
        is_newbie,
        is_created_date_exists,
        is_self_signed,
        taxi_config,
        parks_driver_profiles,
):
    if is_self_signed:
        parks_driver_profiles.make_self_signed_response()
    if not is_created_date_exists:
        parks_driver_profiles.set_created_date(None)
    elif not is_newbie:
        parks_driver_profiles.set_created_date('2020-03-01T12:00:00.000Z')

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(
        load_json(f'{folder_name}/br_response_balance.json'),
    )
    fleet_transactions_api.set_folder(folder_name)

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json(f'{folder_name}/service_request.json'),
    )

    assert response.status_code == 200
    expected_response = load_json(f'{folder_name}/service_response.json')
    if is_self_signed:
        expected_response['ui'].pop(1)
    if is_created_date_exists and is_newbie and is_self_signed:
        expected_response['ui'][0]['subtitle'] = '65,11 ₽'
        expected_response['ui'][0][
            'hint'
        ] = 'Доступный остаток по\n договорам на 3 мая, 15:00'
    assert response.json() == expected_response


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.parametrize(
    'folder_name,status_code,is_response_with_msg',
    [
        ('all', 429, False),
        ('all', 429, True),
        ('no_data', 429, False),
        ('no_data', 429, True),
        ('subventions', 429, False),
        ('subventions', 429, True),
    ],
)
async def test_balance_filtered_fta_429(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        fleet_transactions_api,
        billing_reports,
        folder_name,
        status_code,
        is_response_with_msg,
        taxi_config,
):
    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(
        load_json(f'{folder_name}/br_response_balance.json'),
    )
    fleet_transactions_api.set_transactions_list_429(is_response_with_msg)

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json(f'{folder_name}/service_request.json'),
    )

    assert response.status_code == status_code


@pytest.mark.now('2020-01-16T21:30:00+0300')
async def test_balance_payments_statuses_billing_429(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        fleet_transactions_api,
        billing_reports,
        taxi_config,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == PARKS_REQUEST
        return PARKS_RESPONSE

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/search')
    def _mock_payments(request):
        return mockserver.make_response(status=429)

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(load_json('all/br_response_balance.json'))
    fleet_transactions_api.set_folder('all')

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json('all/service_request.json'),
    )
    assert response.status_code == 429


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.config(DRIVER_BALANCE_QUERY_LIMIT=5)
@pytest.mark.parametrize('folder_name', ['reports'])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='balance_reports_vat',
    consumers=['driver-money/context'],
    clauses=[
        {
            'title': 'driver_profile_id',
            'value': {'enabled': True},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['driver'],
                    'arg_name': 'driver_profile_id',
                    'set_elem_type': 'string',
                },
            },
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'park_id',
            'value': {'enabled': True},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['park_id_0'],
                    'arg_name': 'park_id',
                    'set_elem_type': 'string',
                },
            },
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
        {
            'title': 'country',
            'value': {'enabled': True},
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['rus'],
                    'arg_name': 'country',
                    'set_elem_type': 'string',
                },
            },
            'extension_method': 'replace',
            'is_paired_signal': False,
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)
async def test_balance_reports(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        billing_reports,
        fleet_transactions_api,
        folder_name,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == PARKS_REQUEST
        return PARKS_RESPONSE

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(
        load_json(f'{folder_name}/br_response_balance.json'),
    )
    fleet_transactions_api.set_folder(folder_name)

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json(f'{folder_name}/service_request.json'),
    )
    assert response.status_code == 200

    expected_json = load_json(f'{folder_name}/service_response.json')
    assert response.json() == expected_json


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.parametrize('folder_name', ['closing_documents'])
@pytest.mark.experiments3(filename='experiments3_closing_documents.json')
async def test_closing_documents(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        billing_reports,
        fleet_transactions_api,
        folder_name,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == PARKS_REQUEST
        return PARKS_RESPONSE

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    fleet_transactions_api.set_folder(folder_name)

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json(f'{folder_name}/service_request.json'),
    )
    assert response.status_code == 200

    expected_json = load_json(f'{folder_name}/service_response.json')
    assert response.json() == expected_json


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            id='old config value',
            marks=[
                pytest.mark.config(
                    DRIVER_BALANCE_PAYMENT_LINKS={
                        'park_id_0': 'https://pay.link/abcde/',
                    },
                ),
            ],
        ),
        pytest.param(
            id='new config value',
            marks=[
                pytest.mark.config(
                    DRIVER_BALANCE_PAYMENT_LINKS={
                        'park_id_0': (
                            'https://pay.link/abcde/?first_name={}&'
                            'last_name={}&email={}@pay.id&'
                            'readonly=first_name,last_name,email'
                        ),
                    },
                ),
            ],
        ),
    ],
)
async def test_balance_filtered_payment_link(
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        fleet_transactions_api,
        billing_reports,
        taxi_config,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert request.json == PARKS_REQUEST
        response = copy.deepcopy(PARKS_RESPONSE)
        response['parks'][0].pop('driver_partner_source')
        return response

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(load_json('all/br_response_balance.json'))
    fleet_transactions_api.set_folder('all')

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json('all/service_request.json'),
    )

    assert response.status_code == 200

    expected_url = (
        'https://pay.link/abcde/?'
        'first_name=Ivan&last_name=Ivanov&email=123456@pay.id&'
        'readonly=first_name,last_name,email'
    )
    url = response.json()['ui'][1]['payload']['url']
    assert url == expected_url


@pytest.mark.now('2020-01-16T21:30:00+0300')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_on_demand_payouts',
    consumers=['driver-money/context'],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.parametrize(
    'on_demand_available, payout_mode, pending_payment',
    [
        (True, 'on_demand', None),
        (True, 'on_demand', {'status': 'created'}),
        (
            True,
            'on_demand',
            {'status': 'pending', 'amount': '300', 'currency': 'RUB'},
        ),
        (False, 'on_demand', None),
        (True, 'regular', None),
        (
            True,
            'regular',
            {'status': 'pending', 'amount': '300', 'currency': 'RUB'},
        ),
    ],
)
async def test_on_demand_payouts_ui(
        on_demand_available,
        payout_mode,
        pending_payment,
        taxi_driver_money,
        load_json,
        mockserver,
        driver_authorizer,
        billing_reports,
        fleet_transactions_api,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        ret = copy.deepcopy(PARKS_RESPONSE)
        ret['parks'][0]['driver_partner_source'] = 'self_employed'
        return ret

    @mockserver.json_handler(
        '/fleet-payouts/internal/on-demand-payouts/v1/status',
    )
    def _mock_fleet_payouts(request):
        result = {
            'payout_mode': payout_mode,
            'payout_scheduled_at': '2020-01-26T10:00:00+00:00',
            'on_demand_available': on_demand_available,
        }
        if pending_payment:
            result.update({'pending_payment': pending_payment})
        return result

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/search')
    def _mock_payments(request):
        return {'payments': [], 'cursor': {}}

    def get_expected_icon_detail(pending_payment):
        result = {
            'left_icon': {'icon_type': 'flip'},
            'title': 'Обрабатываем выплату',
            'type': 'icon_detail',
        }
        if pending_payment['status'] == 'pending':
            result.update(
                {'title': 'Банк готовит перевод', 'detail': '300,00 ₽'},
            )
        return result

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')
    billing_reports.set_balances(load_json(f'all/br_response_balance.json'))
    fleet_transactions_api.set_folder('all')

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 9.20 (1234)',
            'Accept-Language': 'ru',
            'X-Driver-Session': 'driver_session',
        },
        params={'park_id': 'park_id_0'},
        json=load_json(f'all/service_request.json'),
    )
    button_enabled = on_demand_available

    assert response.status_code == 200
    ui_ = response.json()['ui']
    header_payload = ui_[0]['payload']
    assert header_payload == {
        'type': 'deeplink',
        'url': 'taximeter://screen/self_employed_withdrawals_settings',
    }
    if payout_mode == 'on_demand':
        button_index = 1
        if pending_payment is not None:
            button_index = 2
            icon_detail = ui_[1]
            assert icon_detail == get_expected_icon_detail(pending_payment)
        button = ui_[button_index]
        assert button['type'] == 'button'
        assert button['enabled'] == button_enabled
    else:
        assert ui_[1]['type'] != 'button'
