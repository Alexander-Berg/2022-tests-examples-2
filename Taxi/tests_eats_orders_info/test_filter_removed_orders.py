# pylint: disable=too-many-lines
import pytest

from tests_eats_orders_info import bdu_orders_utils
from tests_eats_orders_info import utils

BDU_ORDERS_URL = '/eats/v1/orders-info/v1/orders'
BDU_REFRESH_ORDERS_URL = '/eats/v1/orders-info/v1/refresh-orders'

ORDERSHISTORY_URL = '/eats-ordershistory/v2/get-orders'
GROCERY_URL = '/grocery-eats-gateway/internal/grocery-eats-gateway/v1/orders'
BDU_GROCERY_URL = (
    '/grocery-eats-gateway/internal/grocery-eats-gateway/v1/batch-orders'
)
BATCH_ORDERSHISTORY_URL = '/eats-ordershistory/internal/v2/get-orders/list'
BATCH_GROCERY_URL = (
    '/grocery-eats-gateway/internal/grocery-eats-gateway/v1/batch-orders'
)

SUPERAPP_REQUEST_BODY = {
    'range': {'results': 10},
    'services': ['eats'],
    'user_identity': {
        'yandex_uid': 'uid',
        'bound_yandex_uids': [],
        'eater_ids': [],
    },
    'include_service_metadata': True,
}
EXP_SUPERAPP_REQUEST_BODY = {
    'range': {'results': 20},
    'services': ['eats'],
    'user_identity': {
        'yandex_uid': 'uid',
        'bound_yandex_uids': [],
        'eater_ids': [],
    },
    'include_service_metadata': True,
}


@pytest.fixture(name='mock_catalog_storage')
def _mock_eats_catalog_storage(mockserver, load_json):
    @mockserver.json_handler(bdu_orders_utils.CATALOG_STORAGE_URL)
    def mock_eats_catalog_storage(request):
        input_data = load_json('bdu_source_data_common.json')
        return mockserver.make_response(
            json=bdu_orders_utils.generate_catalog_info(
                input_data['catalog']['found'],
                input_data['catalog']['not_found'],
            ),
            status=200,
        )

    return mock_eats_catalog_storage


@pytest.fixture(name='mock_revision')
def _mock_revision(mockserver, load_json):
    @mockserver.json_handler(bdu_orders_utils.REVISIONS_URL)
    def mock_revision(request):
        input_data = load_json('bdu_source_data_common.json')
        assert request.method == 'POST'
        assert 'order_id' in request.json
        order_nr = request.json['order_id']
        return mockserver.make_response(
            status=200, json=input_data['revisions'][order_nr],
        )

    return mock_revision


@pytest.fixture(name='mock_restapp')
def _mock_restapp(mockserver, load_json):
    @mockserver.json_handler(bdu_orders_utils.RESTAPP_URL)
    def mock_restapp(request):
        assert request.method == 'POST'
        return mockserver.make_response(status=200, json={'places_items': []})

    return mock_restapp


@pytest.fixture(name='mock_retail')
def _mock_retail(mockserver, load_json):
    @mockserver.json_handler(bdu_orders_utils.RETAIL_UPDATE_URL)
    def mock_retail(request):
        input_data = load_json('bdu_source_data_common.json')
        assert request.method == 'POST'
        assert 'order_nrs' in request.json
        return mockserver.make_response(status=200, json=input_data['retail'])

    return mock_retail


@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={
        'tracking_enabled': True,
        'revisions_enabled': True,
        'restapp_enabled': True,
        'retail_enabled': True,
        'donation_enabled': False,
    },
)
@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY=True)
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=True)
@utils.can_be_removed_config3()
@utils.remove_enabled_config3()
@bdu_orders_utils.general_widget_config3()
@pytest.mark.pgsql('eats_orders_info', files=['remove_database.sql'])
@pytest.mark.parametrize(
    'input_json, expected_orders',
    [
        pytest.param(
            'bdu_source_data_have_removed.json',
            [
                {
                    'order_nr': '123-123-grocery',
                    'total_cost': 123.45,
                    'place_name': 'lavka',
                    'status': 'Подтвержден',
                    'created_at': '31 Октября 23:58, 2019',
                    'can_be_removed': False,
                },
                {
                    'order_nr': '123-123',
                    'total_cost': 384,
                    'place_name': 'Neverland',
                    'status': 'Подтвержден',
                    'created_at': '12 Октября 02:58, 2019',
                    'items': [
                        {
                            'name': 'pizza2',
                            'image_url': (
                                'product_pizza2_image_url_front/{w}x{h}'
                            ),
                        },
                    ],
                    'total_items_number': 2,
                    'can_be_removed': False,
                },
                {
                    'order_nr': '124-124',
                    'total_cost': 100,
                    'place_name': 'Neverland',
                    'status': 'Завершен',
                    'created_at': '01 Декабря 02:58, 2019',
                    'can_be_removed': True,
                },
            ],
            id='have_removed_orders',
        ),
    ],
)
async def test_bdu_removed_orders_iterations(
        taxi_eats_orders_info,
        mock_orders_tracking_dummy,
        mock_feedback_dummy,
        mock_catalog_storage,
        mock_revision,
        mock_restapp,
        mock_retail,
        mockserver,
        load_json,
        input_json,
        expected_orders,
):
    eater_id = '22'
    limit = 3
    input_data = load_json(input_json)

    @mockserver.json_handler(ORDERSHISTORY_URL)
    def _mock_eats_ordershistory(request):
        offset = request.json['offset']
        assert offset in (0, 2)
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    input_data['ordershistory'][offset : offset + 2],
                ),
            },
        )

    @mockserver.json_handler(GROCERY_URL)
    def _mock_grocery_gateaway(request):
        data = []
        # first getting data
        if 'older_than' in request.json:
            assert request.json['older_than'] == '2'
        else:
            data = input_data['grocery']
        return mockserver.make_response(
            json=bdu_orders_utils.generate_grocery_orders(data), status=200,
        )

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={'pagination_settings': {'limit': limit}, 'goods_items_limit': 2},
        headers=utils.get_auth_headers(eater_id=eater_id),
    )
    assert _mock_eats_ordershistory.times_called == 2
    assert _mock_grocery_gateaway.times_called == 2

    assert response.status_code == 200
    assert response.json()['pagination_settings'] == {
        'has_more': False,
        'cursor': '{"offset":3,"grocery_cursor":"1","version":"0.0"}',
    }
    assert response.json()['orders'] == bdu_orders_utils.generate_bdu_orders(
        expected_orders,
    )


@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={
        'tracking_enabled': True,
        'revisions_enabled': True,
        'restapp_enabled': True,
        'retail_enabled': True,
        'donation_enabled': False,
    },
)
@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY=True)
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=True)
@utils.can_be_removed_config3()
@utils.remove_enabled_config3()
@bdu_orders_utils.general_widget_config3()
@pytest.mark.pgsql('eats_orders_info', files=['remove_database.sql'])
@pytest.mark.parametrize(
    'input_json, expected_orders',
    [
        pytest.param(
            'bdu_source_data_not_removed.json',
            [
                {
                    'order_nr': '123-123-grocery',
                    'total_cost': 123.45,
                    'place_name': 'lavka',
                    'status': 'Подтвержден',
                    'created_at': '31 Октября 23:58, 2019',
                    'can_be_removed': False,
                },
                {
                    'order_nr': '123-123',
                    'total_cost': 384,
                    'place_name': 'Neverland',
                    'status': 'Подтвержден',
                    'created_at': '12 Октября 02:58, 2019',
                    'items': [
                        {
                            'name': 'pizza2',
                            'image_url': (
                                'product_pizza2_image_url_front/{w}x{h}'
                            ),
                        },
                    ],
                    'total_items_number': 2,
                    'can_be_removed': False,
                },
            ],
            id='not_removed_orders',
        ),
        pytest.param(
            'bdu_source_data_have_removed.json',
            [
                {
                    'order_nr': '123-123-grocery',
                    'total_cost': 123.45,
                    'place_name': 'lavka',
                    'status': 'Подтвержден',
                    'created_at': '31 Октября 23:58, 2019',
                    'can_be_removed': False,
                },
                {
                    'order_nr': '123-123',
                    'total_cost': 384,
                    'place_name': 'Neverland',
                    'status': 'Подтвержден',
                    'created_at': '12 Октября 02:58, 2019',
                    'items': [
                        {
                            'name': 'pizza2',
                            'image_url': (
                                'product_pizza2_image_url_front/{w}x{h}'
                            ),
                        },
                    ],
                    'total_items_number': 2,
                    'can_be_removed': False,
                },
                {
                    'order_nr': '124-124',
                    'total_cost': 100,
                    'place_name': 'Neverland',
                    'status': 'Завершен',
                    'created_at': '01 Декабря 02:58, 2019',
                    'can_be_removed': True,
                },
            ],
            id='have_removed_orders',
        ),
        pytest.param(
            'bdu_source_data_only_removed.json', [], id='only_removed_orders',
        ),
    ],
)
async def test_bdu_removed_orders(
        taxi_eats_orders_info,
        mock_orders_tracking_dummy,
        mock_feedback_dummy,
        mock_catalog_storage,
        mock_revision,
        mock_restapp,
        mock_retail,
        mockserver,
        load_json,
        input_json,
        expected_orders,
):
    eater_id = '22'
    input_data = load_json(input_json)

    @mockserver.json_handler(ORDERSHISTORY_URL)
    def _mock_eats_ordershistory(request):
        assert request.json['orders'] == 20
        assert request.json['offset'] == 0
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    input_data['ordershistory'],
                ),
            },
        )

    @mockserver.json_handler(GROCERY_URL)
    def _mock_grocery_gateaway(request):
        assert request.json['limit'] == 20
        return mockserver.make_response(
            json=bdu_orders_utils.generate_grocery_orders(
                input_data['grocery'],
            ),
            status=200,
        )

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={'pagination_settings': {'limit': 10}, 'goods_items_limit': 2},
        headers=utils.get_auth_headers(eater_id=eater_id),
    )
    assert _mock_eats_ordershistory.times_called == 1
    assert _mock_grocery_gateaway.times_called == 1

    assert response.status_code == 200
    assert response.json()['orders'] == bdu_orders_utils.generate_bdu_orders(
        expected_orders,
    )


@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={
        'tracking_enabled': True,
        'revisions_enabled': True,
        'restapp_enabled': True,
        'retail_enabled': True,
        'donation_enabled': False,
    },
)
@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY=True)
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=True)
@utils.can_be_removed_config3()
@utils.remove_enabled_config3()
@bdu_orders_utils.general_widget_config3()
@pytest.mark.pgsql('eats_orders_info', files=['remove_database.sql'])
@pytest.mark.parametrize(
    'input_json, expected_orders',
    [
        pytest.param(
            'bdu_source_data_not_removed.json',
            [
                {
                    'order_nr': '123-123-grocery',
                    'total_cost': 123.45,
                    'place_name': 'lavka',
                    'status': 'Подтвержден',
                    'created_at': '31 Октября 23:58, 2019',
                    'can_be_removed': False,
                },
                {
                    'order_nr': '123-123',
                    'total_cost': 384,
                    'place_name': 'Neverland',
                    'status': 'Подтвержден',
                    'created_at': '12 Октября 02:58, 2019',
                    'items': [
                        {
                            'name': 'pizza2',
                            'image_url': (
                                'product_pizza2_image_url_front/{w}x{h}'
                            ),
                        },
                    ],
                    'total_items_number': 2,
                    'can_be_removed': False,
                },
            ],
            id='not_removed_orders',
        ),
        pytest.param(
            'bdu_source_data_have_removed.json',
            [
                {
                    'order_nr': '124-124',
                    'total_cost': 100,
                    'place_name': 'Neverland',
                    'status': 'Завершен',
                    'created_at': '01 Декабря 02:58, 2019',
                    'can_be_removed': True,
                },
                {
                    'order_nr': '123-123-grocery',
                    'total_cost': 123.45,
                    'place_name': 'lavka',
                    'status': 'Подтвержден',
                    'created_at': '31 Октября 23:58, 2019',
                    'can_be_removed': False,
                },
                {
                    'order_nr': '123-123',
                    'total_cost': 384,
                    'place_name': 'Neverland',
                    'status': 'Подтвержден',
                    'created_at': '12 Октября 02:58, 2019',
                    'items': [
                        {
                            'name': 'pizza2',
                            'image_url': (
                                'product_pizza2_image_url_front/{w}x{h}'
                            ),
                        },
                    ],
                    'total_items_number': 2,
                    'can_be_removed': False,
                },
            ],
            id='have_removed_orders',
        ),
        pytest.param(
            'bdu_source_data_only_removed.json', [], id='only_removed_orders',
        ),
    ],
)
async def test_bdu_removed_refresh_orders(
        taxi_eats_orders_info,
        mock_orders_tracking_dummy,
        mock_feedback_dummy,
        mock_catalog_storage,
        mock_revision,
        mock_restapp,
        mock_retail,
        mockserver,
        load_json,
        input_json,
        expected_orders,
):
    eater_id = '22'
    input_order_nrs = [
        '124-124',
        '125-125',
        '123-123-grocery',
        '124-124-grocery',
        '123-123',
    ]
    input_data = load_json(input_json)

    @mockserver.json_handler(BATCH_ORDERSHISTORY_URL)
    def _mock_eats_ordershistory(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    input_data['ordershistory'],
                ),
            },
        )

    @mockserver.json_handler(BATCH_GROCERY_URL)
    def _mock_grocery_gateaway(request):
        return mockserver.make_response(
            json=bdu_orders_utils.generate_grocery_orders(
                input_data['grocery'],
            ),
            status=200,
        )

    response = await taxi_eats_orders_info.post(
        BDU_REFRESH_ORDERS_URL,
        json={'order_nrs': input_order_nrs},
        headers=utils.get_auth_headers(eater_id=eater_id),
    )
    assert _mock_eats_ordershistory.times_called == 1
    assert _mock_grocery_gateaway.times_called == 1

    assert response.status_code == 200
    assert response.json()['orders'] == bdu_orders_utils.generate_bdu_orders(
        expected_orders,
    )


@pytest.mark.parametrize(
    'input_orders, expected_orders',
    [
        pytest.param(
            [
                {
                    'id': '123-123',
                    'service': 'eats',
                    'comment': 'comment1',
                    'created_at': '2020-12-31 20:00:00',
                    'cart': {
                        'total': 123,
                        'total_rational': '123.4',
                        'place_slug': 'place',
                    },
                },
                {
                    'id': '125-125',
                    'service': 'shop',
                    'comment': 'comment1',
                    'created_at': '2020-12-31 20:00:00',
                    'cart': {
                        'total': 123,
                        'total_rational': '123.4',
                        'place_slug': 'place',
                    },
                },
                {
                    'id': '124-124-grocery',
                    'service': 'shop',
                    'comment': 'comment1',
                    'created_at': '2020-12-31 20:00:00',
                    'cart': {
                        'total': 123,
                        'total_rational': '123.4',
                        'place_slug': 'place',
                    },
                },
            ],
            [
                {
                    'id': '123-123',
                    'service': 'eats',
                    'comment': 'comment1',
                    'created_at': '2020-12-31 20:00:00',
                    'cart': {
                        'total': 123,
                        'total_rational': '123.4',
                        'place_slug': 'place',
                    },
                },
            ],
            id='have_removed_orders',
        ),
        pytest.param(
            [
                {
                    'id': '125-125',
                    'service': 'shop',
                    'comment': 'comment1',
                    'created_at': '2020-12-31 20:00:00',
                    'cart': {
                        'total': 123,
                        'total_rational': '123.4',
                        'place_slug': 'place',
                    },
                },
            ],
            [],
            id='only_removed_orders',
        ),
    ],
)
@utils.can_be_removed_config3()
@utils.remove_enabled_config3()
@pytest.mark.pgsql('eats_orders_info', files=['remove_database.sql'])
@pytest.mark.config(
    EATS_ORDERS_INFO_FALLBACK_FOR_FEEDBACKS={
        'enabled': False,
        'default_feedback_status': 'wait',
        'default_has_feedback': False,
    },
)
@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY=True)
async def test_orders_history(
        taxi_eats_orders_info,
        mockserver,
        local_services,
        grocery,
        input_orders,
        expected_orders,
):
    eater_id = '22'
    local_services.orders = input_orders
    local_services.core_headers = utils.get_auth_headers(eater_id=eater_id)

    @mockserver.json_handler(
        'persey-payments/internal/v1/charity/multibrand/ride_donations',
    )
    def ride_donations(request):
        return mockserver.make_response(status=200, json={'brands': []})

    response = await taxi_eats_orders_info.get(
        'api/v1/orders',
        json={'yandex_uid': utils.YA_UID},
        params={'limit': 11, 'offset': 0},
        headers=utils.get_auth_headers(eater_id=eater_id),
    )
    assert ride_donations.times_called == 1
    assert response.status_code == 200
    assert response.json() == expected_orders


@pytest.mark.parametrize(
    'input_orders, expected_response',
    [
        pytest.param(
            [
                {
                    'order_id': '123-123',
                    'service': 'eats',
                    'comment': 'comment1',
                    'created_at': '2017-01-01T12:00:27.87+00:00',
                    'calculation': {
                        'final_cost_decimal': '123',
                        'final_cost': '123.4',
                        'message': 'message',
                    },
                },
                {
                    'order_id': '124-124',
                    'service': 'eats',
                    'comment': 'comment1',
                    'created_at': '2017-01-01T12:00:27.87+00:00',
                    'calculation': {
                        'final_cost_decimal': '123',
                        'final_cost': '123.4',
                        'message': 'message',
                    },
                },
            ],
            {
                'orders': [
                    {
                        'order_id': '123-123',
                        'service': 'eats',
                        'comment': 'comment1',
                        'created_at': '2017-01-01T12:00:27.87+00:00',
                        'calculation': {
                            'final_cost': '123.4',
                            'message': 'message',
                        },
                    },
                    {
                        'order_id': '124-124',
                        'service': 'eats',
                        'comment': 'comment1',
                        'created_at': '2017-01-01T12:00:27.87+00:00',
                        'calculation': {
                            'final_cost': '123.4',
                            'message': 'message',
                        },
                    },
                ],
                'service_metadata': [],
            },
            id='not_removed_orders',
        ),
        pytest.param(
            [
                {
                    'order_id': '123-123',
                    'service': 'eats',
                    'comment': 'comment1',
                    'created_at': '2017-01-01T12:00:27.87+00:00',
                    'calculation': {
                        'final_cost_decimal': '123',
                        'final_cost': '123.4',
                        'message': 'message',
                    },
                },
                {
                    'order_id': '125-125',
                    'service': 'eats',
                    'comment': 'comment1',
                    'created_at': '2017-01-01T12:00:27.87+00:00',
                    'calculation': {
                        'final_cost_decimal': '123',
                        'final_cost': '123.4',
                        'message': 'message',
                    },
                },
            ],
            {
                'orders': [
                    {
                        'order_id': '123-123',
                        'service': 'eats',
                        'comment': 'comment1',
                        'created_at': '2017-01-01T12:00:27.87+00:00',
                        'calculation': {
                            'final_cost': '123.4',
                            'message': 'message',
                        },
                    },
                ],
                'service_metadata': [],
            },
            id='have_removed_orders',
        ),
        pytest.param(
            [
                {
                    'order_id': '125-125',
                    'service': 'eats',
                    'comment': 'comment1',
                    'created_at': '2017-01-01T12:00:27.87+00:00',
                    'calculation': {
                        'final_cost_decimal': '123',
                        'final_cost': '123.4',
                        'message': 'message',
                    },
                },
            ],
            {'orders': [], 'service_metadata': []},
            id='only_removed_orders',
        ),
    ],
)
@utils.can_be_removed_config3()
@utils.remove_enabled_config3()
@pytest.mark.pgsql('eats_orders_info', files=['remove_database.sql'])
async def test_superapp_orders_history(
        taxi_eats_orders_info,
        mockserver,
        local_services,
        input_orders,
        expected_response,
):
    eater_id = '22'
    local_services.superapp_response = {'orders': input_orders}
    local_services.exp_superapp_request_body = EXP_SUPERAPP_REQUEST_BODY
    local_services.core_headers = utils.get_auth_headers(eater_id=eater_id)

    @mockserver.json_handler(
        'persey-payments/internal/v1/charity/multibrand/ride_donations',
    )
    def ride_donations(request):
        return mockserver.make_response(status=200, json={'brands': []})

    response = await taxi_eats_orders_info.post(
        '/internal/eats-orders-info/v1/retrieve',
        json=SUPERAPP_REQUEST_BODY,
        headers={'Accept-Language': 'ru'},
    )
    assert local_services.mock_superapp_orders.times_called == 1
    assert ride_donations.times_called == 1
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'request_limit, expected_core_called, expected_response',
    [
        pytest.param(
            10,
            2,
            {
                'service_metadata': [
                    {
                        'service': 'eats',
                        'last_order_id': '123-123',
                        'name': 'Eats',
                    },
                ],
                'orders': [
                    {
                        'order_id': '123-123',
                        'service': 'eats',
                        'comment': 'comment1',
                        'created_at': '2018-01-01T12:00:27.87+00:00',
                        'calculation': {
                            'final_cost': '123.4',
                            'message': 'message',
                        },
                    },
                ],
            },
            id='default_iterations',
        ),
        pytest.param(
            1,
            1,
            {'service_metadata': [], 'orders': []},
            id='iterations_under_limit',
        ),
    ],
)
@utils.can_be_removed_config3()
@utils.remove_enabled_config3()
@pytest.mark.pgsql('eats_orders_info', files=['remove_database.sql'])
async def test_superapp_orders_history_iterations(
        taxi_eats_orders_info,
        mockserver,
        taxi_config,
        local_services,
        request_limit,
        expected_core_called,
        expected_response,
):
    taxi_config.set_values(
        {'EATS_ORDERS_INFO_REQUEST_LIMIT': {'limit': request_limit}},
    )
    eater_id = '22'
    local_services.core_headers = utils.get_auth_headers(eater_id=eater_id)
    input_orders = [
        {
            'order_id': '126-126',
            'service': 'eats',
            'comment': 'comment1',
            'created_at': '2019-01-01T12:00:27.87+00:00',
            'calculation': {
                'final_cost_decimal': '123',
                'final_cost': '123.4',
                'message': 'message',
            },
        },
        {
            'order_id': '125-125',
            'service': 'eats',
            'comment': 'comment1',
            'created_at': '2017-01-01T12:00:27.87+00:00',
            'calculation': {
                'final_cost_decimal': '123',
                'final_cost': '123.4',
                'message': 'message',
            },
        },
        {
            'order_id': '123-123',
            'service': 'eats',
            'comment': 'comment1',
            'created_at': '2018-01-01T12:00:27.87+00:00',
            'calculation': {
                'final_cost_decimal': '123',
                'final_cost': '123.4',
                'message': 'message',
            },
        },
        {
            'order_id': '124-124',
            'service': 'eats',
            'comment': 'comment1',
            'created_at': '2017-01-01T12:00:27.87+00:00',
            'calculation': {
                'final_cost_decimal': '123',
                'final_cost': '123.4',
                'message': 'message',
            },
        },
    ]
    service_metadata = [
        {'service': 'eats', 'last_order_id': '126-126', 'name': 'Eats'},
    ]

    @mockserver.json_handler(
        'eats-core-orders-superapp/internal-api/v1/orders/retrieve',
    )
    def superapp_orders(request):
        # sent hidden orders at first
        # after sent not hidden orders
        assert request.json['range']['results'] == 2
        response_orders = input_orders[0:2]
        if 'older_than' in request.json['range']:
            if request.json['range']['older_than'] == '125-125':
                response_orders = input_orders[2:4]
        return mockserver.make_response(
            status=200,
            json={
                'orders': response_orders,
                'service_metadata': service_metadata,
            },
        )

    @mockserver.json_handler(
        'persey-payments/internal/v1/charity/multibrand/ride_donations',
    )
    def ride_donations(request):
        return mockserver.make_response(status=200, json={'brands': []})

    response = await taxi_eats_orders_info.post(
        '/internal/eats-orders-info/v1/retrieve',
        json={
            'range': {'results': 1},
            'services': ['eats'],
            'user_identity': {
                'yandex_uid': 'uid',
                'bound_yandex_uids': [],
                'eater_ids': [],
            },
            'include_service_metadata': True,
        },
        headers={'Accept-Language': 'ru'},
    )
    assert superapp_orders.times_called == expected_core_called
    assert ride_donations.times_called == 1
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'order_nr, status, expected_code, expected_response_json',
    [
        pytest.param(
            '123-123',
            'finished',
            200,
            'expected_response_123-123.json',
            id='not_removed_order',
        ),
        pytest.param(
            '124-124-grocery',
            'confirmed',
            404,
            'expected_response_124-124-grocery.json',
            id='removed_order',
        ),
    ],
)
@utils.can_be_removed_config3()
@utils.remove_enabled_config3()
@pytest.mark.pgsql('eats_orders_info', files=['remove_database.sql'])
@pytest.mark.config(EATS_ORDERS_INFO_RECEIPTS_ENABLED={'enabled': False})
@utils.order_updater_config3()
@utils.order_details_titles_config3()
async def test_order_info(
        taxi_eats_orders_info,
        mockserver,
        load_json,
        local_services,
        order_nr,
        status,
        expected_code,
        expected_response_json,
):
    local_services.set_default(bus_type='eats')
    target_order = load_json(expected_response_json)
    eater_id = '22'

    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{order_nr}/metainfo',
    )
    def core_order_info(request):
        response_body = {
            'order_nr': order_nr,
            'location_latitude': 1,
            'location_longitude': 1,
            'business_type': 'restaurant',
            'city': '',
            'street': '',
            'is_asap': True,
            'status': status,
            'place_id': utils.PLACE_ID,
            'region_id': '1',
            'place_delivery_zone_id': '1',
            'app': 'web',
            'order_status_history': {
                'created_at': utils.SAMPLE_TIME_CONVERTED,
            },
            'order_user_information': {'eater_id': eater_id},
        }
        return mockserver.make_response(status=200, json=response_body)

    @mockserver.json_handler(
        'persey-payments/internal/v1/charity/multibrand/ride_donations',
    )
    def ride_donations(request):
        return mockserver.make_response(status=200, json={'brands': []})

    local_services.add_user_order(status=status, order_id=order_nr)
    local_services.add_order_customer_service(
        revision_id='0',
        customer_service_id='rest-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='100.00',
        order_id=order_nr,
        type_='composition_products',
        composition_products=[
            local_services.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='100.00',
                origin_id='item-0',
            ),
        ],
    )
    local_services.add_place_info(business='restaurant')
    local_services.core_headers = utils.get_auth_headers(eater_id=eater_id)
    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        params={'order_nr': order_nr},
        headers=utils.get_auth_headers(eater_id=eater_id),
    )

    assert core_order_info.times_called == 1
    assert response.status_code == expected_code
    if expected_code == 200:
        assert ride_donations.times_called == 1
        assert utils.format_response(response.json()) == target_order
    else:
        assert ride_donations.times_called == 0
        assert response.json() == {'code': '404', 'message': 'Order not found'}


@utils.can_be_removed_config3()
# @utils.remove_enabled_config3()
@pytest.mark.pgsql('eats_orders_info', files=['remove_database.sql'])
@pytest.mark.config(EATS_ORDERS_INFO_RECEIPTS_ENABLED={'enabled': False})
@utils.order_updater_config3()
@utils.order_details_titles_config3()
async def test_order_info_remove_disabled(
        taxi_eats_orders_info, mockserver, load_json, local_services,
):
    local_services.set_default(bus_type='eats')
    target_order = load_json('expected_response_125-125.json')
    eater_id = '22'
    order_nr = '125-125'

    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{order_nr}/metainfo',
    )
    def core_order_info(request):
        response_body = {
            'order_nr': order_nr,
            'location_latitude': 1,
            'location_longitude': 1,
            'business_type': 'restaurant',
            'city': '',
            'street': '',
            'is_asap': True,
            'status': 'cancelled',
            'place_id': utils.PLACE_ID,
            'region_id': '1',
            'place_delivery_zone_id': '1',
            'app': 'web',
            'order_status_history': {
                'created_at': utils.SAMPLE_TIME_CONVERTED,
            },
            'order_user_information': {'eater_id': eater_id},
        }
        return mockserver.make_response(status=200, json=response_body)

    @mockserver.json_handler(
        'persey-payments/internal/v1/charity/multibrand/ride_donations',
    )
    def ride_donations(request):
        return mockserver.make_response(status=200, json={'brands': []})

    local_services.add_user_order(status='cancelled', order_id=order_nr)
    local_services.add_order_customer_service(
        revision_id='0',
        customer_service_id='rest-product',
        customer_service_name='Расходы на исполнение поручений по заказу',
        cost_for_customer='100.00',
        order_id=order_nr,
        type_='composition_products',
        composition_products=[
            local_services.make_composition_product(
                id_='item_000-0',
                name='Яблоки',
                cost_for_customer='100.00',
                origin_id='item-0',
            ),
        ],
    )
    local_services.add_place_info(business='restaurant')
    local_services.core_headers = utils.get_auth_headers(eater_id=eater_id)
    response = await taxi_eats_orders_info.get(
        '/eats/v1/orders-info/v1/order',
        json={'yandex_uid': utils.YA_UID},
        params={'order_nr': order_nr},
        headers=utils.get_auth_headers(eater_id=eater_id),
    )

    assert core_order_info.times_called == 1
    assert response.status_code == 200
    assert ride_donations.times_called == 1
    assert utils.format_response(response.json()) == target_order
