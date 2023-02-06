import datetime
import typing
import json

import pytest

from . import eats_catalog_storage
from . import experiments
from . import umlaas_eats
from . import utils

# pylint: disable=import-error
from dj.services.eats.eats_recommender.recommender.server.proto import (
    upsell_products_pb2,
)  # noqa: F401
from google.protobuf import json_format
# pylint: enable=import-error


async def test_upsell_empty_response(taxi_eats_upsell):
    """
    sanity-check  test
    """

    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        headers={'x-device-id': 'testsuite'},
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [],
                'cart': {'total': 0, 'items': []},
            },
        },
    )
    assert response.status_code == 200

    payload = response.json()['payload']
    assert not payload['items']


@pytest.mark.skip(reason='not ready yet')
@experiments.upsell_sources([experiments.SourceType.COMPLEMENT])
@experiments.get_upsell_complement()
async def test_upsell_get_recommendations_umlaas(
        taxi_eats_upsell, eats_catalog_storage_service, core_menu_items,
):
    core_menu_items.set_items(
        [utils.build_core_item(777), utils.build_core_item(2)],
    )

    # umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid='2', group_id='1'))

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=1),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {
                    'total': 100,
                    'items': [
                        {'id': 777, 'quantity': 1, 'options': []},
                        {'id': 381732, 'quantity': 1, 'options': []},
                    ],
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json()['payload']['items'] == [
        {
            'id': 2,
            'name': 'name 2',
            'description': 'description 2',
            'available': True,
            'inStock': None,
            'price': 10,
            'decimalPrice': '10',
            'promoPrice': None,
            'decimalPromoPrice': None,
            'promoTypes': [],
            'optionsGroups': [],
            'picture': None,
            'weight': '100кг',
            'adult': False,
            'shippingType': 'all',
        },
    ]

    assert core_menu_items.times_called > 0
    assert eats_catalog_storage_service.times_called == 1


dj_exp_name = 'upsell_history_npmi_popular'

PLACE_ID = 1
item_to_universal = [
    (16846028, 'f358d60b90c6360fa1defaad0feef48a'),
    (16845968, 'd2f5ad5dcd6f83115863a3b8fb65cc7e'),
]
universal_to_items = [
    ('0011657e5a8bf594df5ce7778b82e922', [13751927]),
    ('0fea71e3d430a570c3edfbce1bfa76d4', [18573640, 13748123]),
]


def make_expected_item(id: int):
    return {
        'id': id,
        'name': 'name {}'.format(id),
        'description': 'description {}'.format(id),
        'available': True,
        'inStock': None,
        'price': 10,
        'decimalPrice': '10',
        'promoPrice': None,
        'decimalPromoPrice': None,
        'promoTypes': [],
        'optionsGroups': [],
        'picture': None,
        'weight': '100кг',
        'adult': False,
        'shippingType': 'all',
    }


@pytest.mark.parametrize(
    'dj_called',
    [
        pytest.param(
            1,
            marks=(experiments.upsell_dj_settings(True, dj_exp_name)),
            id='enabled_dj',
        ),
        pytest.param(
            0,
            marks=(experiments.upsell_dj_settings(False, dj_exp_name)),
            id='disabled_dj',
        ),
        pytest.param(0, id='no exp dj'),
    ],
)
async def test_dj_recommendations(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        core_menu_items,
        umlaas_suggest,
        mockserver,
        dj_called,
):
    @mockserver.json_handler('/eats-recommender/v1/upsell/products')
    def recommender_places(request):
        request_proto = upsell_products_pb2.TRequest()
        request_proto.ParseFromString(request.get_data())

        data = json.loads(json_format.MessageToJson(request_proto))

        assert data == {
            'Experiment': dj_exp_name,
            'User': {},
            'Place': {'Id': str(PLACE_ID)},
            'Brand': {'Id': '1'},
            'Cart': {
                'Products': [
                    {'Id': uni_key} for (item_id, uni_key) in item_to_universal
                ],
            },
        }

        response = upsell_products_pb2.TResponse()
        json_format.ParseDict(
            {
                'Products': [
                    {'Id': uni_id} for (uni_id, items) in universal_to_items
                ],
            },
            response,
        )

        return mockserver.make_response(
            response.SerializeToString(deterministic=True),
        )

    core_menu_items.set_items(
        [utils.build_core_item(key) for (key, uni_key) in item_to_universal]
        + [
            utils.build_core_item(item_id)
            for (uni_key, items) in universal_to_items
            for item_id in items
        ],
    )

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=PLACE_ID),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {
                    'total': 100,
                    'items': [
                        {'id': item_id, 'quantity': 1, 'options': []}
                        for item_id, uni_key in item_to_universal
                    ],
                },
            },
        },
    )
    assert response.status_code == 200
    assert recommender_places.times_called == dj_called
    assert umlaas_suggest.times_called == 0 if dj_called else 1
    if dj_called:
        assert response.json()['payload']['items'] == [
            make_expected_item(items[0])
            for (uni_key, items) in universal_to_items
        ]


async def test_upsell_get_recommendations(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        core_menu_items,
        umlaas_suggest,
):
    core_menu_items.set_items(
        [utils.build_core_item(1), utils.build_core_item(2)],
    )

    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid='2', group_id='1'))

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=1),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {
                    'total': 100,
                    'items': [{'id': 1, 'quantity': 1, 'options': []}],
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json()['payload']['items'] == [
        {
            'id': 2,
            'name': 'name 2',
            'description': 'description 2',
            'available': True,
            'inStock': None,
            'price': 10,
            'decimalPrice': '10',
            'promoPrice': None,
            'decimalPromoPrice': None,
            'promoTypes': [],
            'optionsGroups': [],
            'picture': None,
            'weight': '100кг',
            'adult': False,
            'shippingType': 'all',
        },
    ]

    assert core_menu_items.times_called > 0
    assert eats_catalog_storage_service.times_called == 1
    assert umlaas_suggest.times_called == 1


@pytest.mark.parametrize(
    'dynamic_price',
    [
        pytest.param(
            True,
            marks=[
                experiments.dynamic_prices(10),
                pytest.mark.smart_prices_cache({'1': 100}),
            ],
            id='dynamic_prices_10_100',
        ),
        pytest.param(
            True,
            marks=[
                experiments.dynamic_prices(100),
                pytest.mark.smart_prices_cache({'1': 10}),
            ],
            id='dynamic_prices_100_10',
        ),
        pytest.param(
            False,
            marks=pytest.mark.smart_prices_cache({'1': 10}),
            id='dynamic_prices_off_by_exp',
        ),
        pytest.param(
            False,
            marks=experiments.dynamic_prices(10),
            id='dynamic_prices_off_by_service',
        ),
    ],
)
async def test_upsell_smart_prices(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        core_menu_items,
        umlaas_suggest,
        dynamic_price,
):
    core_menu_items.set_items(
        [utils.build_core_item(1), utils.build_core_item(2)],
    )

    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid='2', group_id='1'))

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=1),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {
                    'total': 100,
                    'items': [{'id': 1, 'quantity': 1, 'options': []}],
                },
            },
        },
    )
    assert response.status_code == 200
    price = 10
    decimal_price = '10'
    if dynamic_price:
        price = 11
        decimal_price = '11'
    assert response.json()['payload']['items'] == [
        {
            'id': 2,
            'name': 'name 2',
            'description': 'description 2',
            'available': True,
            'inStock': None,
            'price': price,
            'decimalPrice': decimal_price,
            'promoPrice': None,
            'decimalPromoPrice': None,
            'promoTypes': [],
            'optionsGroups': [],
            'picture': None,
            'weight': '100кг',
            'adult': False,
            'shippingType': 'all',
        },
    ]

    assert core_menu_items.times_called > 0
    assert eats_catalog_storage_service.times_called == 1
    assert umlaas_suggest.times_called == 1


async def test_upsell_filter_group_id(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        core_menu_items,
        umlaas_suggest,
):
    """
    EDACAT-1221: тест проверяет фильтрацию позиций из одинаоковой группы.
    """

    item_ids = [1, 2, 3]
    for item_id in item_ids:
        core_menu_items.add_item(utils.build_core_item(item_id))

    for item_id in [2, 3]:
        umlaas_suggest.add_item(
            umlaas_eats.SuggestItem(uuid=str(item_id), group_id='1'),
        )

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=1),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {
                    'total': 100,
                    'items': [{'id': 1, 'quantity': 1, 'options': []}],
                },
            },
        },
    )
    assert response.status_code == 200

    assert eats_catalog_storage_service.times_called == 1
    assert core_menu_items.times_called == 2
    assert umlaas_suggest.times_called == 1

    items = response.json()['payload']['items']
    assert len(items) == 1
    assert items[0]['id'] == 2


async def test_upsell_filter_unavailable_items(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        core_menu_items,
        umlaas_suggest,
):
    """
    EDACAT-1216: проверяет, что недоступные блюда не попадут в ответ сервиса.
    """

    items = [
        {'id': 1, 'available': True},
        {'id': 2, 'available': True},
        {'id': 3, 'available': False},
    ]
    for item in items:
        core_menu_items.add_item(
            utils.build_core_item(item['id'], available=item['available']),
        )

    umlaas_suggest.add_items(
        [umlaas_eats.SuggestItem(uuid='2'), umlaas_eats.SuggestItem(uuid='3')],
    )

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=1),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {
                    'total': 100,
                    'items': [{'id': 1, 'quantity': 1, 'options': []}],
                },
            },
        },
    )
    assert response.status_code == 200

    items = response.json()['payload']['items']
    assert len(items) == 1
    assert items[0]['id'] == 2


@pytest.mark.parametrize(
    'log_enabled',
    [
        pytest.param(False, id='log disabled'),
        pytest.param(True, id='log enabled'),
    ],
)
async def test_upsell_log_response(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        core_menu_items,
        umlaas_suggest,
        taxi_config,
        testpoint,
        log_enabled,
):
    """
    EDACAT-1250: тест проверяет, что конфиг регулирует логгирование ответа
    ручки рекомендаций.
    """

    taxi_config.set_values(
        {
            'EATS_UPSELL_LOG_SETTINGS': {
                'upsell_response_log_enabled': log_enabled,
            },
        },
    )

    for item_id in [1, 2]:
        core_menu_items.add_item(utils.build_core_item(item_id))

    umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid='2'))

    @testpoint('v1_upsell::log_response')
    def log_response(data):
        assert 'response' in data

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=1),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 2}],
                'cart': {
                    'total': 100,
                    'items': [{'id': 1, 'quantity': 1, 'options': []}],
                },
            },
        },
    )
    assert response.status_code == 200
    assert log_response.times_called == (1 if log_enabled else 0)


@pytest.mark.parametrize(
    'has_recomendations, expected_empty_resps, expected_non_empty_resps',
    [
        pytest.param(True, 0, 1, id='non empty response'),
        pytest.param(False, 1, 0, id='empty response'),
    ],
)
async def test_ml_metrics(
        taxi_eats_upsell,
        taxi_eats_upsell_monitor,
        eats_catalog_storage_service,
        core_menu_items,
        umlaas_suggest,
        has_recomendations,
        expected_empty_resps,
        expected_non_empty_resps,
):
    """
    Тест проверяет работу метрик, отслеживающий пустые/непустые ответы
    eats-umlaas
    """

    await taxi_eats_upsell.tests_control(reset_metrics=True)

    core_menu_items.set_items(
        [utils.build_core_item(0), utils.build_core_item(1)],
    )
    if has_recomendations:
        umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid='1'))

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=1),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 0}],
                'cart': {
                    'total': 100,
                    'items': [{'id': 0, 'quantity': 1, 'options': []}],
                },
            },
        },
    )

    assert response.status_code == 200
    assert (
        await taxi_eats_upsell_monitor.get_metric(
            'eats-upsell_umlaas-empty-responses',
        )
        == expected_empty_resps
    )
    assert (
        await taxi_eats_upsell_monitor.get_metric(
            'eats-upsell_umlaas-non-empty-responses',
        )
        == expected_non_empty_resps
    )


@pytest.mark.now('2021-07-27T13:30:00+00:00')
@pytest.mark.parametrize(
    'cart, expected_umlaas_request, expected_items',
    [
        pytest.param(
            {'total': 0, 'items': [{'id': 2, 'options': [], 'quantity': 1}]},
            umlaas_eats.SuggestRequest(
                context=umlaas_eats.SuggestContext(
                    items=[umlaas_eats.RequestItem(uuid='1')],
                    cart_items=[umlaas_eats.RequestCartItem(uuid='2')],
                    cart_sum=0.0,
                ),
                place_id=1,
                brand_id=1,
                predicting_at=datetime.datetime.fromisoformat(
                    '2021-07-27T13:30:00+00:00',
                ),
            ),
            [1, 3, 4, 5],
            id='cart total is zero',
        ),
        pytest.param(
            {'total': 100, 'items': [{'id': 2, 'options': [], 'quantity': 1}]},
            umlaas_eats.SuggestRequest(
                context=umlaas_eats.SuggestContext(
                    items=[umlaas_eats.RequestItem(uuid='1')],
                    cart_items=[umlaas_eats.RequestCartItem(uuid='2')],
                    cart_sum=100.0,
                ),
                place_id=1,
                brand_id=1,
                predicting_at=datetime.datetime.fromisoformat(
                    '2021-07-27T13:30:00+00:00',
                ),
            ),
            [1, 3, 4, 5],
            id='cart total is 100',
        ),
        pytest.param(
            {'items': [{'id': 2, 'options': [], 'quantity': 1}]},
            umlaas_eats.SuggestRequest(
                context=umlaas_eats.SuggestContext(
                    items=[umlaas_eats.RequestItem(uuid='1')],
                    cart_items=[umlaas_eats.RequestCartItem(uuid='2')],
                    cart_sum=0,
                ),
                place_id=1,
                brand_id=1,
                predicting_at=datetime.datetime.fromisoformat(
                    '2021-07-27T13:30:00+00:00',
                ),
            ),
            [1, 3, 4, 5],
            id='no cart total',
        ),
        pytest.param(
            {
                'items': [{'id': 2, 'options': [], 'quantity': 1}],
                'total': {'value': 339},
            },
            umlaas_eats.SuggestRequest(
                context=umlaas_eats.SuggestContext(
                    items=[umlaas_eats.RequestItem(uuid='1')],
                    cart_items=[umlaas_eats.RequestCartItem(uuid='2')],
                    cart_sum=339,
                ),
                place_id=1,
                brand_id=1,
                predicting_at=datetime.datetime.fromisoformat(
                    '2021-07-27T13:30:00+00:00',
                ),
            ),
            [1, 3, 4, 5],
            id='cart total is object',
        ),
    ],
)
async def test_upsell_parse_request_cart(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        core_menu_items,
        umlaas_suggest,
        cart,
        expected_umlaas_request: umlaas_eats.SuggestRequest,
        expected_items,
):
    """
    EDACAT-1419: проверяет, что корзина парсится валидно
    """

    item_ids: list = [1, 2, 3, 4, 5]
    for item_id in item_ids:
        core_menu_items.add_item(utils.build_core_item(item_id))
        umlaas_suggest.add_item(umlaas_eats.SuggestItem(uuid=str(item_id)))

    umlaas_suggest.set_expected_request(expected_umlaas_request)

    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=1),
    )
    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': cart,
            },
        },
    )
    assert response.status_code == 200
    assert core_menu_items.times_called == 2
    assert eats_catalog_storage_service.times_called == 1
    assert umlaas_suggest.times_called == 1

    items = response.json()['payload']['items']
    assert len(expected_items) == len(items)
    for expected_item, item in zip(expected_items, items):
        assert expected_item == item['id']


async def test_core_has_auth_context(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        mockserver,
        umlaas_suggest,
):
    """
    EDACAT-1367: проверяет, что в запрсое к коре есть заголовки из
    eats-auth-context
    """

    place_id: int = 1
    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=place_id),
    )

    auth_headers: dict = {
        'x-device-id': 'testsuite',
        'x-yandex-uid': 'yandex-suite',
        'x-eats-session': 'session-suite',
    }

    @mockserver.json_handler(
        '/eats-core-place-menu/internal-api/v1/place/menu/get-items',
    )
    def get_items(request):
        for header in auth_headers:
            assert header in request.headers
            assert auth_headers[header] == request.headers[header]

        return {
            'place_id': str(place_id),
            'place_slug': f'place_{place_id}',
            'place_brand_business_type': 'restaurant',
            'place_menu_items': [],
        }

    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        headers=auth_headers,
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {'total': 0, 'items': []},
            },
        },
    )
    assert response.status_code == 200
    assert get_items.times_called == 1


@pytest.mark.parametrize(
    'request_platform, request_app_version',
    [
        pytest.param(None, None, id='pass nothing'),
        pytest.param('', '', id='pass nothing on empty headers'),
        pytest.param('ios_app', '5.30.0', id='pass x-headers'),
        pytest.param('ios_app', None, id='only x-platform'),
        pytest.param(None, '5.30.0', id='only x-app-version'),
    ],
)
async def test_core_has_x_headers(
        taxi_eats_upsell,
        eats_catalog_storage_service,
        mockserver,
        umlaas_suggest,
        request_platform: typing.Optional[str],
        request_app_version: typing.Optional[str],
):
    """
    EDACAT-2301: проверяет, что в запросе в кору передаются непустые заголовки:
        - x-platform
        - x-app-version
    """

    place_id: int = 1
    eats_catalog_storage_service.add_place(
        eats_catalog_storage.build_storage_place(place_id=place_id),
    )

    request_headers = {
        'x-platform': request_platform,
        'x-app-version': request_app_version,
    }

    @mockserver.json_handler(
        '/eats-core-place-menu/internal-api/v1/place/menu/get-items',
    )
    def get_items(request):
        for header in request_headers:
            value = request_headers[header]
            if not value:
                assert (
                    header not in request.headers
                    or not request.headers[header]
                )
            else:
                assert header in request.headers
                assert request_headers[header] == request.headers[header]

        return {
            'place_id': str(place_id),
            'place_slug': f'place_{place_id}',
            'place_brand_business_type': 'restaurant',
            'place_menu_items': [],
        }

    response = await taxi_eats_upsell.post(
        '/eats-upsell/v1/upsell',
        headers=request_headers,
        json={
            'requestSource': 'cart',
            'context': {
                'shippingType': 'delivery',
                'items': [{'id': 1}],
                'cart': {'total': 0, 'items': []},
            },
        },
    )
    assert response.status_code == 200
    assert get_items.times_called == 1
