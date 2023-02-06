import pytest

ENDPOINT = '/fleet/payouts-web/v1/transactions/categories'

HEADERS = {
    'Accept-Language': 'ru,en;q=0.9,la;q=0.8',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
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
    {'category_id': 'super_cat', 'products': []},
]


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=TRANSACTION_PRODUCTS,
)
@pytest.mark.translations(
    opteum_page_report_payouts={
        'category_cashless': {'ru': 'Безнал'},
        'category_tips': {'ru': 'Чаевые'},
        'category_gas_station': {'ru': 'Заправка'},
        'category_compensation': {'ru': 'Компенсация'},
        'category_corporate': {'ru': 'Корпоративный'},
        'category_netting': {'ru': 'Взаимозачет'},
        'category_promocodes': {'ru': 'Промокоды'},
        'category_scouts': {'ru': 'Скауты'},
        'category_other': {'ru': 'Прочее'},
    },
)
async def test_success(taxi_fleet_payouts_web):
    response = await taxi_fleet_payouts_web.get(ENDPOINT, headers=HEADERS)

    assert response.status == 200
    assert response.json() == {
        'items': [
            {
                'id': 'cashless',
                'name': 'Безнал',
                'is_enabled_for_filtering': True,
            },
            {'id': 'tips', 'name': 'Чаевые', 'is_enabled_for_filtering': True},
            {
                'id': 'gas_station',
                'name': 'Заправка',
                'is_enabled_for_filtering': True,
            },
            {
                'id': 'compensation',
                'name': 'Компенсация',
                'is_enabled_for_filtering': True,
            },
            {
                'id': 'corporate',
                'name': 'Корпоративный',
                'is_enabled_for_filtering': True,
            },
            {
                'id': 'netting',
                'name': 'Взаимозачет',
                'is_enabled_for_filtering': True,
            },
            {
                'id': 'promocodes',
                'name': 'Промокоды',
                'is_enabled_for_filtering': True,
            },
            {
                'id': 'scouts',
                'name': 'Скауты',
                'is_enabled_for_filtering': True,
            },
            {
                'id': 'super_cat',
                'name': 'super_cat',
                'is_enabled_for_filtering': True,
            },
            {
                'id': 'other',
                'name': 'Прочее',
                'is_enabled_for_filtering': False,
            },
        ],
    }


@pytest.mark.config(OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=[])
async def test_empty_config(taxi_fleet_payouts_web):
    response = await taxi_fleet_payouts_web.get(ENDPOINT, headers=HEADERS)

    assert response.status == 500
