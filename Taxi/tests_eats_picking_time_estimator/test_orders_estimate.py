import pytest

from tests_eats_picking_time_estimator import utils


@pytest.mark.parametrize(
    'request_file, response_file',
    [
        pytest.param('success_request.json', 'success_response.json'),
        pytest.param(
            'success_exp_request.json',
            'success_exp_response.json',
            marks=[utils.picking_formula()],
        ),
    ],
)
async def test_estimate_exp_orders_success(
        taxi_eats_picking_time_estimator,
        load_json,
        load_orders,
        request_file,
        response_file,
):
    await estimate_picking_time(
        taxi_eats_picking_time_estimator,
        load_orders(request_file),
        200,
        load_json(response_file),
    )


async def post(
        taxi_eats_picking_time_estimator, url, data, expected_status_code,
):
    response = await taxi_eats_picking_time_estimator.post(url, data)
    assert response.status_code == expected_status_code, (
        response.status_code,
        expected_status_code,
        response.json(),
    )

    return response.json()


async def estimate_picking_time(
        taxi_eats_picking_time_estimator,
        data,
        expected_status_code,
        expected_response_json=None,
):
    response_json = await post(
        taxi_eats_picking_time_estimator,
        'api/v1/orders/estimate',
        data,
        expected_status_code,
    )

    if expected_response_json:
        assert expected_response_json == response_json, (
            expected_response_json,
            response_json,
        )

    return response_json
