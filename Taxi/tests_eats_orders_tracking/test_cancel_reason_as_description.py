# pylint: disable=unused-variable
import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'
MOCK_DATETIME = '2020-10-28T18:20:00.00+00:00'


@pytest.fixture(name='mock_eda_candidates_list_by_ids')
def _mock_eda_candidates_list_by_ids(mockserver):
    @mockserver.json_handler('/eda-candidates/list-by-ids')
    def _handler_eda_candidates_list_by_ids(request):
        assert len(request.json['ids']) == 1
        mock_response = {'candidates': [{'position': [20.22, 10.11]}]}
        return mockserver.make_response(json=mock_response, status=200)


@pytest.mark.config(
    EATS_ORDERS_TRACKING_CANCEL_REASON_TO_TANKER_KEY={
        'payment_failed': {
            'description_key': 'cancel_reason.payment_failed.description_key',
            'short_description_key': (
                'cancel_reason.payment_failed.short_description_key'
            ),
        },
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_green_flow(
        taxi_eats_orders_tracking,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers={'X-Eats-User': 'user_id=eater1'},
    )

    orders = response.json()['payload']['trackedOrders']
    assert len(orders) == 1

    order = orders[0]
    assert response.status_code == 200
    assert order['description'] == 'Заказ отменен по причине \'Ошибка оплаты\''
    assert order['ShortDescription'] == 'Заказ отменен'


@pytest.mark.config(
    EATS_ORDERS_TRACKING_CANCEL_REASON_TO_TANKER_KEY={
        'payment_failed': {
            'description_key': 'cancel_reason.payment_failed.description_key',
            'short_description_key': (
                'cancel_reason.payment_failed.short_description_key'
            ),
        },
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_order_not_cancelled(
        taxi_eats_orders_tracking,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers={'X-Eats-User': 'user_id=eater2'},
    )

    orders = response.json()['payload']['trackedOrders']
    assert len(orders) == 1

    order = orders[0]
    assert response.status_code == 200
    assert order['description'] == 'description'
    assert order['ShortDescription'] == 'short_description'


@pytest.mark.config(
    EATS_ORDERS_TRACKING_CANCEL_REASON_TO_TANKER_KEY={
        'duplicate': {
            'description_key': 'cancel_reason.duplicate.description_key',
            'short_description_key': (
                'cancel_reason.duplicate.short_description_key'
            ),
        },
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_order_no_config_key(
        taxi_eats_orders_tracking,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers={'X-Eats-User': 'user_id=eater1'},
    )

    orders = response.json()['payload']['trackedOrders']
    assert len(orders) == 1

    order = orders[0]
    assert response.status_code == 200
    assert order['description'] == 'description'
    assert order['ShortDescription'] == 'short_description'


@pytest.mark.config(
    EATS_ORDERS_TRACKING_CANCEL_REASON_TO_TANKER_KEY={
        'payment_failed': {
            'description_key': 'cancel_reason.payment_failed.description_key',
            'short_description_key': (
                'cancel_reason.payment_failed.short_description_key'
            ),
        },
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching_without_flag.json')
async def test_order_no_key_in_exp(
        taxi_eats_orders_tracking,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers={'X-Eats-User': 'user_id=eater1'},
    )

    orders = response.json()['payload']['trackedOrders']
    assert len(orders) == 1

    order = orders[0]
    assert response.status_code == 200
    assert order['description'] == 'description'
    assert order['ShortDescription'] == 'short_description'
