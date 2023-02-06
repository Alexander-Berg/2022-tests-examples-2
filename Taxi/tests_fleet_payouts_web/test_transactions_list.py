import copy

import pytest

ENDPOINT = '/fleet/payouts-web/v1/transactions/list'

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': 'park_id',
}

TRANSACTION_PRODUCTS = [
    {
        'category_id': 'cashless',
        'products': [
            {'product': 'ALFA'},
            {'product': 'BRAINTREE'},
            {'product': 'CARDPAY'},
            {'product': 'ECOMMPAY'},
            {'product': 'KASSANOVA'},
            {'product': 'OPEN'},
            {'product': 'PAYBOX'},
            {'product': 'PAYCASH'},
            {'product': 'PAYTURE'},
            {'product': 'SBERBANK'},
            {'product': 'VTB'},
            {'product': 'RBK_MONEY'},
        ],
        'tanker_key': 'category_cashless',
    },
    {
        'category_id': 'tips',
        'products': [
            {'product': 'ECOMMPAY_AZ', 'product_details': 'tips'},
            {'product': 'ALFA', 'product_details': 'tips'},
            {'product': 'BRAINTREE', 'product_details': 'tips'},
            {'product': 'CARDPAY', 'product_details': 'tips'},
            {'product': 'ECOMMPAY', 'product_details': 'tips'},
            {'product': 'KASSANOVA', 'product_details': 'tips'},
            {'product': 'OPEN', 'product_details': 'tips'},
            {'product': 'PAYBOX', 'product_details': 'tips'},
            {'product': 'PAYCASH', 'product_details': 'tips'},
            {'product': 'PAYTURE', 'product_details': 'tips'},
            {'product': 'SBERBANK', 'product_details': 'tips'},
            {'product': 'VTB', 'product_details': 'tips'},
            {'product': 'RBK_MONEY', 'product_details': 'tips'},
        ],
        'tanker_key': 'category_tips',
    },
    {
        'category_id': 'gas_station',
        'products': [
            {'product': 'CORRECTION_FUEL_HOLD'},
            {'product': 'FUEL_FACT'},
            {'product': 'FUEL_FACT', 'product_details': 'comission'},
            {'product': 'FUEL_HOLD'},
            {'product': 'FUEL_HOLD_PAYMENT'},
            {'product': 'FUEL_HOLD_RETURN'},
            {'product': 'FUEL_HOLD_RETURN', 'product_details': 'comission'},
        ],
        'tanker_key': 'category_gas_station',
    },
    {
        'category_id': 'compensation',
        'products': [{'product': 'YA_COMPENSATION'}],
        'tanker_key': 'category_compensation',
    },
    {
        'category_id': 'corporate',
        'products': [
            {'product': 'YA_CORPORATE'},
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'client_b2b_trip_payment',
                'product_details': 'client_b2b_trip_payment',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'client_b2b_trip_payment',
                'product_details': 'decoupling_b2b_trip_payment',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'client_b2b_trip_payment',
                'product_details': 'multi_client_b2b_trip_payment',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'park_b2b_trip_payment',
                'product_details': 'park_b2b_trip_payment',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'park_b2b_trip_payment',
                'product_details': 'multi_park_b2b_trip_payment',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'park_b2b_trip_payment',
                'product_details': 'park_b2b_trip_payment_test',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'park_b2b_trip_payment',
                'product_details': 'rebate_b2b_trip_payment',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'park_b2b_trip_payment',
                'product_details': 'rebate_b2b_trip_payment_test',
            },
            {'product': 'food_payment', 'product_details': 'food_payment'},
            {
                'product': 'client_b2b_drive_payment',
                'product_details': 'client_b2b_drive_payment',
            },
        ],
        'tanker_key': 'category_corporate',
    },
    {
        'category_id': 'netting',
        'products': [
            {'product': 'YA_NETTING'},
            {'product': 'CORRECTION_NETTING'},
        ],
        'tanker_key': 'category_netting',
    },
    {
        'category_id': 'promocodes',
        'products': [
            {'product': 'YA_PROMOCODES'},
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'coupon',
                'product_details': 'coupon_personal_wallet',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'coupon',
                'product_details': 'user_marketing_coupon_compensation',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'coupon',
                'product_details': 'user_support_coupon_compensation',
            },
            {'product': 'coupon_plus', 'product_details': 'coupon_plus'},
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'order',
                'product_details': 'driver_workshift_coupon',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'order',
                'product_details': 'driver_marketing_coupon_compensation',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'order',
                'product_details': 'driver_support_coupon_compensation',
            },
            {
                'additional_prefixes': ['cargo', 'delivery'],
                'product': 'order',
                'product_details': 'fee_branding_chargeback',
            },
        ],
        'tanker_key': 'category_promocodes',
    },
    {
        'category_id': 'scouts',
        'products': [
            {'product': 'YA_SCOUTS'},
            {
                'additional_prefixes': ['cargo'],
                'product': 'scout',
                'product_details': 'scout',
            },
            {
                'additional_prefixes': ['cargo'],
                'product': 'scout_sz',
                'product_details': 'scout_sz',
            },
        ],
        'tanker_key': 'category_scouts',
    },
]

FLEET_PARKS_REQUEST = {'query': {'park': {'ids': ['park_id']}}}

FLEET_PARKS_RESPONSE = {
    'parks': [
        {
            'city_id': 'Москва',
            'country_id': 'rus',
            'demo_mode': False,
            'driver_hiring': {
                'park_email': 'test@mail.ru',
                'park_phone': '+7 (000) 999-99-99',
            },
            'has_pay_systems_integration': False,
            'id': 'park_id',
            'integration_events': [
                'carstatus',
                'orderstatus',
                'card_payments',
                'requestcar',
                'setcar_on_requestconfirm',
            ],
            'is_active': True,
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'locale': 'ru',
            'login': 'лещ1',
            'name': 'Sea bream',
            'org_name': 'ИП Прудников',
            'owner': 'antipovav',
            'provider_config': {'clid': 'clid', 'type': 'production'},
            'providers': ['yandex', 'park'],
            'specifications': ['taxi'],
            'tz_offset': 3,
            'ui_mode': 'default',
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
    ],
}


BILLING_BANK_ORDERS_REQUEST = {
    'clid': 'clid',
    'limit': 25,
    'payment_id': '999',
}

BILLING_BANK_ORDERS_RESPONSE = {
    'cursor': 'cursor',
    'order_number': '137',
    'payment_id': '999',
    'transactions': [
        {
            'agreement': 'contract_id1',
            'alias_id': 'order_id1',
            'credited_amount': '1',
            'currency': 'RUB',
            'driver_details': {'db_id': 'park_id', 'uuid': 'driver_id1'},
            'orig_amount': '1',
            'payment_id': 999,
            'product': 'YA_CORPORATE',
            'transaction_id': 'transaction_id1',
            'transaction_time': '2020-02-28T00:00:00+03:00',
        },
        {
            'agreement': 'contract_id1',
            'alias_id': 'order_id2',
            'credited_amount': '2',
            'currency': 'RUB',
            'driver_details': {'db_id': 'park_id', 'uuid': 'driver_id1'},
            'orig_amount': '2',
            'payment_id': 999,
            'product': 'SUPER_UNKNOWN',
            'transaction_id': 'transaction_id2',
            'transaction_time': '2020-02-28T00:00:00+03:00',
        },
        {
            'agreement': 'contract_id1',
            'alias_id': 'order_id3',
            'credited_amount': '3',
            'currency': 'RUB',
            'driver_details': {},
            'orig_amount': '3',
            'payment_id': 999,
            'product': 'YA_CORPORATE',
            'transaction_id': 'transaction_id3',
            'transaction_time': '2020-03-01T00:00:00+03:00',
        },
        {
            'agreement': 'contract_id2',
            'alias_id': 'order_id4',
            'credited_amount': '4',
            'currency': 'RUB',
            'driver_details': {'db_id': 'park_id', 'uuid': 'driver_id2'},
            'orig_amount': '4',
            'payment_id': 999,
            'product': 'FUEL_HOLD_RETURN',
            'product_details': 'comission',
            'transaction_id': 'transaction_id4',
            'transaction_time': '2020-02-28T00:00:00+03:00',
        },
        {
            'agreement': 'contract_id2',
            'alias_id': 'order_id1',
            'credited_amount': '5',
            'currency': 'RUB',
            'driver_details': {},
            'orig_amount': '5',
            'payment_id': 999,
            'product': 'FUEL_FACT',
            'transaction_id': 'transaction_id5',
            'transaction_time': '2020-03-01T00:00:00+03:00',
        },
    ],
}

DRIVER_PROFILES_REQUEST = {
    'id_in_set': ['park_id_driver_id2', 'park_id_driver_id1'],
    'projection': ['data.full_name', 'data.park_id'],
}

DRIVER_PROFILES_RESPONSE = {
    'profiles': [
        {'park_driver_profile_id': 'park_id_driver_id2'},
        {
            'data': {
                'full_name': {
                    'first_name': 'f',
                    'last_name': 'l',
                    'middle_name': 'm',
                },
                'park_id': '12345',
            },
            'park_driver_profile_id': 'park_id_driver_id1',
        },
    ],
}

SERVICE_REQUEST = {'limit': 25, 'payment_id': '999'}

SERVICE_RESPONSE = {
    'cursor': 'cursor',
    'order_number': '137',
    'transactions': [
        {
            'amount': '1',
            'contract_id': 'contract_id1',
            'currency': 'RUB',
            'order_id': 'order_id1',
            'transaction_id': 'transaction_id1',
            'driver': {
                'first_name': 'f',
                'id': 'driver_id1',
                'last_name': 'l',
                'middle_name': 'm',
                'park_id': '12345',
            },
            'transaction_type': 'corporate',
        },
        {
            'amount': '2',
            'contract_id': 'contract_id1',
            'currency': 'RUB',
            'order_id': 'order_id2',
            'transaction_id': 'transaction_id2',
            'driver': {
                'first_name': 'f',
                'id': 'driver_id1',
                'last_name': 'l',
                'middle_name': 'm',
                'park_id': '12345',
            },
            'transaction_type': 'other',
        },
        {
            'amount': '3',
            'contract_id': 'contract_id1',
            'currency': 'RUB',
            'order_id': 'order_id3',
            'transaction_id': 'transaction_id3',
            'transaction_type': 'corporate',
        },
        {
            'amount': '4',
            'contract_id': 'contract_id2',
            'currency': 'RUB',
            'order_id': 'order_id4',
            'transaction_id': 'transaction_id4',
            'transaction_type': 'gas_station',
        },
        {
            'amount': '5',
            'contract_id': 'contract_id2',
            'currency': 'RUB',
            'order_id': 'order_id1',
            'transaction_id': 'transaction_id5',
            'transaction_type': 'gas_station',
        },
    ],
}


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=TRANSACTION_PRODUCTS,
)
async def test_success(taxi_fleet_payouts_web, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/details')
    async def _payments_details(request):
        assert request.json == BILLING_BANK_ORDERS_REQUEST
        return BILLING_BANK_ORDERS_RESPONSE

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _retrieve(request):
        assert request.query == {'consumer': 'fleet-payouts-web'}
        assert request.json == DRIVER_PROFILES_REQUEST
        return DRIVER_PROFILES_RESPONSE

    response = await taxi_fleet_payouts_web.post(
        ENDPOINT, headers=HEADERS, json=SERVICE_REQUEST,
    )

    assert response.status == 200
    assert response.json() == SERVICE_RESPONSE


@pytest.mark.config(OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=[])
async def test_empty_config(taxi_fleet_payouts_web):

    response = await taxi_fleet_payouts_web.post(
        ENDPOINT, headers=HEADERS, json=SERVICE_REQUEST,
    )

    assert response.status == 500


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=TRANSACTION_PRODUCTS,
)
async def test_filter_category_ids(taxi_fleet_payouts_web, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    billing_bank_orders_request = copy.deepcopy(BILLING_BANK_ORDERS_REQUEST)
    billing_bank_orders_request['filter'] = {
        'product': [
            {'product': 'CORRECTION_FUEL_HOLD'},
            {'product': 'FUEL_FACT'},
            {'detailed_product': 'comission', 'product': 'FUEL_FACT'},
            {'product': 'FUEL_HOLD'},
            {'product': 'FUEL_HOLD_PAYMENT'},
            {'product': 'FUEL_HOLD_RETURN'},
            {'detailed_product': 'comission', 'product': 'FUEL_HOLD_RETURN'},
        ],
    }

    billing_bank_orders_response = copy.deepcopy(BILLING_BANK_ORDERS_RESPONSE)
    transactions = [
        x
        for x in billing_bank_orders_response['transactions']
        if x['transaction_id'] in ['transaction_id4', 'transaction_id5']
    ]
    billing_bank_orders_response['transactions'] = transactions

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/details')
    async def _payments_details(request):
        assert request.json == billing_bank_orders_request
        return billing_bank_orders_response

    driver_profiles_request = copy.deepcopy(DRIVER_PROFILES_REQUEST)
    driver_profiles_request['id_in_set'] = [
        x
        for x in driver_profiles_request['id_in_set']
        if x in ['park_id_driver_id2']
    ]

    driver_profiles_response = copy.deepcopy(DRIVER_PROFILES_RESPONSE)
    driver_profiles_response['profiles'] = [
        x
        for x in driver_profiles_response['profiles']
        if x['park_driver_profile_id'] in ['park_id_driver_id2']
    ]

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _retrieve(request):
        assert request.query == {'consumer': 'fleet-payouts-web'}
        assert request.json == driver_profiles_request
        return driver_profiles_response

    service_request = copy.deepcopy(SERVICE_REQUEST)
    service_request['category_ids'] = ['gas_station']

    response = await taxi_fleet_payouts_web.post(
        ENDPOINT, headers=HEADERS, json=service_request,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    transactions = [
        x
        for x in service_response['transactions']
        if x['transaction_id'] in ['transaction_id4', 'transaction_id5']
    ]
    service_response['transactions'] = transactions

    assert response.status == 200
    assert response.json() == service_response


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=TRANSACTION_PRODUCTS,
)
async def test_filter_alias_ids(taxi_fleet_payouts_web, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    billing_bank_orders_request = copy.deepcopy(BILLING_BANK_ORDERS_REQUEST)
    billing_bank_orders_request['filter'] = {
        'alias_id': ['order_id1', 'order_id77'],
    }

    billing_bank_orders_response = copy.deepcopy(BILLING_BANK_ORDERS_RESPONSE)
    transactions = [
        x
        for x in billing_bank_orders_response['transactions']
        if x['transaction_id'] in ['transaction_id1', 'transaction_id5']
    ]
    billing_bank_orders_response['transactions'] = transactions

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/details')
    async def _payments_details(request):
        assert request.json == billing_bank_orders_request
        return billing_bank_orders_response

    driver_profiles_request = copy.deepcopy(DRIVER_PROFILES_REQUEST)
    driver_profiles_request['id_in_set'] = [
        x
        for x in driver_profiles_request['id_in_set']
        if x in ['park_id_driver_id1']
    ]

    driver_profiles_response = copy.deepcopy(DRIVER_PROFILES_RESPONSE)
    driver_profiles_response['profiles'] = [
        x
        for x in driver_profiles_response['profiles']
        if x['park_driver_profile_id'] in ['park_id_driver_id1']
    ]

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _retrieve(request):
        assert request.query == {'consumer': 'fleet-payouts-web'}
        assert request.json == driver_profiles_request
        return driver_profiles_response

    service_request = copy.deepcopy(SERVICE_REQUEST)
    service_request['alias_ids'] = ['order_id1', 'order_id77']

    response = await taxi_fleet_payouts_web.post(
        ENDPOINT, headers=HEADERS, json=service_request,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    transactions = [
        x
        for x in service_response['transactions']
        if x['transaction_id'] in ['transaction_id1', 'transaction_id5']
    ]
    service_response['transactions'] = transactions

    assert response.status == 200
    assert response.json() == service_response


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=TRANSACTION_PRODUCTS,
)
async def test_filter_driver_ids(taxi_fleet_payouts_web, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    billing_bank_orders_request = copy.deepcopy(BILLING_BANK_ORDERS_REQUEST)
    billing_bank_orders_request['filter'] = {
        'driver': ['driver_id1', 'driver_id77'],
    }

    billing_bank_orders_response = copy.deepcopy(BILLING_BANK_ORDERS_RESPONSE)
    transactions = [
        x
        for x in billing_bank_orders_response['transactions']
        if x['transaction_id'] in ['transaction_id1', 'transaction_id2']
    ]
    billing_bank_orders_response['transactions'] = transactions

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/details')
    async def _payments_details(request):
        assert request.json == billing_bank_orders_request
        return billing_bank_orders_response

    driver_profiles_request = copy.deepcopy(DRIVER_PROFILES_REQUEST)
    driver_profiles_request['id_in_set'] = [
        x
        for x in driver_profiles_request['id_in_set']
        if x in ['park_id_driver_id1']
    ]

    driver_profiles_response = copy.deepcopy(DRIVER_PROFILES_RESPONSE)
    driver_profiles_response['profiles'] = [
        x
        for x in driver_profiles_response['profiles']
        if x['park_driver_profile_id'] in ['park_id_driver_id1']
    ]

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _retrieve(request):
        assert request.query == {'consumer': 'fleet-payouts-web'}
        assert request.json == driver_profiles_request
        return driver_profiles_response

    service_request = copy.deepcopy(SERVICE_REQUEST)
    service_request['driver_ids'] = ['driver_id1', 'driver_id77']

    response = await taxi_fleet_payouts_web.post(
        ENDPOINT, headers=HEADERS, json=service_request,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    transactions = [
        x
        for x in service_response['transactions']
        if x['transaction_id'] in ['transaction_id1', 'transaction_id2']
    ]
    service_response['transactions'] = transactions

    assert response.status == 200
    assert response.json() == service_response


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=TRANSACTION_PRODUCTS,
)
async def test_filter_contract_ids(taxi_fleet_payouts_web, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    billing_bank_orders_request = copy.deepcopy(BILLING_BANK_ORDERS_REQUEST)
    billing_bank_orders_request['filter'] = {
        'contract': ['contract_id2', 'contract_id77'],
    }

    billing_bank_orders_response = copy.deepcopy(BILLING_BANK_ORDERS_RESPONSE)
    transactions = [
        x
        for x in billing_bank_orders_response['transactions']
        if x['transaction_id'] in ['transaction_id4', 'transaction_id5']
    ]
    billing_bank_orders_response['transactions'] = transactions

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/details')
    async def _payments_details(request):
        assert request.json == billing_bank_orders_request
        return billing_bank_orders_response

    driver_profiles_request = copy.deepcopy(DRIVER_PROFILES_REQUEST)
    driver_profiles_request['id_in_set'] = [
        x
        for x in driver_profiles_request['id_in_set']
        if x in ['park_id_driver_id2']
    ]

    driver_profiles_response = copy.deepcopy(DRIVER_PROFILES_RESPONSE)
    driver_profiles_response['profiles'] = [
        x
        for x in driver_profiles_response['profiles']
        if x['park_driver_profile_id'] in ['park_id_driver_id2']
    ]

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _retrieve(request):
        assert request.query == {'consumer': 'fleet-payouts-web'}
        assert request.json == driver_profiles_request
        return driver_profiles_response

    service_request = copy.deepcopy(SERVICE_REQUEST)
    service_request['contract_ids'] = ['contract_id2', 'contract_id77']

    response = await taxi_fleet_payouts_web.post(
        ENDPOINT, headers=HEADERS, json=service_request,
    )

    service_response = copy.deepcopy(SERVICE_RESPONSE)
    transactions = [
        x
        for x in service_response['transactions']
        if x['transaction_id'] in ['transaction_id4', 'transaction_id5']
    ]
    service_response['transactions'] = transactions

    assert response.status == 200
    assert response.json() == service_response
