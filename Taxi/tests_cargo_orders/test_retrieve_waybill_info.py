import pytest


async def test_retrieve_waybill_info_order_not_found(
        taxi_cargo_orders,
        mock_waybill_info,
        yt_apply,
        load_json,
        my_waybill_info,
        default_order_id,
):
    response = await taxi_cargo_orders.post(
        '/v1/retrieve-waybill-info',
        json={'provider_order_id': 'unknown_order'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'order_not_found',
        'message': 'cargo order not found',
    }


@pytest.mark.parametrize(
    'dispatch_response_code, result_code, code, message, '
    'resolution, visit_status',
    [
        (200, 200, None, None, 'finished', 'visited'),
        (400, 500, '500', 'Internal Server Error', 'finished', 'visited'),
        (
            404,
            404,
            'waybill_not_found',
            'cargo waybill not found',
            'finished',
            'visited',
        ),
        (500, 500, '500', 'Internal Server Error', 'finished', 'visited'),
        (200, 200, None, None, 'cancelled_by_user', 'visited'),
        (200, 200, None, None, 'finished', 'pending'),
    ],
)
async def test_retrieve_waybill_info(
        taxi_cargo_orders,
        mockserver,
        yt_apply,
        load_json,
        my_waybill_info,
        default_order_id,
        dispatch_response_code: int,
        result_code: int,
        code: str,
        message: str,
        resolution: str,
        visit_status: str,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock_waybill_info(request):
        my_waybill_info['segments'][-1]['resolution'] = resolution
        my_waybill_info['execution']['points'][1][
            'visit_status'
        ] = visit_status
        return mockserver.make_response(
            json=my_waybill_info
            if dispatch_response_code == 200
            else {'code': 'not_found', 'message': 'some message'},
            status=dispatch_response_code,
        )

    response = await taxi_cargo_orders.post(
        '/v1/retrieve-waybill-info', json={'provider_order_id': 'taxi-order'},
    )
    assert response.status_code == result_code
    if result_code != 200:
        assert response.json() == {'code': code, 'message': message}
    else:
        assert response.json() == {
            'visited_endpoints_count': (
                1
                if resolution == 'finished' and visit_status == 'visited'
                else 0
            ),
        }
