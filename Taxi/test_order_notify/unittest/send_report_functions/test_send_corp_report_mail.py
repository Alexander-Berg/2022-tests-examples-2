import typing

import bson
import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories import send_report_functions
from order_notify.repositories.email.message import Message
from order_notify.repositories.order_info import OrderData


@pytest.fixture(name='mock_functions')
def mock_corp_send_functions(patch):
    class Counter:
        def __init__(self):
            self.times_called = 0

        def call(self):
            self.times_called += 1

    class Counters:
        def __init__(self):
            self.construct_message = Counter()
            self.send = Counter()
            self.mark_corp_ride_report_as_sent = Counter()

    counters = Counters()

    @patch('order_notify.repositories.email.message._construct_message')
    async def _construct_message(
            context: stq_context.Context,
            email: str,
            order_data: OrderData,
            locale: str,
            confirmation_code: typing.Optional[str] = None,
            is_corp_report: bool = False,
    ):
        assert email in ('hehehe.haha@yandex.ru', 'siiii.httt@yandex.com')
        assert confirmation_code is None
        assert is_corp_report

        if email == 'hehehe.haha@yandex.ru':
            assert locale == 'ru'
        if email == 'siiii.httt@yandex.ru':
            assert locale == 'en'
        counters.construct_message.call()
        return Message(
            campaign_slug='template_data.country_data.campaign_slug',
            from_name='template_data.locale_data.from_name',
            from_email='template_data.locale_data.from_email',
            to_email=email,
            template_vars={},
        )

    @patch('taxi.clients.sender.SenderClient.send_transactional_email')
    async def _handle_sender(
            campaign_slug,
            from_name,
            from_email,
            to_email,
            template_vars,
            is_async,
    ):
        counters.send.call()

    return counters


@pytest.fixture(name='mock_server')
def mock_server_fixture(mockserver):
    @mockserver.json_handler('/corp-clients/v1/clients')
    async def corp_handler(request):
        assert request.method == 'GET'

        client_id = request.query['client_id']
        if client_id == 'aljabcla':
            return mockserver.make_response(
                json={
                    'id': 'lol',
                    'email': 'hehehe.haha@yandex.ru',
                    'country': 'rus',
                },
                status=200,
            )
        if client_id == '1j4l29cn':
            return mockserver.make_response(
                json={
                    'id': 'lol',
                    'email': 'siiii.httt@yandex.com',
                    'country': 'engl',
                },
                status=200,
            )
        return mockserver.make_response(
            json={'message': 'not found'}, status=404,
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    async def order_core_set_handler(request):
        assert request.method == 'POST'

        order_id = request.query['order_id']
        assert order_id == '2'

        return mockserver.make_response(
            bson.BSON.encode({}), status=200, content_type='application/bson',
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    async def order_core_get_handler(request):
        assert request.method == 'POST'

        order_id = request.query['order_id']
        assert order_id == '2'

        revision = {'processing.version': 8, 'order.version': 16}
        document = {
            'order_info': {'statistics': {'corp_ride_report_sent': False}},
        }
        return mockserver.make_response(
            bson.BSON.encode({'document': document, 'revision': revision}),
            status=200,
            content_type='application/bson',
        )

    return corp_handler, order_core_set_handler, order_core_get_handler


@pytest.mark.parametrize(
    'payment_type, corp_id, expected_times_called',
    [
        pytest.param('cash', 'aljabcla', [0, 0, 0, 0, 0], id='not_corp_order'),
        pytest.param('corp', 'qwcwcww', [1, 0, 0, 0, 0], id='no_corp_client'),
        pytest.param('corp', 'aljabcla', [1, 1, 1, 1, 1], id='corp_no_locale'),
        pytest.param(
            'corp', '1j4l29cn', [1, 1, 1, 1, 1], id='corp_exist_locale',
        ),
    ],
)
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={'engl': {'default_language': 'en'}},
)
async def test_send_corp_report_mail(
        stq3_context: stq_context.Context,
        mock_server,
        mock_functions,
        payment_type,
        corp_id,
        expected_times_called,
):
    await send_report_functions.send_corp_report_mail(
        context=stq3_context,
        order_data=OrderData(
            brand='',
            country='',
            order={'payment_tech': {'type': payment_type}},
            order_proc={
                '_id': '2',
                'payment_tech': {'main_card_billing_id': corp_id},
                'order': {'version': 8},
                'processing': {'version': 1},
            },
        ),
        locale='ru',
    )
    corp_handler, order_core_handler, order_core_get_handler = mock_server
    times_called = [
        corp_handler.times_called,
        mock_functions.construct_message.times_called,
        mock_functions.send.times_called,
        order_core_handler.times_called,
        order_core_get_handler.times_called,
    ]
    assert times_called == expected_times_called
