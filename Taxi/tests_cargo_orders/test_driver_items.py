import pytest


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.parametrize(
    'waybill_tpl, point_id, expected_response',
    [
        pytest.param(
            'cargo-dispatch/v1_waybill_info_tpl.json',
            100500,
            {
                'items': [
                    {'detail': '1', 'title': 'title1', 'type': 'detail'},
                    {
                        'detail': '21861',
                        'title': 'title21861',
                        'type': 'detail',
                    },
                    {'detail': '78', 'title': 'title78', 'type': 'detail'},
                ],
            },
            id='destination_point',
        ),
        pytest.param(
            'cargo-dispatch/v1_waybill_info_tpl.json',
            100499,
            {
                'items': [
                    {
                        'horizontal_divider_type': 'top',
                        'markdown': True,
                        'subtitle': 'Точка выгрузски 1',
                        'title': '**Получение 1**',
                        'type': 'detail',
                    },
                    {'detail': '1', 'title': 'title1', 'type': 'detail'},
                    {
                        'detail': '21861',
                        'title': 'title21861',
                        'type': 'detail',
                    },
                    {
                        'horizontal_divider_type': 'top_bold',
                        'markdown': True,
                        'subtitle': 'Точка выгрузски 2',
                        'title': '**Получение 2**',
                        'type': 'detail',
                    },
                    {'detail': '998', 'title': 'title998', 'type': 'detail'},
                ],
            },
            id='source_point',
        ),
        pytest.param(
            'cargo-dispatch/v1_waybill_info_tpl.json',
            100600,
            {
                'items': [
                    {
                        'horizontal_divider_type': 'top',
                        'markdown': True,
                        'subtitle': 'Точка выгрузски 1',
                        'title': '**Возврат 1**',
                        'type': 'detail',
                    },
                    {'detail': '1', 'title': 'title1', 'type': 'detail'},
                    {
                        'detail': '21861',
                        'title': 'title21861',
                        'type': 'detail',
                    },
                    {
                        'horizontal_divider_type': 'top_bold',
                        'markdown': True,
                        'subtitle': 'Точка выгрузски 2',
                        'title': '**Возврат 2**',
                        'type': 'detail',
                    },
                    {'detail': '998', 'title': 'title998', 'type': 'detail'},
                ],
            },
            id='return_point',
        ),
        pytest.param(
            'cargo-dispatch/v1_waybill_info_tpl_partial_delivery.json',
            100500,
            {
                'items': [
                    {'detail': '1', 'title': 'title1', 'type': 'detail'},
                    {
                        'detail': '10000',
                        'title': 'title21861',
                        'type': 'detail',
                    },
                    {'detail': '8', 'title': 'title78', 'type': 'detail'},
                ],
            },
            id='destination_point_partial_delivery',
        ),
        pytest.param(
            'cargo-dispatch/v1_waybill_info_tpl_partial_delivery.json',
            100600,
            {
                'items': [
                    {
                        'horizontal_divider_type': 'top',
                        'markdown': True,
                        'subtitle': 'Точка выгрузски 1',
                        'title': '**Возврат 1**',
                        'type': 'detail',
                    },
                    {
                        'detail': '11861',
                        'title': 'title21861',
                        'type': 'detail',
                    },
                    {
                        'horizontal_divider_type': 'top_bold',
                        'markdown': True,
                        'subtitle': 'Точка выгрузски 2',
                        'title': '**Возврат 2**',
                        'type': 'detail',
                    },
                    {'detail': '899', 'title': 'title998', 'type': 'detail'},
                ],
            },
            id='return_point_partial_delivery',
        ),
    ],
)
async def test_driver_items(
        taxi_cargo_orders,
        mock_driver_tags_v1_match_profile,
        default_order_id,
        fetch_order,
        waybill_state,
        point_id,
        expected_response,
        waybill_tpl,
):
    waybill_state.load_waybill(waybill_tpl)
    cargo_ref_id = 'order/' + default_order_id
    response = await taxi_cargo_orders.get(
        'driver/v1/cargo-claims/v1/cargo/items'
        f'?cargo_ref_id={cargo_ref_id}&point_id={point_id}',
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


async def test_batch_first_point(
        taxi_cargo_orders,
        mock_driver_tags_v1_match_profile,
        default_order_id,
        mock_waybill_info,
        my_batch_waybill_info,
):
    cargo_ref_id = 'order/' + default_order_id
    response = await taxi_cargo_orders.get(
        'driver/v1/cargo-claims/v1/cargo/items'
        f'?cargo_ref_id={cargo_ref_id}&point_id=1',
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'detail': '1', 'title': 'batch_item_1_title', 'type': 'detail'},
        ],
    }
