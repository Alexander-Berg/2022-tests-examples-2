# pylint: disable=unused-variable
import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'


@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_widget_disabled.json')
async def test_disabled_widget_not_shown(
        taxi_eats_orders_tracking, make_tracking_headers,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    assert response.status_code == 200
    assert (
        'subtitle_with_action'
        not in response.json()['payload']['trackedOrders'][0]
    )


@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_invalid_deeplink_template.json')
async def test_invalid_deeplink_template(
        taxi_eats_orders_tracking, make_tracking_headers,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    assert response.status_code == 200
    assert response.json()['payload']['trackedOrders'][0][
        'subtitle_with_action'
    ] == {'text': 'Подзаголовок с действием'}


@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(
    filename='exp3_deeplink_template_without_placeholders.json',
)
async def test_deeplink_template_without_placeholders(
        taxi_eats_orders_tracking, make_tracking_headers,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    assert response.status_code == 200
    assert (
        response.json()['payload']['trackedOrders'][0]['subtitle_with_action']
        == {
            'text': 'Подзаголовок с действием',
            'destination_url': 'eda.yandex://orders',
        }
    )
