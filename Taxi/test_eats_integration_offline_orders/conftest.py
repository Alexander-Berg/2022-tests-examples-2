# pylint: disable=redefined-outer-name,invalid-name
import asyncio
import os
import pathlib
import typing

import aiohttp
import asynctest
import pytest

from eats_integration_offline_orders.components.pos import (
    base_client as base_pos_client,
)
import eats_integration_offline_orders.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from eats_integration_offline_orders.generated.service.swagger.models import (
    api as api_module,
)
from eats_integration_offline_orders.internal import enums
from eats_integration_offline_orders.models.order import model as order_models


pytest_plugins = [
    'eats_integration_offline_orders.generated.service.pytest_plugins',
]


ADMIN_ORDER_ITEMS = [
    {
        'id': 'product_id__1',
        'in_pay_count': 1.0,
        'paid_count': 0.0,
        'price': 0.1,
        'base_price': 0.1,
        'quantity': 2.0,
        'title': 'Торт с холестерином',
        'vat': 20.0,
    },
    {
        'id': 'product_id__2',
        'in_pay_count': 1.0,
        'paid_count': 0.0,
        'price': 0.23,
        'base_price': 0.23,
        'quantity': 1.0,
        'title': 'Палтус за палтус',
        'vat': 20.0,
    },
]
ADMIN_PLACE_1_CONTACTS_1 = {
    'comment': 'звонить в будни',
    'fullname_id': 'personal_fullname_id_1',
    'phone_id': 'personal_phone_id_1',
    'place_id': 'place_id__1',
    'title': 'ЛПР',
    'uuid': 'contact_uuid_1',
}
ADMIN_PLACE_1_MANGERS_1 = {
    'place_id': 'place_id__1',
    'telegram_login_id': 'personal_telegram_login_id_1',
    'uuid': 'manager_uuid_1',
}
BASE_MENU = {
    'menu': {
        'categories': [
            {
                'available': True,
                'id': 'menu_category_id__1',
                'name': 'Выпечка',
            },
        ],
        'items': [
            {
                'available': True,
                'categoryId': 'menu_category_id__1',
                'description': 'с изюмом',
                'id': 'menu_item_id__1',
                'images': [],
                'name': 'Булочка',
                'price': 100.0,
            },
        ],
    },
}
PARTLY_UPDATED_MENU = {
    'menu': {
        'categories': [
            {
                'available': True,
                'id': 'menu_category_id__1',
                'name': 'Выпечка',
            },
        ],
        'items': [
            {
                'available': True,
                'categoryId': 'menu_category_id__1',
                'description': 'с изюмом',
                'id': 'menu_item_id__1',
                'images': [
                    {
                        'url': (
                            '$mockserver/mds_avatars/get-inplace/1/image/orig'
                        ),
                        'image_id': '1/image',
                    },
                ],
                'measure': 200.0,
                'measureUnit': 'Грамм',
                'name': 'Булочка',
                'price': 100.0,
                'sortOrder': 150,
                'vat': 10,
            },
        ],
    },
}
FULL_MENU_UPDATES = {
    'menu': {
        'categories': [
            {
                'available': True,
                'id': 'menu_category_id__1',
                'name': 'Выпечка',
                'sortOrder': 160,
            },
        ],
        'items': [
            {
                'available': True,
                'categoryId': 'menu_category_id__1',
                'description': 'с изюмом',
                'id': 'menu_item_id__1',
                'images': [
                    {
                        'url': (
                            '$mockserver/mds_avatars/get-inplace/1/image1/orig'
                        ),
                        'image_id': '1/image1',
                    },
                    {
                        'url': (
                            '$mockserver/mds_avatars/get-inplace/1/image2/orig'
                        ),
                        'image_id': '1/image2',
                    },
                ],
                'measure': 200.0,
                'measureUnit': 'Грамм',
                'name': 'Булочка',
                'nutrients': {
                    'calories': '1.0',
                    'carbohydrates': '50',
                    'fats': '3.6',
                    'proteins': '2.3',
                },
                'price': 100.0,
                'sortOrder': 150,
                'vat': 10,
            },
        ],
    },
}

ADMIN_TRANSACTION_ITEMS = [
    {
        'id': 'product_id__1',
        'price': 0.1,
        'quantity': 2.0,
        'title': 'Торт с холестерином',
        'vat': 20.0,
        'in_pay_count': 0.0,
        'paid_count': 0.0,
        'base_price': 0.1,
    },
    {
        'id': 'product_id__2',
        'price': 0.23,
        'quantity': 1.0,
        'title': 'Палтус за палтус',
        'vat': 20.0,
        'in_pay_count': 0.0,
        'paid_count': 0.0,
        'base_price': 0.23,
    },
]
ADMIN_TEMPLATE_SETTINGS = {
    'qr': {'rotate': 0.0, 'size': 40, 'x': 50, 'y': 50},
    'text': {
        'alpha': 1.0,
        'color': '#FFFFFF',
        'font_name': 'YandexSansText-Medium',
        'font_size': 8.0,
        'rotate': 0.0,
        'x': 50,
        'y': 20,
    },
}
ADMIN_TEMPLATE_AUTO_GENERATE_SETTINGS = {
    'qr': {'rotate': 0.0, 'size': 50, 'x': 0, 'y': 0},
    'text': {
        'alpha': 1.0,
        'color': '#FFFFFF',
        'font_name': 'YandexSansText-Medium',
        'font_size': 8.0,
        'rotate': 0.0,
        'x': 0,
        'y': 0,
    },
}
MDS_S3_BUCKET_NAME = 'eats-integration-offline-orders-test'
MOCK_UUID = 'new_uuid'


@pytest.fixture
def table_uuid():
    return 'uuid__1'


@pytest.fixture
def place_id():
    # for:
    #   table_uuid: uuid__1
    return 'place_id__1'


@pytest.fixture
def table_pos_id():
    # for:
    #   place: place_id__1
    return 'table_id__1'


@pytest.fixture
def restaurant_slug():
    # for:
    #   place: place_id__1
    return 'place_id__1_slug'


@pytest.fixture
def order_uuid():
    # for:
    #   place: place_id__1
    #   pos table:  table_id__1
    return 'order_uuid__1'


@pytest.fixture
def pos_type():
    # for:
    #   place_id: place_id__1
    return 'iiko'


@pytest.fixture
def payment_transaction_uuid():
    # for:
    #   place_id: place_id__1
    #   table_uuid: uuid__1
    return 'transaction_uuid__1'


@pytest.fixture
def front_transaction_uuid():
    # for:
    #   place_id: place_id__1
    #   table_uuid: uuid__1
    #   transaction_uuid: transaction_uuid__1
    return 'front_transaction_uuid__1'


@pytest.fixture
def pos_orders(load_json):
    return api_module.PosOrders.deserialize(load_json('orders.json'))


@pytest.fixture
def order_model_object(pos_orders):
    return order_models.Order.from_pos_model(pos_orders.orders[0])


@pytest.fixture
def get_search_pathes(get_search_pathes, request):
    def _get_search_pathes(filename):
        yield from get_search_pathes(filename)
        yield (
            pathlib.Path(request.fspath.dirname).parent
            / pathlib.Path('static/default')
            / filename
        )

    return _get_search_pathes


@pytest.fixture
def payture_mocks(mockserver, web_context, load):

    client = web_context.payture_client
    init_path = client.config['init_path']

    @mockserver.handler(f'/payture{init_path}')
    def _init(request):
        _init.request = request
        return mockserver.make_response(load('payture/response_init.xml'))

    return {'init': _init}


@pytest.fixture
def billing_mocks(
        mock_eda_billing_storage, mock_eats_billing_processor, stq, mockserver,
):
    @mock_eda_billing_storage('/internal-api/v1/billing-storage/create')
    def order_billing(request):
        return mockserver.make_response(json={})

    @mock_eats_billing_processor('/v1/create')
    def discount_billing(request):
        return mockserver.make_response(json={'event_id': '1'})

    return {
        'for_order': order_billing,
        'for_fee': stq.eats_payments_billing_proxy_callback,
        'for_ya_discount': discount_billing,
    }


@pytest.fixture
def pos_client_mock(load_json, patch):
    class MockedPOSClient:

        get_check = asynctest.CoroutineMock(
            return_value=api_module.PosOrders.deserialize(
                data=load_json('orders.json'),
            ),
        )

        freeze_order = asynctest.CoroutineMock(
            return_value=api_module.PosOrders.deserialize(
                data=load_json('orders.json'),
            ).orders[0],
        )

        send_payment_result = asynctest.CoroutineMock(return_value=True)
        apply_loyalty = asynctest.CoroutineMock(
            return_value=base_pos_client.POSResponse(status=200),
        )

    mocked_pos_client = MockedPOSClient()

    @patch(
        'eats_integration_offline_orders.components.pos.'
        'pos_selector.POSSelector.by_type',
    )
    def _pos_by_type(*args, **kwargs):
        return mocked_pos_client

    return mocked_pos_client


# ws mocks


@pytest.fixture
def pos_ws_id():
    # its just login for connect
    return 'pos_id__1'


@pytest.fixture
def pos_ws_token():
    # token for pos_id__1 fixture value
    return 'token__1'


@pytest.fixture
def pos_ws_message_factory():
    def factory(**values):
        default = {
            'message_uuid': 'message_uuid',
            'headers': {'code': 200},
            'type': enums.POSWsMessageType.RESPONSE.value,
            'body': {},
        }
        return {**default, **values}

    return factory


@pytest.fixture
async def pos_ws_connection(
        web_app_client, pos_ws_id, pos_ws_token, load_json,
):

    ws_conn = await web_app_client.ws_connect(
        f'/v1/ws?pos_id={pos_ws_id}', headers={'Authorization': pos_ws_token},
    )

    assert ws_conn

    async def _remote_client():

        try:
            async for msg in ws_conn:
                if msg.type in (
                        aiohttp.WSMsgType.TEXT,
                        aiohttp.WSMsgType.BINARY,
                ):
                    msg = msg.json()

                    assert msg['message_uuid']
                    assert msg['type']
                    assert msg['headers']['method']
                    assert 'body' in msg

                    answer = msg.copy()
                    answer['type'] = 'response'
                    answer['headers'] = {'code': 200}

                    method = msg['headers']['method']
                    if method == 'get_table':
                        assert msg['headers']['args']['table_id']
                        answer['body'] = load_json('orders.json')

                    elif method == 'freeze_order':
                        assert msg['headers']['args']['order_uuid']
                        answer['body'] = load_json('orders.json')['orders'][0]

                    elif method == 'pay_order':
                        assert msg['body']['success']
                        answer['body'] = {}

                    await ws_conn.send_json(answer)
                    print(f'WS Client send answer to WS Server "{answer}"')
                elif msg.type == aiohttp.WSMsgType.closed:
                    print(f'WS Client get close message from server')
                    break
                elif msg.type == aiohttp.WSMsgType.error:
                    print(f'WS Client get error message from server')
                    break

        finally:
            await ws_conn.close()
            print(f'Remote server close connection.')

    remote_client = asyncio.create_task(_remote_client())

    yield ws_conn

    remote_client.cancel()
    await ws_conn.close()


@pytest.fixture
async def notify_none_selector(web_context, patch):
    @patch(
        'eats_integration_offline_orders.components.notifications'
        '.notifier_selector.NotifierSelector.get_selector',
    )
    async def _selector(place_id=None):
        return None

    return _selector


@pytest.fixture
async def notify_iiko_waiter_selector(web_context, patch):
    @patch(
        'eats_integration_offline_orders.components.notifications'
        '.notifier_selector.NotifierSelector.get_selector',
    )
    async def _selector(place_id=None):
        return web_context.iiko_waiter_notifier

    return _selector


@pytest.fixture
async def notify_telegram_selector(web_context, patch):
    @patch(
        'eats_integration_offline_orders.components.notifications'
        '.notifier_selector.NotifierSelector.get_selector',
    )
    async def _selector(place_id=None):
        return web_context.telegram_bot

    return _selector


@pytest.fixture
def epma_v1_payment_methods_availability_response():
    return {
        'payment_methods': [
            {
                'type': 'card',
                'name': 'unknown',
                'id': 'card-x66b88c90fc8d571e6d5e9715',
                'bin': '000000',
                'currency': 'RUB',
                'system': 'unknown',
                'number': '000000****0000',
                'short_title': '****0000',
                'availability': {'available': True, 'disabled_reason': ''},
                'service_token': (
                    'food_payment_c808ddc93ffec050bf0624a4d3f3707c'
                ),
            },
            {
                'type': 'googlepay',
                'availability': {'available': True, 'disabled_reason': ''},
                'merchant_id': '54d3b442-0e2c-4b44-8294-62ed87d047b7',
                'service_token': (
                    'food_payment_c808ddc93ffec050bf0624a4d3f3707c'
                ),
            },
            {
                'availability': {'available': True, 'disabled_reason': ''},
                'name': 'Yandex Badge',
                'id': 'badge:yandex_badge:RUB',
                'currency': 'RUB',
                'description': '',
                'type': 'corp',
            },
            {
                'availability': {'available': True, 'disabled_reason': ''},
                'name': 'ООО СОЦ-Информ',
                'id': 'corp:61a7f66f3bc44cf2a8e2a32c8326abf0:RUB',
                'currency': 'RUB',
                'description': '',
                'type': 'corp',
            },
        ],
    }


@pytest.fixture
def mock_epma_v1_payment_methods_availability(  # pylint: disable=invalid-name
        mock_eats_payment_methods_availability,
        epma_v1_payment_methods_availability_response,
):
    @mock_eats_payment_methods_availability('/v1/payment-methods/availability')
    def _mock_v1_payment_methods_availability():
        return epma_v1_payment_methods_availability_response

    return _mock_v1_payment_methods_availability


@pytest.fixture
def mock_generate_uuid(patch):
    @patch('eats_integration_offline_orders.internal.utils.' 'generate_uuid')
    def _generate_uuid() -> str:
        return MOCK_UUID


def create_admin_place(
        id: int,  # pylint: disable=W0622
        slug: str,
        name: str,
        enabled: bool = True,
        description: str = '',
        logo_link: str = '',
        pos_type: str = 'iiko',
        tips_link: str = '',
        place_id: typing.Optional[str] = None,
        pos_token_updated_at: typing.Optional[str] = None,
        pos_api_version: typing.Optional[str] = None,
        address: typing.Optional[str] = None,
        brand_id: typing.Optional[str] = None,
        contacts: typing.Optional[typing.List] = None,
        mark_status: str = 'success',
) -> typing.Dict:
    if contacts is None:
        contacts = []
    if place_id is None:
        place_id = f'place_id__{id}'
    response = {
        'id': id,
        'place_id': place_id,
        'slug': slug,
        'name': name,
        'logo_link': logo_link,
        'description': description,
        'pos_type': pos_type,
        'tips_link': tips_link,
        'enabled': enabled,
        'contacts': contacts,
        'mark_status': mark_status,
    }
    if pos_token_updated_at is not None:
        response['pos_token_updated_at'] = pos_token_updated_at
    if pos_api_version is not None:
        response['pos_api_version'] = pos_api_version
    if address is not None:
        response['address'] = address
    if brand_id is not None:
        response['brand_id'] = brand_id
    return response


def load_pdf_template(filename):
    static_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'static', 'default',
    )
    with open(os.path.join(static_dir, filename), 'rb') as stream:
        return stream.read()


def create_admin_posm_template(
        template_id,
        name,
        description,
        visibility='global',
        settings=None,
        place_ids=None,
):
    if settings is None:
        settings = ADMIN_TEMPLATE_SETTINGS
    result = {
        'description': description,
        'name': name,
        'settings': settings,
        'template_id': template_id,
        'visibility': visibility,
        'url': f'/admin/v1/posm/template/download?template_id={template_id}',
    }
    if place_ids is not None:
        result['place_ids'] = place_ids
    return result


ADMIN_POSM_TEMPLATE_1 = create_admin_posm_template(
    template_id=1,
    name='template_1',
    description='nice template',
    settings=ADMIN_TEMPLATE_AUTO_GENERATE_SETTINGS,
)
ADMIN_POSM_TEMPLATE_2 = create_admin_posm_template(
    template_id=2,
    name='awesome template',
    description='another template',
    settings=ADMIN_TEMPLATE_SETTINGS,
)
ADMIN_POSM_TEMPLATE_4 = create_admin_posm_template(
    template_id=4,
    name='template_4',
    description='restaurant template',
    visibility='restaurant',
    settings=ADMIN_TEMPLATE_SETTINGS,
    place_ids=['place_id__4', 'place_id__5'],
)
