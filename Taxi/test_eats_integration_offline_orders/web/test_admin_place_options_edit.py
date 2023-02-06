import http

import pytest


BODY = {
    'enabled': True,
    'show_tips': False,
    'payment_online': True,
    'payment_offline': False,
    'payment_split': True,
    'show_menu': True,
    'show_call_waiter': False,
    'parse_menu': False,
}


@pytest.mark.parametrize(
    ['params', 'request_body', 'expected_code', 'expected_response'],
    (
        pytest.param(
            {'place_id': 'place_id__1'},
            BODY,
            http.HTTPStatus.OK,
            {},
            id='ok-options-found',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'order_online': True, **BODY},
            http.HTTPStatus.OK,
            {},
            id='ok-order-online',
        ),
        pytest.param(
            {'place_id': 'place_id__2'},
            BODY,
            http.HTTPStatus.OK,
            {},
            id='ok-options-not-found',
        ),
        pytest.param(
            {'place_id': 'not-found'},
            BODY,
            http.HTTPStatus.NOT_FOUND,
            {'message': 'place not found', 'code': 'not_found'},
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'restaurants_options.sql'],
)
async def test_admin_place_options_edit(
        web_app_client,
        pgsql,
        params,
        request_body,
        expected_code,
        expected_response,
):
    response = await web_app_client.put(
        '/admin/v1/place/options', params=params, json=request_body,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if response.status != http.HTTPStatus.OK:
        return
    cursor = pgsql['eats_integration_offline_orders'].cursor()
    cursor.execute(
        f"""
        SELECT
            r.enabled,
            ro.show_tips,
            ro.show_menu,
            ro.show_call_waiter,
            ro.order_online,
            ro.payment_online,
            ro.payment_offline,
            ro.payment_split,
            ro.parse_menu
        FROM restaurants AS r
        LEFT JOIN restaurants_options AS ro
            ON r.place_id = ro.place_id
        WHERE r.place_id = '{params['place_id']}'
        ;
        """,
    )
    row = cursor.fetchone()
    assert row
    assert row[0] == request_body['enabled']
    assert row[1] == request_body['show_tips']
    assert row[2] == request_body['show_menu']
    assert row[3] == request_body['show_call_waiter']
    assert row[4] == request_body.get('order_online', False)
    assert row[5] == request_body['payment_online']
    assert row[6] == request_body['payment_offline']
    assert row[7] == request_body['payment_split']
    assert row[8] == request_body['parse_menu']
