import pytest

from tests_contractor_balances import utils

PARK_ID = 'park1'
ENTRY_ID = 8484848484
ORDER_ID = 'order1'
MOCK_NOW = '2021-09-28T19:31:00+00:00'

CURRENCY_RUB = 'RUB'
CURRENCY_ILS = 'ILS'

CURRENCY_MAP = {CURRENCY_RUB: '₽', CURRENCY_ILS: '₪'}


def _make_stq_args(
        agreement_id, sub_account, amount, currency, order_id, event_at,
):
    return {
        'park_id': PARK_ID,
        'transactions': [
            {
                'entry_id': ENTRY_ID,
                'account': {
                    'agreement_id': agreement_id,
                    'sub_account': sub_account,
                    'currency': currency,
                },
                'amount': amount,
                'event_at': event_at,
                'details': {'alias_id': order_id},
            },
        ],
    }


def _make_driver_order_messages_request(order_id, brand_name, message, date):
    return {
        'park_id': PARK_ID,
        'order_id': order_id,
        'user_name': brand_name,
        'date': date,
        'message': message,
    }


TEST_ORDER_MESSAGE_PARAMS = [
    (  # locale en
        'taxi/yandex_ride',
        'card',
        '1',
        CURRENCY_RUB,
        MOCK_NOW,
        'order1',
        None,
        'en',
        'aze',
        'Uber',
        f'Payment 1.00 {CURRENCY_MAP[CURRENCY_RUB]}',
    ),
    (  # locale ru
        'taxi/yandex_ride',
        'card',
        '2',
        CURRENCY_RUB,
        MOCK_NOW,
        'order2',
        None,
        'ru',
        'rus',
        'Яндекс',
        f'Оплата 2,00 {CURRENCY_MAP[CURRENCY_RUB]}',
    ),
    (  # park country not found in config -> default brand
        'taxi/yandex_ride',
        'tips',
        '3',
        CURRENCY_ILS,
        MOCK_NOW,
        'order3',
        'uberdriver',
        'en',
        'kaz',
        'Yango',
        f'Tips 3.00 {CURRENCY_MAP[CURRENCY_ILS]}',
    ),
    (  # brand found in config by country, not by fleet_type -> default brand
        'taxi/yandex_ride',
        'tips',
        '4',
        CURRENCY_ILS,
        MOCK_NOW,
        'order4',
        'uberdriver',
        'en',
        'tur',
        'Yango',
        f'Tips 4.00 {CURRENCY_MAP[CURRENCY_ILS]}',
    ),
    (  # brand found in config by country and by fleet_type
        'taxi/yandex_ride',
        'tips',
        '5',
        CURRENCY_ILS,
        MOCK_NOW,
        'order5',
        'uberdriver',
        'en',
        'ils',
        'Uber',
        f'Tips 5.00 {CURRENCY_MAP[CURRENCY_ILS]}',
    ),
    (  # brand found in config by country, no fleet_type in config
        'taxi/yandex_ride',
        'tips',
        '6',
        CURRENCY_ILS,
        MOCK_NOW,
        'order6',
        None,
        'en',
        'aze',
        'Uber',
        f'Tips 6.00 {CURRENCY_MAP[CURRENCY_ILS]}',
    ),
    (  # found two brands by country, brand with matched fleet_type
        'taxi/yandex_ride',
        'tips',
        '6',
        CURRENCY_ILS,
        MOCK_NOW,
        'order6',
        'uberdriver',
        'en',
        'ils',
        'Uber',
        f'Tips 6.00 {CURRENCY_MAP[CURRENCY_ILS]}',
    ),
    (  # found two brands by country, brand with no fleet_type
        'taxi/yandex_ride',
        'tips',
        '6',
        CURRENCY_ILS,
        MOCK_NOW,
        'order6',
        None,
        'en',
        'ils',
        'Yandex',
        f'Tips 6.00 {CURRENCY_MAP[CURRENCY_ILS]}',
    ),
    (  # event_at other than MOCK_NOW
        'taxi/yandex_ride',
        'tips',
        '7',
        CURRENCY_ILS,
        '2021-09-21T19:31:00+00:00',
        'order7',
        'uberdriver',
        'en',
        'ils',
        'Uber',
        f'Tips 7.00 {CURRENCY_MAP[CURRENCY_ILS]}',
    ),
    (  # order id missing
        'taxi/yandex_ride',
        'tips',
        '8',
        CURRENCY_ILS,
        MOCK_NOW,
        None,
        None,
        None,
        None,
        None,
        None,
    ),
    (  # negative amount
        'taxi/yandex_ride',
        'tips',
        '-9',
        CURRENCY_ILS,
        MOCK_NOW,
        'order9',
        'uberdriver',
        'ru',
        'ils',
        None,
        None,
    ),
    (  # formatted positive amount equal zero
        'taxi/yandex_ride',
        'tips',
        '0.001',
        CURRENCY_ILS,
        MOCK_NOW,
        'order10',
        None,
        'en',
        'ils',
        None,
        None,
    ),
    (  # formatted negative amount equal zero
        'taxi/yandex_ride',
        'card',
        '-0.001',
        CURRENCY_RUB,
        MOCK_NOW,
        'order11',
        None,
        'en',
        'rus',
        None,
        None,
    ),
    (  # order message disabled by config
        'commission',
        'subsidy',
        '7',
        CURRENCY_RUB,
        MOCK_NOW,
        'order12',
        'uberdriver',
        'en',
        'rus',
        None,
        None,
    ),
    (  # agreement or subaccount missing in config
        'unknown',
        'subsidy',
        '8',
        CURRENCY_RUB,
        MOCK_NOW,
        'order13',
        'uberdriver',
        'en',
        'rus',
        None,
        None,
    ),
]


@pytest.mark.parametrize(
    (
        'agreement_id',
        'sub_account',
        'amount',
        'currency',
        'event_at',
        'order_id',
        'fleet_type',
        'locale',
        'country_id',
        'brand',
        'message',
    ),
    TEST_ORDER_MESSAGE_PARAMS,
)
async def test_order_message(
        mockserver,
        stq_runner,
        parks_list_context,
        mock_parks_list,
        agreement_id,
        sub_account,
        amount,
        currency,
        event_at,
        order_id,
        fleet_type,
        locale,
        country_id,
        brand,
        message,
):
    parks_list_context.set_data(
        country_id=country_id, locale=locale, fleet_type=fleet_type,
    )

    @mockserver.json_handler('/driver-order-messages/v1/messages/add')
    def mock_driver_order_messages(request):
        assert request.headers['X-Idempotency-Token'] == utils.make_sha1(
            f'{PARK_ID}{order_id}{ENTRY_ID}',
        )
        assert request.json == (
            _make_driver_order_messages_request(
                order_id, brand, message, event_at,
            )
        )
        return {}

    await stq_runner.contractor_balances_order_messages.call(
        task_id='task1',
        kwargs=_make_stq_args(
            agreement_id, sub_account, amount, currency, order_id, event_at,
        ),
    )
    assert mock_parks_list.has_calls == (order_id is not None)
    assert mock_driver_order_messages.has_calls == (message is not None)


@pytest.mark.parametrize(
    ('config_date', 'event_at', 'expect_message'),
    [
        ('2020-01-01T00:00:00+00:00', '2021-01-01T00:00:00+00:00', True),
        ('2021-01-01T00:00:00+00:00', '2021-01-01T00:00:00+00:00', True),
        ('2021-01-01T00:00:00+00:00', '2020-01-01T00:00:00+00:00', False),
    ],
)
async def test_order_message_enabled_date_config(
        taxi_config,
        mockserver,
        stq_runner,
        mock_parks_list,
        config_date,
        event_at,
        expect_message,
):
    taxi_config.set(CONTRACTOR_BALANCES_ORDER_MESSAGE_ENABLED_DATE=config_date)

    @mockserver.json_handler('/driver-order-messages/v1/messages/add')
    def mock_driver_order_messages(request):
        return {}

    await stq_runner.contractor_balances_order_messages.call(
        task_id='task1',
        kwargs=_make_stq_args(
            'taxi/yandex_ride', 'card', '1', 'rub', 'o1', event_at,
        ),
    )
    assert mock_driver_order_messages.has_calls == expect_message


@pytest.mark.parametrize('expect_fail', [True, False])
async def test_driver_order_message_fail(
        mockserver,
        stq_runner,
        parks_list_context,
        mock_parks_list,
        expect_fail,
):
    parks_list_context.set_data(
        country_id='aze', locale='en', fleet_type='Uber',
    )

    @mockserver.json_handler('/driver-order-messages/v1/messages/add')
    def mock_driver_order_messages(request):
        return mockserver.make_response(status=500) if expect_fail else {}

    await stq_runner.contractor_balances_order_messages.call(
        task_id='task1',
        kwargs=_make_stq_args(
            'taxi/yandex_ride', 'card', '1', CURRENCY_RUB, 'order1', MOCK_NOW,
        ),
        expect_fail=expect_fail,
    )

    assert mock_driver_order_messages.has_calls
