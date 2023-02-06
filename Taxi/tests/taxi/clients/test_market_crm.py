# pylint: disable=redefined-outer-name, protected-access
import datetime

import pytest

from taxi import discovery
from taxi.clients import market_crm
from taxi.clients.helpers import base_client
from taxi.clients.helpers import errors


@pytest.fixture
def mock_request(patch):
    @patch('taxi.clients.market_crm.MarketCrmApiClient.request')
    async def _dummy_request(method: str, url: str, **kwargs):
        if url == '/chatterbox/orders/111':
            return base_client.Response(body={'first': '111'}, headers={})

        raise errors.NotFoundError('Order not found', 404, '', bytearray())

    return _dummy_request


@pytest.mark.parametrize(
    'order_id, expected_result, expected_exception',
    [('000', None, errors.NotFoundError), ('111', {'first': '111'}, None)],
)
async def test_get_order_meta(
        test_taxi_app,
        mock_request,
        order_id,
        expected_result,
        expected_exception,
):
    client = market_crm.MarketCrmApiClient(
        session=test_taxi_app.session, tvm_client=test_taxi_app.tvm,
    )

    if expected_exception is not None:
        with pytest.raises(expected_exception):
            await client.get_order_meta(order_id)
    else:
        result = await client.get_order_meta(order_id)
        assert result == expected_result


@pytest.mark.parametrize(
    'puid, orders_ids, expected_json_body',
    [
        ('111111111', [], {'puid': '111111111', 'ordersIds': []}),
        ('222222222', ['123'], {'puid': '222222222', 'ordersIds': ['123']}),
    ],
)
async def test_send_message_notify(
        test_taxi_app,
        patch_aiohttp_session,
        response_mock,
        puid,
        orders_ids,
        expected_json_body,
):
    client = market_crm.MarketCrmApiClient(
        session=test_taxi_app.session, tvm_client=test_taxi_app.tvm,
    )

    service = discovery.find_service(market_crm.SERVICE_NAME)

    @patch_aiohttp_session(service.url)
    def _mock_request(*args, **kwargs):
        assert kwargs['json'] == expected_json_body
        return response_mock(status=200)

    await client.send_message_notify(puid, orders_ids)


@pytest.mark.parametrize(
    'ticket, messages, http_status, expected_json_body, expected_exception',
    [
        (
            {
                '_id': '5b2cae5cb2682a976914caa1',
                'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
                'external_id': 'user_chat_message_id_1',
                'line': 'first',
                'status': 'ready_to_archive',
                'support_admin': 'superuser',
                'type': 'chat',
                'chat_type': 'market',
                'meta_info': {
                    'order_id': '11111',
                    'user_email': '111@mail.ru',
                    'user_phone': '+79110000000',
                },
                'history': [
                    {
                        'action': 'accept_task',
                        'login': 'superuser',
                        'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
                    },
                ],
            },
            {
                'messages': [
                    {
                        'sender': {'id': 'support_login', 'role': 'support'},
                        'text': 'support text',
                        'metadata': {
                            'created': datetime.datetime(
                                2018, 5, 5, 12, 34, 57,
                            ),
                        },
                    },
                    {
                        'sender': {'id': 'client_login', 'role': 'client'},
                        'text': 'client text',
                        'metadata': {
                            'created': datetime.datetime(
                                2018, 5, 5, 12, 34, 58,
                            ),
                        },
                    },
                    {
                        'sender': {'id': 'client_login', 'role': 'client'},
                        'text': 'client text',
                    },
                    {
                        'sender': {'id': 'client_login', 'role': 'client'},
                        'text': '',
                    },
                    {
                        'sender': {'id': 'client_login', 'role': 'client'},
                        'text': None,
                    },
                ],
                'hidden_comments': [
                    {
                        'comment': 'hide text',
                        'login': 'superuser',
                        'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
                    },
                    {'comment': 'hide text', 'login': 'superuser'},
                    {
                        'comment': '',
                        'login': 'superuser',
                        'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
                    },
                    {
                        'comment': None,
                        'login': 'superuser',
                        'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
                    },
                ],
            },
            200,
            {
                'title': 'Обращение Крутилки: 5b2cae5cb2682a976914caa1',
                'channel': 'taxiChatterbox',
                'service': 'taxiChat',
                'status': 'archived',
                'taxiChatterboxId': '5b2cae5cb2682a976914caa1',
                'creationTime': '2018-05-05T12:34:56+0000',
                'clientEmail': '111@mail.ru',
                'clientPhone': '+79110000000',
                'orderNumber': '11111',
                'taxiProperties': {
                    'order_id': '11111',
                    'user_email': '111@mail.ru',
                    'user_phone': '+79110000000',
                },
                'taxiHistory': [
                    {
                        'action': 'accept_task',
                        'login': 'superuser',
                        'created': '2018-05-05T12:34:56+0000',
                    },
                ],
                '@comments': [
                    {
                        'metaclass': 'comment$public',
                        'body': 'support text',
                        'creationTime': '2018-05-05T12:34:57+0000',
                    },
                    {
                        'metaclass': 'comment$user',
                        'body': 'client text',
                        'creationTime': '2018-05-05T12:34:58+0000',
                    },
                    {
                        'metaclass': 'comment$user',
                        'body': 'client text',
                        'creationTime': None,
                    },
                    {
                        'metaclass': 'comment$internal',
                        'body': 'hide text',
                        'creationTime': '2018-05-05T12:34:56+0000',
                    },
                    {
                        'metaclass': 'comment$internal',
                        'body': 'hide text',
                        'creationTime': None,
                    },
                ],
            },
            None,
        ),
        (
            {
                '_id': 'task_409',
                'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
            },
            {},
            409,
            {
                'title': 'Обращение Крутилки: task_409',
                'channel': 'taxiChatterbox',
                'service': 'taxiChat',
                'status': 'archived',
                'taxiChatterboxId': 'task_409',
                'creationTime': '2018-05-05T12:34:56+0000',
                'clientEmail': None,
                'clientPhone': None,
                'orderNumber': None,
                'taxiProperties': None,
                'taxiHistory': None,
                '@comments': [],
            },
            None,
        ),
        (
            {
                '_id': 'task_500',
                'created': datetime.datetime(2018, 5, 5, 12, 34, 56),
            },
            {},
            500,
            {
                'title': 'Обращение Крутилки: task_500',
                'channel': 'taxiChatterbox',
                'service': 'taxiChat',
                'status': 'archived',
                'taxiChatterboxId': 'task_500',
                'creationTime': '2018-05-05T12:34:56+0000',
                'clientEmail': None,
                'clientPhone': None,
                'orderNumber': None,
                'taxiProperties': None,
                'taxiHistory': None,
                '@comments': [],
            },
            errors.ResponseError,
        ),
    ],
)
async def test_send_ticket(
        test_taxi_app,
        patch_aiohttp_session,
        response_mock,
        ticket,
        messages,
        http_status,
        expected_json_body,
        expected_exception,
):
    client = market_crm.MarketCrmApiClient(
        session=test_taxi_app.session, tvm_client=test_taxi_app.tvm,
    )

    service = discovery.find_service(market_crm.SERVICE_NAME)

    @patch_aiohttp_session(service.url, 'POST')
    def _mock_request(*args, **kwargs):
        assert kwargs['json'] == expected_json_body
        return response_mock(status=http_status, text='{}')

    if expected_exception is not None:
        with pytest.raises(expected_exception):
            await client.send_ticket(ticket, messages)
    else:
        await client.send_ticket(ticket, messages)
