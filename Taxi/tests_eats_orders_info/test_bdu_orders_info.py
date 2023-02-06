# pylint: disable=too-many-lines
import json

import pytest

from tests_eats_orders_info import bdu_orders_utils
from tests_eats_orders_info import utils

LIMIT = 100
OFFSET = 0

BDU_ORDERS_URL = '/eats/v1/orders-info/v1/orders'
ORDERSHISTORY_URL = '/eats-ordershistory/v2/get-orders'
GROCERY_URL = '/grocery-eats-gateway/internal/grocery-eats-gateway/v1/orders'
ORIGIN_ID_WITH_CHANGES = bdu_orders_utils.ORIGIN_ID_WITH_CHANGES


@pytest.fixture(name='mock_ordershistory_dummy')
def _mock_ordershistory_dummy(mockserver):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def _mock_eats_ordershistory(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    [
                        {
                            'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                            'status': 'confirmed',
                            'place_id': int(bdu_orders_utils.PLACE_ID),
                            'order_type': 'native',
                            'total_cost': 123.45,
                            'created_at': (
                                bdu_orders_utils.SAMPLE_TIME_CONVERTED
                            ),
                        },
                    ],
                ),
            },
        )

    return _mock_eats_ordershistory


@pytest.mark.parametrize(
    ('cursor', 'code', 'body', 'exp_code', 'exp_body', 'oh_times_called'),
    [
        (
            '{"offset": "so string"}',
            200,
            {'orders': []},
            400,
            {
                'message': 'Bad request with ordershistory cursor="so string"',
                'code': '400',
            },
            0,
        ),
        (
            'offset',
            200,
            {'orders': []},
            200,
            {
                'orders': [],
                'pagination_settings': {
                    'has_more': False,
                    'cursor': '{"offset":0,"version":"0.0"}',
                },
            },
            1,
        ),
        (
            '[{"offset": "so string"}]',
            200,
            {'orders': []},
            400,
            {
                'message': 'Bad request with cursor=[{"offset":"so string"}]',
                'code': '400',
            },
            0,
        ),
        (
            '{"offset": ' + str(OFFSET) + '}',
            400,
            {'message': 'message', 'code': '400'},
            400,
            {'message': 'message', 'code': '400'},
            1,
        ),
        (
            '{"offset": ' + str(OFFSET) + '}',
            500,
            {'message': 'message', 'code': '500'},
            500,
            {'message': 'Internal Server Error', 'code': '500'},
            1,
        ),
    ],
    ids=[
        'string_offset',
        'not_json_cursor',
        'not_object_cursor',
        'error_400',
        'error_500',
    ],
)  # using default limit from config
@bdu_orders_utils.update_pagination_config3()
async def test_common_ordershistory_fail(
        taxi_eats_orders_info,
        cursor,
        code,
        body,
        exp_code,
        exp_body,
        oh_times_called,
        grocery,
        mock_orders_tracking_dummy,
        mock_feedback_dummy,
        mockserver,
):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def _mock_eats_ordershistory(request):
        assert request.json['days'] == 111
        assert request.json['orders'] == 20  # check default from config limit
        return mockserver.make_response(status=code, json=body)

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={'pagination_settings': {'cursor': cursor}},
        headers=utils.get_auth_headers(),
    )
    assert _mock_eats_ordershistory.times_called == oh_times_called
    assert response.status_code == exp_code
    assert response.json() == exp_body


@pytest.mark.config(EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={})
@pytest.mark.parametrize(
    ('code', 'body', 'exp_body'),
    [
        (
            500,
            {'message': 'message', 'code': '500'},
            {'message': 'Internal Server Error', 'code': '500'},
        ),
    ],
    ids=['error_500'],
)
async def test_catalog_fail(
        taxi_eats_orders_info,
        code,
        body,
        exp_body,
        grocery,
        mock_ordershistory_dummy,
        mock_orders_tracking_dummy,
        mock_feedback_dummy,
        mockserver,
):
    @mockserver.json_handler(bdu_orders_utils.CATALOG_STORAGE_URL)
    def _mock_eats_catalog_storage(request):
        return mockserver.make_response(status=code, json=body)

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={
            'pagination_settings': {
                'cursor': '{"offset": ' + str(OFFSET) + '}',
                'limit': LIMIT,
            },
        },
        headers=utils.get_auth_headers(),
    )
    assert mock_ordershistory_dummy.times_called == 1
    assert _mock_eats_catalog_storage.times_called == 1
    assert response.status_code == code
    assert response.json() == exp_body


async def test_unauthorized(taxi_eats_orders_info, mock_ordershistory_dummy):
    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={
            'pagination_settings': {
                'cursor': '{"offset": ' + str(OFFSET) + '}',
                'limit': LIMIT,
            },
        },
    )
    assert mock_ordershistory_dummy.times_called == 0
    assert response.status_code == 401


@pytest.mark.parametrize(
    ('revision_code', 'revision_body_json', 'result_total_cost'),
    [
        (400, 'error.json', 123.45),
        (404, 'error.json', 123.45),
        (500, 'error.json', 123.45),
        (200, 'empty_customer_service.json', 123.45),
        (200, 'customer_service.json', 449.99),
    ],
    ids=[
        'error_400',
        'error_404',
        'error_500',
        'no_customer_products',
        'with_new_data',
    ],
)
@bdu_orders_utils.feedback_widget_config3()
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=False)
@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={
        'revisions_enabled': True,
        'restapp_enabled': False,
    },
)
@bdu_orders_utils.general_widget_config3()
async def test_bdu_goods_only_revision(
        taxi_eats_orders_info,
        revision_body_json,
        revision_code,
        result_total_cost,
        mock_catalog_storage_dummy,
        mockserver,
        load_json,
):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def mock_ordershistory(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    [
                        {
                            'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                            'status': 'confirmed',
                            'place_id': int(utils.PLACE_ID),
                            'order_type': 'native',
                            'total_cost': 123.45,
                            'created_at': utils.SAMPLE_TIME_CONVERTED,
                        },
                    ],
                ),
            },
        )

    @mockserver.json_handler(bdu_orders_utils.REVISIONS_URL)
    def mock_revision(request):
        assert request.method == 'POST'
        assert 'order_id' in request.json
        return mockserver.make_response(
            status=revision_code, json=load_json(revision_body_json),
        )

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={
            'pagination_settings': {
                'cursor': '{"offset": ' + str(OFFSET) + '}',
                'limit': LIMIT,
            },
        },
        headers=utils.get_auth_headers(),
    )
    assert mock_ordershistory.times_called == 1
    assert mock_catalog_storage_dummy.times_called == 1
    assert mock_revision.times_called == 1
    assert response.status_code == 200
    assert response.json()['orders'] == bdu_orders_utils.generate_bdu_orders(
        [
            {
                'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                'total_cost': result_total_cost,
                'place_name': utils.PLACE_NAME,
                'status': 'Подтвержден',
                'created_at': utils.SAMPLE_TIME_CONVERTED_FOR_BDU_ORDERS,
            },
        ],
    )


@bdu_orders_utils.feedback_widget_config3()
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=False)
@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={
        'revisions_enabled': False,
        'restapp_enabled': True,
    },
)
@bdu_orders_utils.general_widget_config3()
async def test_no_type_from_ordershistory(
        taxi_eats_orders_info,
        mock_catalog_storage_dummy,
        mockserver,
        load_json,
):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def mock_ordershistory(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    [
                        {
                            'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                            'status': 'confirmed',
                            'place_id': int(utils.PLACE_ID),
                            # 'order_type': 'native',
                            'total_cost': 123.45,
                            'created_at': utils.SAMPLE_TIME_CONVERTED,
                            'items': [
                                {'origin_id': 'origin_1', 'name': 'name'},
                            ],
                        },
                    ],
                ),
            },
        )

    @mockserver.json_handler(bdu_orders_utils.RESTAPP_URL)
    def mock_restapp(request):
        assert request.method == 'POST'
        assert request.json == {
            'places': [
                {  # data from dummy-revision
                    'place_id': utils.PLACE_ID,
                    'origin_ids': ['origin_1'],
                },
            ],
        }
        return mockserver.make_response(status=200, json={'places_items': []})

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={
            'pagination_settings': {
                'cursor': '{"offset": ' + str(OFFSET) + '}',
                'limit': LIMIT,
            },
        },
        headers=utils.get_auth_headers(),
    )
    assert mock_ordershistory.times_called == 1
    assert mock_catalog_storage_dummy.times_called == 1
    # default items source
    assert mock_restapp.times_called == 1
    assert response.status_code == 200
    assert response.json()['orders'] == bdu_orders_utils.generate_bdu_orders(
        [
            {
                'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                'total_cost': 123.45,
                'place_name': utils.PLACE_NAME,
                'status': 'Подтвержден',
                'created_at': '06 Августа 15:42, 2021',
            },
        ],
    )


@pytest.mark.parametrize(
    ('restapp_code', 'restapp_body', 'result_response_items'),
    [
        (400, {'code': 'code', 'message': 'message'}, {}),
        (404, {'code': 'code', 'message': 'message'}, {}),
        (500, {'code': 'code', 'message': 'message'}, {}),
        (
            200,
            {
                'places_items': [
                    {
                        'place_id': bdu_orders_utils.PLACE_ID,
                        'items': [
                            {
                                'origin_id': ORIGIN_ID_WITH_CHANGES,
                                'name': 'name',
                                'images': [],
                            },
                        ],
                    },
                ],
            },
            {},
        ),
        (
            200,
            {
                'places_items': [
                    {
                        'place_id': bdu_orders_utils.PLACE_ID,
                        'items': [
                            {
                                'origin_id': ORIGIN_ID_WITH_CHANGES,
                                'name': 'name',
                                'images': [
                                    'image_url_front',
                                    'image_url_back',
                                ],
                            },
                        ],
                    },
                ],
            },
            {
                'total_items_number': 2,
                'items': [
                    {
                        'name': 'Margarita',
                        'image_url': 'image_url_front/{w}x{h}',
                    },
                ],
            },
        ),
    ],
    ids=[
        'error_400',
        'error_404',
        'error_500',
        'empty_image_url',
        'with_image_url',
    ],
)
@bdu_orders_utils.feedback_widget_config3()
@bdu_orders_utils.general_widget_config3()
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=False)
@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={
        'revisions_enabled': True,
        'restapp_enabled': True,
    },
)
async def test_bdu_goods_only_restapp(
        taxi_eats_orders_info,
        restapp_body,
        restapp_code,
        result_response_items,
        mock_catalog_storage_dummy,
        mock_last_revisions_dummy,
        mockserver,
):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def mock_ordershistory(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    [
                        {
                            'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                            'status': 'confirmed',
                            'place_id': int(utils.PLACE_ID),
                            'total_cost': 123.45,
                            'created_at': utils.SAMPLE_TIME_CONVERTED,
                            'order_type': 'native',
                        },
                    ],
                ),
            },
        )

    @mockserver.json_handler(bdu_orders_utils.RESTAPP_URL)
    def mock_restapp(request):
        assert request.method == 'POST'
        assert request.json == {
            'places': [
                {  # data from dummy-revision
                    'place_id': utils.PLACE_ID,
                    'origin_ids': ['origin_123', 'origin_1'],
                },
            ],
        }
        return mockserver.make_response(status=restapp_code, json=restapp_body)

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={
            'pagination_settings': {
                'cursor': '{"offset": ' + str(OFFSET) + '}',
                'limit': LIMIT,
            },
        },
        headers=utils.get_auth_headers(),
    )
    assert mock_ordershistory.times_called == 1
    assert mock_catalog_storage_dummy.times_called == 1
    assert mock_last_revisions_dummy.times_called == 1
    assert mock_restapp.times_called == 1
    assert response.status_code == 200
    assert response.json()['orders'] == bdu_orders_utils.generate_bdu_orders(
        [
            {
                'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                'total_cost': 449.99,
                'place_name': utils.PLACE_NAME,
                'status': 'Подтвержден',
                'created_at': utils.SAMPLE_TIME_CONVERTED_FOR_BDU_ORDERS,
                **result_response_items,
            },
        ],
    )


@bdu_orders_utils.feedback_widget_config3()
@bdu_orders_utils.general_widget_config3()
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=False)
@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={
        'revisions_enabled': False,
        'restapp_enabled': True,
    },
)
async def test_bdu_goods_skip_options(
        taxi_eats_orders_info, mock_catalog_storage_dummy, mockserver,
):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def mock_ordershistory(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    [
                        {
                            'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                            'status': 'confirmed',
                            'place_id': int(utils.PLACE_ID),
                            'total_cost': 123.45,
                            'created_at': utils.SAMPLE_TIME_CONVERTED,
                            'order_type': 'native',
                            'items': [
                                {
                                    'name': 'Margarita',
                                    'origin_id': 'origin_123',
                                },
                                {
                                    'parent_origin_id': 'origin_123',
                                    'name': 'cheese',
                                },
                            ],
                        },
                    ],
                ),
            },
        )

    @mockserver.json_handler(bdu_orders_utils.RESTAPP_URL)
    def mock_restapp(request):
        assert request.method == 'POST'
        assert request.json == {
            'places': [
                {  # data from dummy-revision
                    'place_id': utils.PLACE_ID,
                    'origin_ids': ['origin_123'],
                },
            ],
        }
        return mockserver.make_response(
            status=200,
            json={
                'places_items': [
                    {
                        'place_id': bdu_orders_utils.PLACE_ID,
                        'items': [
                            {
                                'origin_id': 'origin_123',
                                'name': 'Margarita',
                                'images': [
                                    'image_url_front',
                                    'image_url_back',
                                ],
                            },
                        ],
                    },
                ],
            },
        )

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={
            'pagination_settings': {
                'cursor': '{"offset": ' + str(OFFSET) + '}',
                'limit': LIMIT,
            },
        },
        headers=utils.get_auth_headers(),
    )
    assert mock_ordershistory.times_called == 1
    assert mock_catalog_storage_dummy.times_called == 1
    assert mock_restapp.times_called == 1
    assert response.status_code == 200
    assert response.json()['orders'] == bdu_orders_utils.generate_bdu_orders(
        [
            {
                'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                'total_cost': 123.45,
                'place_name': utils.PLACE_NAME,
                'status': 'Подтвержден',
                'created_at': utils.SAMPLE_TIME_CONVERTED_FOR_BDU_ORDERS,
                'total_items_number': 1,
                'items': [
                    {
                        'name': 'Margarita',
                        'image_url': 'image_url_front/{w}x{h}',
                    },
                ],
            },
        ],
    )


@pytest.mark.parametrize(
    (
        'retail_code',
        'retail_body',
        'result_response_items',
        'result_total_amount',
    ),
    [
        (500, {'code': 'code', 'message': 'message'}, {}, 123.45),
        (
            200,
            {
                'orders': [
                    {
                        'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                        'total_amount': '384',
                        'items': [
                            {
                                'origin_id': ORIGIN_ID_WITH_CHANGES,
                                'name': 'Margarita',
                                'images_url_template': [],
                            },
                        ],
                    },
                ],
            },
            {},
            384,
        ),
        (
            200,
            {
                'orders': [
                    {
                        'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                        'total_amount': '384',
                        'items': [
                            {
                                'origin_id': ORIGIN_ID_WITH_CHANGES,
                                'name': 'Margarita',
                                'images_url_template': [
                                    'image_url_front/{w}x{h}',
                                    'image_url_back/{w}x{h}',
                                ],
                            },
                            {
                                'origin_id': ORIGIN_ID_WITH_CHANGES,
                                'name': 'Margarita2',
                                'images_url_template': [],
                            },
                        ],
                    },
                ],
            },
            {
                'total_items_number': 2,
                'items': [
                    {
                        'name': 'Margarita',
                        'image_url': 'image_url_front/{w}x{h}',
                    },
                ],
            },
            384,
        ),
    ],
    ids=['error_500', 'empty_image_url', 'with_image_url'],
)
@bdu_orders_utils.feedback_widget_config3()
@bdu_orders_utils.general_widget_config3()
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=False)
@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={'retail_enabled': True},
)
async def test_bdu_goods_only_retail(
        taxi_eats_orders_info,
        retail_body,
        retail_code,
        result_response_items,
        result_total_amount,
        mock_catalog_storage_dummy,
        mock_last_revisions_dummy,
        mockserver,
):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def mock_ordershistory(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    [
                        {
                            'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                            'status': 'confirmed',
                            'place_id': int(utils.PLACE_ID),
                            'order_type': 'retail',
                            'total_cost': 123.45,
                            'created_at': utils.SAMPLE_TIME_CONVERTED,
                            'source': 'eda',
                            'shipping_type': 'pickup',
                            'delivery_type': 'native',
                        },
                    ],
                ),
            },
        )

    @mockserver.json_handler(bdu_orders_utils.RETAIL_UPDATE_URL)
    def mock_retail(request):
        assert request.method == 'POST'
        assert 'order_nrs' in request.json
        return mockserver.make_response(status=retail_code, json=retail_body)

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={
            'pagination_settings': {
                'cursor': '{"offset": ' + str(OFFSET) + '}',
                'limit': LIMIT,
            },
        },
        headers=utils.get_auth_headers(),
    )
    assert mock_ordershistory.times_called == 1
    assert mock_catalog_storage_dummy.times_called == 1
    assert mock_last_revisions_dummy.times_called == 0
    assert mock_retail.times_called == 1
    assert response.status_code == 200
    assert response.json()['orders'] == bdu_orders_utils.generate_bdu_orders(
        [
            {
                'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                'total_cost': result_total_amount,
                'place_name': utils.PLACE_NAME,
                'status': 'Подтвержден',
                'created_at': utils.SAMPLE_TIME_CONVERTED_FOR_BDU_ORDERS,
                **result_response_items,
            },
        ],
    )


@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={'tracking_enabled': True},
)
@pytest.mark.parametrize(
    ('code', 'body', 'have_tracking'),
    [
        (400, {'message': 'message', 'code': '400'}, False),
        (500, {'message': 'message', 'code': '500'}, False),
        (200, bdu_orders_utils.generate_tracking_orders([]), False),
        (
            200,
            bdu_orders_utils.generate_tracking_orders(
                [{'order_nr': 'order_nr_no_in_history_now'}],
            ),
            False,
        ),
        (
            200,
            bdu_orders_utils.generate_tracking_orders(
                [{'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR}],
            ),
            True,
        ),
    ],
    ids=[
        'error_400',
        'error_500',
        'no_tracking_data',
        'tracking_data_without_history',
        'with_tracking_data',
    ],
)
@bdu_orders_utils.general_widget_config3()
async def test_bdu_orders_tracking(
        taxi_eats_orders_info,
        code,
        body,
        have_tracking,
        mock_ordershistory_dummy,
        mock_catalog_storage_dummy,
        mock_feedback_dummy,
        mockserver,
):
    @mockserver.json_handler(bdu_orders_utils.TRACKING_URL)
    def _mock_eats_orders_tracking(request):
        return mockserver.make_response(status=code, json=body)

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={
            'pagination_settings': {
                'cursor': '{"offset": ' + str(OFFSET) + '}',
                'limit': LIMIT,
            },
        },
        headers=utils.get_auth_headers(),
    )
    assert mock_ordershistory_dummy.times_called == 1
    assert mock_catalog_storage_dummy.times_called == 1
    assert _mock_eats_orders_tracking.times_called == 1
    assert response.status_code == 200
    assert response.json()['orders'] == bdu_orders_utils.generate_bdu_orders(
        [
            {
                'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                'total_cost': 123.45,
                'place_name': bdu_orders_utils.PLACE_NAME,
                'status': 'Подтвержден',
                'created_at': (
                    bdu_orders_utils.SAMPLE_TIME_CONVERTED_FOR_BDU_ORDERS
                ),
                'have_tracking': have_tracking,
            },
        ],
    )


@pytest.mark.parametrize(
    ('code', 'body', 'show_feedback_button'),
    [
        (400, {'message': 'message', 'code': '400'}, False),
        (500, {'message': 'message', 'code': '500'}, False),
        (200, bdu_orders_utils.generate_feedbacks_orders([]), False),
        (
            200,
            bdu_orders_utils.generate_feedbacks_orders(
                [
                    {
                        'order_nr': 'order_nr_no_in_history_now',
                        'status': 'show',
                        'has_feedback': False,
                        'is_feedback_needed': True,
                    },
                ],
            ),
            False,
        ),
        (
            200,
            bdu_orders_utils.generate_feedbacks_orders(
                [
                    {
                        'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                        'status': 'show',
                        'has_feedback': False,
                        'is_feedback_needed': True,
                    },
                ],
            ),
            True,
        ),
    ],
    ids=[
        'error_400',
        'error_500',
        'no_feedback_data',
        'feedback_data_without_history',
        'with_feedback_data',
    ],
)
@bdu_orders_utils.feedback_widget_config3()
@bdu_orders_utils.general_widget_config3()
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=True)
@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={'tracking_enabled': True},
)
async def test_bdu_feedbacks(
        taxi_eats_orders_info,
        code,
        body,
        show_feedback_button,
        mock_ordershistory_dummy,
        mock_catalog_storage_dummy,
        mock_orders_tracking_dummy,
        mockserver,
):
    @mockserver.json_handler(bdu_orders_utils.FEEDBACK_URL)
    def _mock_feedbacks(request):
        return mockserver.make_response(status=code, json=body)

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={
            'pagination_settings': {
                'cursor': '{"offset": ' + str(OFFSET) + '}',
                'limit': LIMIT,
            },
        },
        headers=utils.get_auth_headers(),
    )
    assert mock_ordershistory_dummy.times_called == 1
    assert mock_catalog_storage_dummy.times_called == 1
    assert mock_orders_tracking_dummy.times_called == 1
    assert _mock_feedbacks.times_called == 1
    assert response.status_code == 200
    assert response.json()['orders'] == bdu_orders_utils.generate_bdu_orders(
        [
            {
                'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                'total_cost': 123.45,
                'place_name': bdu_orders_utils.PLACE_NAME,
                'status': 'Подтвержден',
                'created_at': (
                    bdu_orders_utils.SAMPLE_TIME_CONVERTED_FOR_BDU_ORDERS
                ),
                'show_feedback_button': show_feedback_button,
            },
        ],
    )


@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY=False)
@bdu_orders_utils.general_widget_config3()
async def test_no_grocery_request(
        taxi_eats_orders_info, grocery, mock_ordershistory_dummy, mockserver,
):
    @mockserver.json_handler(bdu_orders_utils.CATALOG_STORAGE_URL)
    def mock_catalog_retrieve_places(request):
        return mockserver.make_response(
            status=200,
            json=bdu_orders_utils.generate_catalog_info(
                [
                    {
                        'id': int(bdu_orders_utils.PLACE_ID),
                        'name': bdu_orders_utils.PLACE_NAME,
                    },
                ],
                [],
            ),
        )

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={
            'pagination_settings': {
                'cursor': '{"offset": ' + str(OFFSET) + '}',
                'limit': LIMIT,
            },
        },
        headers=utils.get_auth_headers(),
    )

    assert mock_ordershistory_dummy.times_called == 1
    assert mock_catalog_retrieve_places.times_called == 1
    assert grocery.times_called_info() == 0
    assert response.status_code == 200


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
@pytest.mark.parametrize(
    'input_cursors, ordershistory_offset, grocery_cursor',
    [
        ({}, 0, None),
        ({'cursor': '{"offset": 2}'}, 2, None),
        (
            {'cursor': '{"grocery_cursor": "grocery-id", "version": "0"}'},
            0,
            'grocery-id',
        ),
        (
            {
                'cursor': (
                    '{"offset": 2, '
                    '"grocery_cursor": "grocery-id", "version": "0"}'
                ),
            },
            2,
            'grocery-id',
        ),
    ],
    ids=['none_cursors', 'only_cursor', 'only_grocery_cursor', 'all_cursors'],
)
@pytest.mark.parametrize(
    (
        'limit',
        'input_json',
        'has_more',
        'exp_orders_data',
        'exp_cursor',
        'exp_grocery_cursor',
        'required_data_times_called',
        'revisions_times_called',
        'restapp_times_called',
        'retail_times_called',
        'expected_update_settings',
    ),
    [
        (0, 'empty.json', False, [], 0, None, 0, 0, 0, 0, None),
        (  # not used revision data for goods widget, have lavka images
            3,
            'input_part_of_all.json',
            True,
            [
                {
                    'order_nr': '125-125',
                    'status': 'Завершен',
                    'place_name': 'Neverland',
                    'total_cost': 100.46,
                    'created_at': '01 Декабря 02:58, 2019',
                    'items': [
                        {
                            'name': 'pizza',
                            'image_url': 'pizza_image_url_front/{w}x{h}',
                        },
                    ],
                    'total_items_number': 2,
                },
                {
                    'order_nr': '123-123-grocery',
                    'total_cost': 123.45,
                    'place_name': 'lavka',
                    'status': 'Подтвержден',
                    'created_at': '31 Октября 23:58, 2019',
                    'total_items_number': 3,
                    'items': [
                        {
                            'name': 'kakao',
                            'image_url': 'lavka_image_url_kakao/{w}x{h}',
                        },
                        {
                            'name': 'ketchup',
                            'image_url': 'lavka_image_url_ketchup/{w}x{h}',
                        },
                    ],
                },
                {
                    'order_nr': '124-124-grocery',
                    'total_cost': 100,
                    'place_name': 'lavka',
                    'status': 'Завершен',
                    'created_at': '21 Октября 23:58, 2019',
                },
            ],
            1,
            '2',
            1,
            0,
            1,
            0,
            {'update_period': 60, 'order_nrs_to_update': ['123-123-grocery']},
        ),
        (  # used only revision data for goods widget
            5,
            'input_all.json',
            False,
            [
                {
                    'order_nr': '125-125',
                    'status': 'Завершен',
                    'place_name': 'Neverland',
                    'total_cost': 100.46,
                    'created_at': '01 Декабря 02:58, 2019',
                },
                {
                    'order_nr': '123-123-grocery',
                    'total_cost': 123.45,
                    'place_name': 'lavka',
                    'status': 'Подтвержден',
                    'created_at': '31 Октября 23:58, 2019',
                },
                {
                    'order_nr': '124-124-grocery',
                    'total_cost': 100,
                    'place_name': 'lavka',
                    'status': 'Завершен',
                    'created_at': '21 Октября 23:58, 2019',
                },
                {
                    'order_nr': '123-123',
                    'total_cost': 449.99,
                    'place_name': 'Neverland',
                    'status': 'Подтвержден',
                    'created_at': '12 Октября 02:58, 2019',
                    'items': [
                        {
                            'name': 'Margarita2',
                            'image_url': (
                                'pizza_revision_image_url_front/{w}x{h}'
                            ),
                        },
                    ],
                    'total_items_number': 1,
                },
            ],
            # 3 because 2 have in response,
            # one skipped because of catalog
            3,
            '2',
            1,
            1,
            1,
            0,
            {
                'update_period': 60,
                'order_nrs_to_update': ['123-123-grocery', '123-123'],
            },
        ),
        (  # used revision and source data for goods widget
            7,
            'input_more_then_all.json',
            False,
            [
                {  # order with images and retail types
                    'order_nr': '125-125',
                    'status': 'Завершен',
                    'place_name': 'Neverland',
                    'total_cost': 384,
                    'created_at': '01 Декабря 02:58, 2019',
                    'items': [
                        {
                            'name': 'pizza',
                            'image_url': (
                                'product_pizza_image_url_front/{w}x{h}'
                            ),
                        },
                    ],
                    'total_items_number': 1,
                },
                {
                    'order_nr': '123-123-grocery',
                    'total_cost': 123.45,
                    'place_name': 'lavka',
                    'status': 'Подтвержден',
                    'created_at': '31 Октября 23:58, 2019',
                },
                {
                    'order_nr': '124-124-grocery',
                    'total_cost': 100,
                    'place_name': 'lavka',
                    'status': 'Завершен',
                    'created_at': '21 Октября 23:58, 2019',
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
                },
            ],
            3,
            '2',
            1,
            0,
            0,
            1,
            {
                'update_period': 60,
                'order_nrs_to_update': ['123-123-grocery', '123-123'],
            },
        ),
    ],
    ids=[
        'get_zero',
        'get_part_of_all_source_origin_id',
        'get_all_revision_origin_id',
        'get_more_then_all_revision_origin_id',
    ],
)
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=True)
@bdu_orders_utils.general_widget_config3()
async def test_greenflow(
        taxi_eats_orders_info,
        limit,
        input_cursors,
        input_json,
        ordershistory_offset,
        grocery_cursor,
        exp_cursor,
        exp_grocery_cursor,
        has_more,
        exp_orders_data,
        expected_update_settings,
        required_data_times_called,
        revisions_times_called,
        restapp_times_called,
        retail_times_called,
        mock_orders_tracking_dummy,
        mock_feedback_dummy,
        mockserver,
        load_json,
):
    input_data = load_json(input_json)

    @mockserver.json_handler(ORDERSHISTORY_URL)
    def _mock_eats_ordershistory(request):
        assert request.json['orders'] == limit * 2
        assert request.json['offset'] == ordershistory_offset
        assert request.json['days'] == 180
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
        assert request.json['limit'] == limit * 2
        if grocery_cursor:
            assert request.json['older_than'] == grocery_cursor
        return mockserver.make_response(
            json=bdu_orders_utils.generate_grocery_orders(
                input_data['grocery'],
            ),
            status=200,
        )

    @mockserver.json_handler(bdu_orders_utils.CATALOG_STORAGE_URL)
    def _mock_eats_catalog_storage(request):
        return mockserver.make_response(
            json=bdu_orders_utils.generate_catalog_info(
                input_data['catalog']['found'],
                input_data['catalog']['not_found'],
            ),
            status=200,
        )

    @mockserver.json_handler(bdu_orders_utils.REVISIONS_URL)
    def mock_revision(request):
        assert request.method == 'POST'
        assert 'order_id' in request.json
        order_nr = request.json['order_id']
        return mockserver.make_response(
            status=200, json=load_json(input_json)['revisions'][order_nr],
        )

    @mockserver.json_handler(bdu_orders_utils.RESTAPP_URL)
    def mock_restapp(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=200, json=load_json('images.json')['restapp'],
        )

    @mockserver.json_handler(bdu_orders_utils.RETAIL_UPDATE_URL)
    def mock_retail(request):
        assert request.method == 'POST'
        assert 'order_nrs' in request.json
        return mockserver.make_response(
            status=200, json=load_json(input_json)['retail'],
        )

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={
            'pagination_settings': {'limit': limit, **input_cursors},
            'goods_items_limit': 2,
        },
        headers=utils.get_auth_headers(),
    )
    if limit:
        assert _mock_eats_ordershistory.times_called == 1
        assert _mock_grocery_gateaway.times_called == 1
    else:
        assert _mock_eats_ordershistory.times_called == 0
        assert _mock_grocery_gateaway.times_called == 0
    assert (
        _mock_eats_catalog_storage.times_called == required_data_times_called
    )
    assert mock_revision.times_called == revisions_times_called
    assert mock_restapp.times_called == restapp_times_called
    assert mock_retail.times_called == retail_times_called
    if limit != 0:
        assert mock_orders_tracking_dummy.times_called == 1
        assert mock_feedback_dummy.times_called == 1
    assert response.status_code == 200
    grocery_cursor_result = {}
    cursor_result = {'offset': ordershistory_offset + exp_cursor}
    if exp_grocery_cursor:
        grocery_cursor_result = {'grocery_cursor': exp_grocery_cursor}
    assert response.json()['orders'] == bdu_orders_utils.generate_bdu_orders(
        exp_orders_data,
    )
    result_pagination_settings = response.json()['pagination_settings']
    assert result_pagination_settings['has_more'] == has_more
    assert json.loads(result_pagination_settings['cursor']) == {
        'version': '0.0',
        **cursor_result,
        **grocery_cursor_result,
    }
    if expected_update_settings:
        assert response.json()['update_settings'] == expected_update_settings


@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY=True)
@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={'donation_enabled': True},
)
@bdu_orders_utils.general_widget_config3()
async def test_donations(
        taxi_eats_orders_info,
        mock_catalog_storage_dummy,
        mock_donations_bdu_orders,
        mockserver,
):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def _mock_eats_ordershistory(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    [
                        {
                            'order_nr': 'finished_donation',
                            'status': 'finished',
                            'place_id': int(bdu_orders_utils.PLACE_ID),
                            'total_cost': 123.45,
                            'created_at': (
                                bdu_orders_utils.SAMPLE_TIME_CONVERTED
                            ),
                            'order_type': 'native',
                            'shipping_type': 'pickup',
                            'delivery_type': 'native',
                        },
                        {
                            'order_nr': 'unauthorized_donation',
                            'status': 'cancelled',
                            'place_id': int(bdu_orders_utils.PLACE_ID),
                            'total_cost': 123.45,
                            'created_at': (
                                bdu_orders_utils.SAMPLE_TIME_CONVERTED
                            ),
                            'order_type': 'native',
                            'shipping_type': 'delivery',
                            'delivery_type': 'marketplace',
                        },
                    ],
                ),
            },
        )

    @mockserver.json_handler(GROCERY_URL)
    def _mock_grocery_gateaway(request):
        return mockserver.make_response(
            json=bdu_orders_utils.generate_grocery_orders(
                [
                    {
                        'created_at': '2019-10-31 23:58:59',
                        'id': '1',
                        'order_nr': 'finished_donation_grocery',
                        'status': 'Какой-то статус',
                        'status_id': 4,
                        'total_cost': 123.45,
                    },
                    {
                        'created_at': '2019-10-21 23:58:59',
                        'id': '2',
                        'order_nr': 'unauthorized_donation_grocery',
                        'status': 'Какой-то статус',
                        'status_id': 4,
                        'total_cost': 100.0,
                    },
                ],
            ),
            status=200,
        )

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={'pagination_settings': {'limit': LIMIT}},
        headers=utils.get_auth_headers(),
    )

    assert _mock_eats_ordershistory.times_called == 1
    assert _mock_grocery_gateaway.times_called == 1
    assert mock_catalog_storage_dummy.times_called == 1
    assert mock_donations_bdu_orders.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'orders': bdu_orders_utils.generate_bdu_orders(
            [
                {
                    'order_nr': 'finished_donation',
                    'total_cost': 128.45,
                    'place_name': utils.PLACE_NAME,
                    'status': 'Завершен',
                    'created_at': '06 Августа 15:42, 2021',
                },
                {
                    'order_nr': 'unauthorized_donation',
                    'total_cost': 123.45,
                    'place_name': utils.PLACE_NAME,
                    'status': 'Отменен',
                    'created_at': '06 Августа 15:42, 2021',
                },
                {
                    'order_nr': 'finished_donation_grocery',
                    'total_cost': 126.45,
                    'place_name': 'lavka',
                    'status': 'Завершен',
                    'created_at': '31 Октября 23:58, 2019',
                },
                {
                    'order_nr': 'unauthorized_donation_grocery',
                    'total_cost': 100,
                    'place_name': 'lavka',
                    'status': 'Завершен',
                    'created_at': '21 Октября 23:58, 2019',
                },
            ],
        ),
        'pagination_settings': {
            'cursor': '{"offset":2,"grocery_cursor":"2","version":"0.0"}',
            'has_more': False,
        },
    }


@pytest.mark.now('2022-09-06T12:42:12+00:00')
@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY=True)
@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={'donation_enabled': True},
)
@bdu_orders_utils.general_widget_config3()
async def test_equal_year_format(
        taxi_eats_orders_info,
        mock_catalog_storage_dummy,
        mock_donations_bdu_orders,
        mockserver,
):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def _mock_eats_ordershistory(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    [
                        {
                            'order_nr': 'finished_donation',
                            'status': 'finished',
                            'place_id': int(bdu_orders_utils.PLACE_ID),
                            'total_cost': 123.45,
                            'created_at': '2022-08-06T12:42:12+00:00',
                            'order_type': 'native',
                            'shipping_type': 'pickup',
                            'delivery_type': 'native',
                        },
                        {
                            'order_nr': 'unauthorized_donation',
                            'status': 'cancelled',
                            'place_id': int(bdu_orders_utils.PLACE_ID),
                            'total_cost': 123.45,
                            'created_at': (
                                bdu_orders_utils.SAMPLE_TIME_CONVERTED
                            ),
                            'order_type': 'native',
                            'shipping_type': 'delivery',
                            'delivery_type': 'marketplace',
                        },
                    ],
                ),
            },
        )

    @mockserver.json_handler(GROCERY_URL)
    def _mock_grocery_gateaway(request):
        return mockserver.make_response(json={}, status=200)

    response = await taxi_eats_orders_info.post(
        BDU_ORDERS_URL,
        json={'pagination_settings': {'limit': LIMIT}},
        headers=utils.get_auth_headers(),
    )

    assert _mock_eats_ordershistory.times_called == 1
    assert _mock_grocery_gateaway.times_called == 1
    assert mock_catalog_storage_dummy.times_called == 1
    assert mock_donations_bdu_orders.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'orders': bdu_orders_utils.generate_bdu_orders(
            [
                {
                    'order_nr': 'finished_donation',
                    'total_cost': 128.45,
                    'place_name': utils.PLACE_NAME,
                    'status': 'Завершен',
                    'created_at': '06 Августа 15:42',
                },
                {
                    'order_nr': 'unauthorized_donation',
                    'total_cost': 123.45,
                    'place_name': utils.PLACE_NAME,
                    'status': 'Отменен',
                    'created_at': '06 Августа 15:42, 2021',
                },
            ],
        ),
        'pagination_settings': {
            'cursor': '{"offset":2,"version":"0.0"}',
            'has_more': False,
        },
    }
