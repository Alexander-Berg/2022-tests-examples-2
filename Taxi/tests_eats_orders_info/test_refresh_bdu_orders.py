import pytest

from tests_eats_orders_info import bdu_orders_utils
from tests_eats_orders_info import utils

BDU_REFRESH_ORDERS_URL = '/eats/v1/orders-info/v1/refresh-orders'
ORDERSHISTORY_URL = '/eats-ordershistory/internal/v2/get-orders/list'
GROCERY_URL = (
    '/grocery-eats-gateway/internal/grocery-eats-gateway/v1/batch-orders'
)

SAMPLE_TIME_CONVERTED = bdu_orders_utils.SAMPLE_TIME_CONVERTED_FOR_BDU_ORDERS


@pytest.fixture(name='mock_ordershistory_default')
def _mock_ordershistory_default(mockserver):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def mock(request):
        assert 'eater_ids' in request.json['filters']
        assert request.json['filters']['eater_ids'] == [21]
        return mockserver.make_response(
            status=200,
            json={
                'orders': bdu_orders_utils.generate_ordershistory_orders(
                    [
                        {
                            'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                            'place_id': int(bdu_orders_utils.PLACE_ID),
                            'total_cost': 123.45,
                            'created_at': (
                                bdu_orders_utils.SAMPLE_TIME_CONVERTED
                            ),
                            'order_type': 'native',
                            'status': 'finished',
                            'shipping_type': 'pickup',
                            'delivery_type': 'native',
                        },
                        {
                            'order_nr': 'active_order_nr',
                            'place_id': int(bdu_orders_utils.PLACE_ID),
                            'total_cost': 123.45,
                            'created_at': (
                                bdu_orders_utils.SAMPLE_TIME_CONVERTED
                            ),
                            'order_type': 'native',
                            'status': 'confirmed',
                            'delivery_type': 'native',
                            'shipping_type': 'pickup',
                        },
                    ],
                ),
            },
        )

    return mock


@pytest.mark.parametrize(
    ('input_order_nrs', 'exp_body'),
    [
        ({'order_nrs': []}, {'orders': []}),
        (
            {'order_nrs': [bdu_orders_utils.DEFAULT_ORDER_NR]},
            {
                'orders': bdu_orders_utils.generate_bdu_orders(
                    [
                        {
                            'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                            'total_cost': 123.45,
                            'place_name': bdu_orders_utils.PLACE_NAME,
                            'status': 'Завершен',
                            'created_at': SAMPLE_TIME_CONVERTED,
                            'show_feedback_button': True,
                        },
                    ],
                ),
            },
        ),
        (
            {
                'order_nrs': [
                    bdu_orders_utils.DEFAULT_ORDER_NR,
                    'active_order_nr',
                ],
            },
            {
                'orders': bdu_orders_utils.generate_bdu_orders(
                    [
                        {
                            'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                            'total_cost': 123.45,
                            'place_name': bdu_orders_utils.PLACE_NAME,
                            'status': 'Завершен',
                            'created_at': SAMPLE_TIME_CONVERTED,
                            'show_feedback_button': True,
                        },
                        {
                            'order_nr': 'active_order_nr',
                            'total_cost': 123.45,
                            'place_name': bdu_orders_utils.PLACE_NAME,
                            'status': 'Подтвержден',
                            'created_at': SAMPLE_TIME_CONVERTED,
                            'have_tracking': True,
                        },
                    ],
                ),
                'update_settings': {
                    'update_period': 50,
                    'order_nrs_to_update': ['active_order_nr'],
                },
            },
        ),
    ],
    ids=['empty_list', 'not_active_list', 'partly_active_list'],
)
@bdu_orders_utils.general_widget_config3()
@bdu_orders_utils.update_pagination_config3()
@bdu_orders_utils.feedback_widget_config3()
@pytest.mark.config(EATS_ORDERS_INFO_GET_ORDER_USE_FEEDBACKS_ENABLED=True)
@pytest.mark.config(
    EATS_ORDERS_INFO_BDU_ORDERS_SERVICE_ENABLED={
        'grocery_enabled': True,
        'tracking_enabled': True,
    },
)
async def test_refresh_orders(
        taxi_eats_orders_info,
        input_order_nrs,
        exp_body,
        mock_ordershistory_default,
        mock_catalog_storage_dummy,
        mockserver,
        taxi_eats_orders_info_monitor,
):
    await taxi_eats_orders_info.tests_control(reset_metrics=True)

    @mockserver.json_handler(bdu_orders_utils.TRACKING_URL)
    def _mock_tracking(request):
        return mockserver.make_response(
            status=200,
            json=bdu_orders_utils.generate_tracking_orders(
                [{'order_nr': 'active_order_nr'}],
            ),
        )

    @mockserver.json_handler(bdu_orders_utils.FEEDBACK_URL)
    def _mock_feedback(request):
        return mockserver.make_response(
            status=200,
            json={
                'feedbacks': [
                    {
                        'has_feedback': False,
                        'status': 'show',
                        'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                        'is_feedback_needed': True,
                    },
                ],
            },
        )

    response = await taxi_eats_orders_info.post(
        BDU_REFRESH_ORDERS_URL,
        json=input_order_nrs,
        headers=utils.get_auth_headers(),
    )
    assert mock_ordershistory_default.times_called == 1
    assert mock_catalog_storage_dummy.times_called == 1
    assert response.status_code == 200
    assert response.json() == exp_body

    orders_len = len(exp_body['orders'])
    if orders_len:
        metrics = await taxi_eats_orders_info_monitor.get_metric(
            'bdu-orders-info-metrics',
        )
        assert metrics['build_for_native']['general_widget'] == orders_len
        await taxi_eats_orders_info.tests_control(reset_metrics=True)


@pytest.mark.parametrize(
    ('grocery_body', 'grocery_code', 'exp_body'),
    [
        (
            {},
            500,
            {
                'orders': bdu_orders_utils.generate_bdu_orders(
                    [
                        {
                            'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                            'total_cost': 123.45,
                            'place_name': bdu_orders_utils.PLACE_NAME,
                            'status': 'Завершен',
                            'created_at': SAMPLE_TIME_CONVERTED,
                        },
                        {
                            'order_nr': 'active_order_nr',
                            'total_cost': 123.45,
                            'place_name': bdu_orders_utils.PLACE_NAME,
                            'status': 'Подтвержден',
                            'created_at': SAMPLE_TIME_CONVERTED,
                        },
                    ],
                ),
                'update_settings': {
                    'update_period': 50,
                    'order_nrs_to_update': ['active_order_nr'],
                },
            },
        ),
        (
            bdu_orders_utils.generate_grocery_orders(
                [
                    {
                        'created_at': '2021-08-06 15:42:12',
                        'id': '1',
                        'order_nr': 'grocery_not_active_order_nr',
                        'status': 'Какой-то статус',
                        'status_id': 5,
                        'total_cost': 100,
                    },
                    {
                        'created_at': '2021-08-06 15:42:12',
                        'id': '2',
                        'order_nr': 'grocery_active_order_nr',
                        'status': 'Какой-то статус',
                        'status_id': 1,
                        'total_cost': 100,
                    },
                ],
            ),
            200,
            {
                'orders': bdu_orders_utils.generate_bdu_orders(
                    [
                        {
                            'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                            'total_cost': 123.45,
                            'place_name': bdu_orders_utils.PLACE_NAME,
                            'status': 'Завершен',
                            'created_at': SAMPLE_TIME_CONVERTED,
                        },
                        {
                            'order_nr': 'active_order_nr',
                            'total_cost': 123.45,
                            'place_name': bdu_orders_utils.PLACE_NAME,
                            'status': 'Подтвержден',
                            'created_at': SAMPLE_TIME_CONVERTED,
                        },
                        {
                            'order_nr': 'grocery_not_active_order_nr',
                            'total_cost': 100,
                            'place_name': 'lavka',
                            'status': 'Отменен',
                            'created_at': SAMPLE_TIME_CONVERTED,
                        },
                        {
                            'order_nr': 'grocery_active_order_nr',
                            'total_cost': 100,
                            'place_name': 'lavka',
                            'status': 'Подтвержден',
                            'created_at': SAMPLE_TIME_CONVERTED,
                        },
                    ],
                ),
                'update_settings': {
                    'update_period': 50,
                    'order_nrs_to_update': [
                        'active_order_nr',
                        'grocery_active_order_nr',
                    ],
                },
            },
        ),
    ],
    ids=['grocery_error', 'with_grocery'],
)
@bdu_orders_utils.general_widget_config3()
@bdu_orders_utils.update_pagination_config3()
@bdu_orders_utils.feedback_widget_config3()
@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY=True)
async def test_refresh_orders_with_grocery(
        taxi_eats_orders_info,
        grocery_body,
        grocery_code,
        exp_body,
        mock_ordershistory_default,
        mock_catalog_storage_dummy,
        mockserver,
        taxi_eats_orders_info_monitor,
):
    @mockserver.json_handler(GROCERY_URL)
    def _mock_grocery_gateaway_batch(request):
        assert 'order_nrs' in request.json
        return mockserver.make_response(json=grocery_body, status=grocery_code)

    await taxi_eats_orders_info.tests_control(reset_metrics=True)
    response = await taxi_eats_orders_info.post(
        BDU_REFRESH_ORDERS_URL,
        json={
            'order_nrs': [
                bdu_orders_utils.DEFAULT_ORDER_NR,
                'active_order_nr',
                'grocery_not_active_order_nr',
                'grocery_active_order_nr',
            ],
        },
        headers=utils.get_auth_headers(),
    )
    assert mock_ordershistory_default.times_called == 1
    assert mock_catalog_storage_dummy.times_called == 1
    assert _mock_grocery_gateaway_batch.times_called == 1
    assert response.status_code == 200
    assert response.json() == exp_body
    metrics = await taxi_eats_orders_info_monitor.get_metric(
        'bdu-orders-info-metrics',
    )
    if grocery_code == 500:
        # error from grocery
        assert metrics['refresh_order_nr_not_found'] == 2
    else:
        assert metrics['refresh_order_nr_not_found'] == 0


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
        taxi_eats_orders_info_monitor,
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
                            'order_type': 'native',
                            'created_at': (
                                bdu_orders_utils.SAMPLE_TIME_CONVERTED
                            ),
                        },
                        {
                            'order_nr': 'unauthorized_donation',
                            'status': 'cancelled',
                            'order_type': 'native',
                            'place_id': int(bdu_orders_utils.PLACE_ID),
                            'total_cost': 123.45,
                            'created_at': (
                                bdu_orders_utils.SAMPLE_TIME_CONVERTED
                            ),
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

    await taxi_eats_orders_info.tests_control(reset_metrics=True)
    response = await taxi_eats_orders_info.post(
        BDU_REFRESH_ORDERS_URL,
        json={
            'order_nrs': [
                'finished_donation',
                'unauthorized_donation',
                'finished_donation_grocery',
                'unauthorized_donation_grocery',
            ],
        },
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
    }
    metrics = await taxi_eats_orders_info_monitor.get_metric(
        'bdu-orders-info-metrics',
    )
    assert metrics['refresh_order_nr_not_found'] == 0


@bdu_orders_utils.general_widget_config3()
@bdu_orders_utils.update_pagination_config3()
@bdu_orders_utils.feedback_widget_config3()
@pytest.mark.config(EATS_ORDERS_INFO_USE_GROCERY=True)
async def test_refresh_orders_not_found_order(
        taxi_eats_orders_info, mockserver, taxi_eats_orders_info_monitor,
):
    @mockserver.json_handler(ORDERSHISTORY_URL)
    def _mock_ordershistory_batch(request):
        assert 'order_ids' in request.json['filters']
        return mockserver.make_response(json={'orders': []}, status=200)

    @mockserver.json_handler(GROCERY_URL)
    def _mock_grocery_gateaway_batch(request):
        assert 'order_nrs' in request.json
        return mockserver.make_response(json=[], status=200)

    await taxi_eats_orders_info.tests_control(reset_metrics=True)
    response = await taxi_eats_orders_info.post(
        BDU_REFRESH_ORDERS_URL,
        json={'order_nrs': ['123', '124']},
        headers=utils.get_auth_headers(),
    )
    assert _mock_ordershistory_batch.times_called == 1
    assert _mock_grocery_gateaway_batch.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'orders': []}
    metrics = await taxi_eats_orders_info_monitor.get_metric(
        'bdu-orders-info-metrics',
    )
    assert metrics['refresh_order_nr_not_found'] == 2
