import pytest

ENDPOINT = '/fleet/payouts-web/v1/transactions/summary'

HEADERS = {
    'Accept-Language': 'ru,en;q=0.9,la;q=0.8',
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


BILLING_BANK_ORDERS_REQUEST = {'clid': 'clid', 'payment_id': '999'}

BILLING_BANK_ORDERS_RESPONSE = {
    'summary': [
        {
            'amount': '374',
            'contract': '124612/18',
            'currency': 'RUB',
            'product': 'ALFA',
        },
        {
            'amount': '-6344.05',
            'contract': '124612/18',
            'currency': 'RUB',
            'product': 'FUEL_FACT',
        },
        {
            'amount': '-6226.05',
            'contract': '124612/18',
            'currency': 'RUB',
            'product': 'FUEL_HOLD',
        },
        {
            'amount': '6344.05',
            'contract': '124612/18',
            'currency': 'RUB',
            'product': 'FUEL_HOLD_RETURN',
        },
        {
            'amount': '1758',
            'contract': '124612/18',
            'currency': 'RUB',
            'product': 'PAYCASH',
        },
        {
            'amount': '704',
            'contract': '124612/18',
            'currency': 'RUB',
            'product': 'PAYTURE',
        },
        {
            'amount': '28465',
            'contract': '124612/18',
            'currency': 'RUB',
            'product': 'SBERBANK',
        },
        {
            'amount': '1164',
            'contract': '124612/18',
            'currency': 'RUB',
            'product': 'VTB',
        },
        {
            'amount': '1',
            'contract': '124612/18',
            'currency': 'RUB',
            'product': 'YA_COMPENSATION',
        },
        {
            'amount': '-12014.64',
            'contract': '124612/18',
            'currency': 'RUB',
            'product': 'YA_NETTING',
        },
        {
            'amount': '-144.86',
            'contract': '124612/18',
            'currency': 'RUB',
            'detailed_product': 'comission',
            'product': 'FUEL_FACT',
        },
        {
            'amount': '144.86',
            'contract': '124612/18',
            'currency': 'RUB',
            'detailed_product': 'comission',
            'product': 'FUEL_HOLD_RETURN',
        },
        {
            'amount': '158.15',
            'contract': '124612/18',
            'currency': 'RUB',
            'detailed_product': 'tips',
            'product': 'SBERBANK',
        },
        {
            'amount': '15.25',
            'contract': '124612/18',
            'currency': 'RUB',
            'detailed_product': 'tips',
            'product': 'VTB',
        },
        {
            'amount': '13720.27',
            'contract': 'ОФ-124612/18',
            'currency': 'RUB',
            'product': 'YA_PROMOCODES',
        },
        {
            'amount': '4761',
            'contract': 'РАС-115660',
            'currency': 'RUB',
            'product': 'YA_CORPORATE',
        },
    ],
}

SERVICE_REQUEST = {'payment_id': '999'}

SERVICE_RESPONSE = {
    'items': [
        {
            'contract': '124612/18',
            'categories': [
                {
                    'category': {'id': 'cashless', 'name': 'Оплата по карте'},
                    'amount': '32465.00',
                    'currency': 'RUB',
                },
                {
                    'category': {'id': 'compensation', 'name': 'Компенсация'},
                    'amount': '1.00',
                    'currency': 'RUB',
                },
                {
                    'category': {
                        'id': 'gas_station',
                        'name': 'Прочее: заправка',
                    },
                    'amount': '-6226.05',
                    'currency': 'RUB',
                },
                {
                    'category': {'id': 'netting', 'name': 'Взаимозачёт'},
                    'amount': '-12014.64',
                    'currency': 'RUB',
                },
                {
                    'category': {'id': 'tips', 'name': 'Чаевые'},
                    'amount': '173.40',
                    'currency': 'RUB',
                },
            ],
        },
        {
            'contract': 'ОФ-124612/18',
            'categories': [
                {
                    'category': {'id': 'promocodes', 'name': 'Промокод'},
                    'amount': '13720.27',
                    'currency': 'RUB',
                },
            ],
        },
        {
            'contract': 'РАС-115660',
            'categories': [
                {
                    'category': {
                        'id': 'corporate',
                        'name': 'Корпоративная оплата',
                    },
                    'amount': '4761.00',
                    'currency': 'RUB',
                },
            ],
        },
    ],
}

TRANSLATIONS = {
    'category_cashless': {'ru': 'Оплата по карте'},
    'category_tips': {'ru': 'Чаевые'},
    'category_gas_station': {'ru': 'Прочее: заправка'},
    'category_compensation': {'ru': 'Компенсация'},
    'category_corporate': {'ru': 'Корпоративная оплата'},
    'category_netting': {'ru': 'Взаимозачёт'},
    'category_promocodes': {'ru': 'Промокод'},
}


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=TRANSACTION_PRODUCTS,
)
@pytest.mark.translations(opteum_page_report_payouts=TRANSLATIONS)
async def test_success(taxi_fleet_payouts_web, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        assert request.json == FLEET_PARKS_REQUEST
        return FLEET_PARKS_RESPONSE

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/summary')
    async def _payments_details(request):
        assert request.json == BILLING_BANK_ORDERS_REQUEST
        return BILLING_BANK_ORDERS_RESPONSE

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
