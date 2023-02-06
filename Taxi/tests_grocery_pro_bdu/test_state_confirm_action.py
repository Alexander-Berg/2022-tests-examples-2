import pytest

from tests_grocery_pro_bdu import models


SUPPORT_NAVIGATE_URL = (
    'https://taxi-frontend.taxi.tst.yandex.ru/' 'webview/driver-support/main'
)
NOT_ANSWERING_NAVIGATE_URL = (
    'https://taxi-frontend.taxi.tst.yandex.ru/'
    'webview/driver-support/documents/view/'
    'taximeter-lavka/from-order/not-contacted.html'
)


@pytest.mark.parametrize(
    'segment_status',
    [
        'pickuped',
        'returning',
        'delivery_arrived',
        'ready_for_delivery_confirmation',
        'pay_waiting',
        'return_arrived',
        'ready_for_return_confirmation',
    ],
)
@pytest.mark.experiments3(
    name='grocery_batch_skip_arrive_screen',
    consumers=['grocery-pro-bdu/skip'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'skip_arrive_screen': True},
    is_config=True,
)
@pytest.mark.experiments3(
    name='grocery_pro_bdu_common',
    consumers=['grocery-pro-bdu/common'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'support_navigate_url': SUPPORT_NAVIGATE_URL,
        'not_answering_navigate_url': NOT_ANSWERING_NAVIGATE_URL,
        'check_age_title_tanker_key': 'constructor.age_check_title',
        'check_age_title_modal_body_tanker_key': (
            'constructor.age_check_modal_body'
        ),
        'enable_confirm_action': True,
    },
    is_config=True,
)
@models.TIMER_CONFIG_ETA_TEXT
async def test_simple(
        taxi_grocery_pro_bdu,
        default_order_id,
        mockserver,
        my_waybill_at_client,
        segment_status,
):
    my_waybill_at_client['execution']['segments'][0]['status'] = segment_status

    @mockserver.json_handler('/cargo-orders/v1/pro-platform/order-info')
    def _mock_order_info(_request):
        return {
            'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_at_client,
        }

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/state',
        headers=models.AUTH_HEADERS_V1,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )

    assert response.status_code == 200

    assert response.json()['state']['point']['actions'][1] == {
        'button': 'actions.confirm.default_button',
        'cancel_button': 'actions.confirm.cancel_button',
        'message': 'actions.confirm.dropoff_message',
        'title': 'actions.confirm.dropoff_title',
        'type': 'confirm',
    }
