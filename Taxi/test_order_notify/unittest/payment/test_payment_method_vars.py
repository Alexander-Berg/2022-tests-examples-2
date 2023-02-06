import typing

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.order_info import OrderData
from order_notify.repositories.payment import payment_method


PATH = 'ride_report.html_body'


@pytest.fixture(name='mock_functions')
def mock_payment_vars_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.get_payment_icon = Counter()
            self.get_payment_phrase = Counter()

    counters = Counters()

    @patch('order_notify.repositories.payment.payment_method.get_payment_icon')
    def _get_payment_icon(
            context: stq_context.Context,
            payment_type: str,
            card_system: typing.Optional[str],
    ) -> str:
        counters.get_payment_icon.call()
        assert payment_type in ('cash', 'card', 'corp')
        if payment_type != 'card':
            return payment_type
        if not card_system:
            return ''
        assert card_system == '<system>'
        return 'card'

    @patch(
        'order_notify.repositories.payment.payment_method.'
        'get_payment_phrase',
    )
    def _get_payment_phrase(
            context: stq_context.Context,
            payment_type: str,
            card_number: typing.Optional[str],
            locale: str,
            brand: str,
    ) -> str:
        counters.get_payment_phrase.call()
        assert locale == 'ru'
        if payment_type == 'card' and not card_number:
            return payment_type + '-'
        return payment_type + '+'

    return counters


@pytest.fixture(name='mock_server')
def mock_driver_trackstory_fixture(mockserver, load_json):
    @mockserver.json_handler('/cardstorage/v1/card')
    async def handler(request):
        query = request.json
        assert query['yandex_uid'] == '0'
        assert query['card_id'] in ('2', '3')
        if query['card_id'] == '3':
            return {
                'card_id': '3',
                'billing_card_id': '<billing_card_id>',
                'permanent_card_id': '<permanent_card_id>',
                'currency': 'RUB',
                'expiration_month': 1,
                'expiration_year': 2020,
                'number': '12349873',
                'owner': '<owner>',
                'possible_moneyless': False,
                'region_id': '<region_id>',
                'regions_checked': [],
                'system': '<system>',
                'valid': True,
                'bound': True,
                'unverified': False,
                'busy': False,
                'busy_with': [],
                'from_db': True,
            }
        return mockserver.make_response(
            json={'code': '404', 'message': 'Not Found'}, status=404,
        )

    return handler


@pytest.mark.parametrize(
    'main_card_payment_id, payment_type, expected_vars',
    [
        pytest.param(
            '1',
            'cash',
            {
                'payment_icon': 'cash',
                'payment_phrase': 'cash+',
                'payment_method_corp': False,
                'payment_method_card': False,
            },
            id='cash',
        ),
        pytest.param(
            '2',
            'card',
            {
                'payment_icon': '',
                'payment_phrase': 'card-',
                'payment_method_corp': False,
                'payment_method_card': True,
            },
            id='cant_find_card',
        ),
        pytest.param(
            '3',
            'card',
            {
                'payment_icon': 'card',
                'payment_phrase': 'card+',
                'payment_method_corp': False,
                'payment_method_card': True,
            },
            id='can_find_card',
        ),
        pytest.param(
            '4',
            'corp',
            {
                'payment_icon': 'corp',
                'payment_phrase': 'corp+',
                'payment_method_corp': True,
                'payment_method_card': False,
            },
            id='corp',
        ),
    ],
)
async def test_get_payment_method_vars(
        stq3_context: stq_context.Context,
        mock_server,
        mock_functions,
        main_card_payment_id,
        payment_type,
        expected_vars,
):
    method_vars = await payment_method.get_payment_method_vars(
        context=stq3_context,
        order_data=OrderData(
            brand='yataxi',
            country='',
            order={
                'payment_tech': {
                    'main_card_payment_id': main_card_payment_id,
                    'type': payment_type,
                },
            },
            order_proc={'order': {'user_uid': '0'}},
        ),
        locale='ru',
    )
    assert method_vars == expected_vars


@pytest.mark.parametrize(
    'payment_type, card_system, expected_icon',
    [
        pytest.param('cash', None, 'cash', id='cash'),
        pytest.param('corp', None, 'corp', id='corp'),
        pytest.param('applepay', None, 'apple_pay', id='apple_pay'),
        pytest.param('googlepay', None, 'google_pay', id='googlepay'),
        pytest.param('card', None, 'card', id='card'),
        pytest.param('card', 'MasterCard', 'mastercard', id='mastercard'),
        pytest.param('card', 'Maestro', 'maestro', id='maestro'),
        pytest.param('card', 'MIR', 'mir', id='mir'),
        pytest.param('card', 'VISA', 'visa', id='visa'),
        pytest.param('yandex_card', None, 'yandex_card', id='yandex_card'),
        pytest.param('card', 'sbp', 'card', id='sbp'),
        pytest.param('testtesttest', None, None, id='garbage'),
    ],
)
@pytest.mark.config(
    RIDE_REPORT_PAYMENT_METHOD_ICONS={
        'cash_payment_icon': 'cash',
        'corp_payment_icon': 'corp',
        'apple_pay_payment_icon': 'apple_pay',
        'google_pay_payment_icon': 'google_pay',
        'card_payment_icon': 'card',
        'mastercard_payment_icon': 'mastercard',
        'maestro_payment_icon': 'maestro',
        'mir_payment_icon': 'mir',
        'visa_payment_icon': 'visa',
        'yandex_card_payment_icon': 'yandex_card',
    },
)
def test_get_payment_icon(
        stq3_context: stq_context.Context,
        payment_type,
        card_system,
        expected_icon,
):

    icon = payment_method.get_payment_icon(
        context=stq3_context,
        payment_type=payment_type,
        card_system=card_system,
    )
    assert icon == expected_icon


@pytest.mark.parametrize(
    'payment_type, card_number, expected_phrase',
    [
        pytest.param('cash', None, 'Наличные', id='cash'),
        pytest.param('corp', None, 'Корп счёт', id='corp'),
        pytest.param('applepay', None, 'Apple Pay', id='apple_pay'),
        pytest.param('googlepay', None, 'Google Pay', id='googlepay'),
        pytest.param('card', None, '', id='card'),
        pytest.param('card', '12349876', '••••&nbsp;9876', id='mastercard'),
        pytest.param('card', '28395011', '••••&nbsp;5011', id='maestro'),
        pytest.param('card', '28901329', '••••&nbsp;1329', id='mir'),
        pytest.param('card', '79920194', '••••&nbsp;0194', id='visa'),
        pytest.param('yandex_card', None, 'Я', id='yandex_card'),
    ],
)
@pytest.mark.translations(
    notify={
        f'ride_report.html_body.cash_payment_phrase': {'ru': 'Наличные'},
        f'ride_report.html_body.corp_payment_phrase': {'ru': 'Корп счёт'},
        f'ride_report.html_body.yandex_card_payment_phrase': {'ru': 'Я'},
    },
)
def test_get_payment_phrase(
        stq3_context: stq_context.Context,
        payment_type,
        card_number,
        expected_phrase,
):
    phrase = payment_method.get_payment_phrase(
        context=stq3_context,
        payment_type=payment_type,
        card_number=card_number,
        locale='ru',
        brand='yataxi',
    )
    assert phrase == expected_phrase
