import pytest

from tests_eats_picking_time_estimator import utils


@pytest.mark.config(
    EATS_PICKING_TIME_ESTIMATOR_CONFIDENCE_INTERVAL={
        'min_estimated_time_seconds': 300,
        'max_estimated_time_seconds': 7200,
    },
)
@pytest.mark.parametrize(
    'request_file, eta_seconds',
    [
        ['estimate_flow_packing_without_weight_items_request.json', 840],
        pytest.param(
            'estimate_flow_packing_without_weight_items_request.json',
            457,
            marks=[utils.picking_formula()],
        ),
        ['estimate_flow_handing_without_weight_items_request.json', 840],
        pytest.param(
            'estimate_flow_handing_without_weight_items_request.json',
            529,
            marks=[utils.picking_formula()],
        ),
        ['estimate_flow_packing_composite_items_request.json', 840],
        pytest.param(
            'estimate_flow_packing_composite_items_request.json',
            1537,
            marks=[utils.picking_formula()],
        ),
        pytest.param(
            'estimate_with_picked_items.json',
            1537,
            marks=[utils.picking_formula()],
        ),
        ['estimate_flow_packing_without_non_weight_items_request.json', 840],
        pytest.param(
            'estimate_flow_packing_without_non_weight_items_request.json',
            2617,
            marks=[utils.picking_formula()],
        ),
        ['estimate_flow_packing_multiple_categories_request.json', 840],
        pytest.param(
            'estimate_flow_packing_multiple_categories_request.json',
            457,
            marks=[utils.picking_formula()],
        ),
    ],
)
async def test_estimate_without_weight_items_request(
        taxi_eats_picking_time_estimator,
        load_order,
        request_file,
        eta_seconds,
):
    await estimate_picking_time(
        taxi_eats_picking_time_estimator,
        load_order(request_file),
        200,
        {'eta_seconds': eta_seconds},
    )


@pytest.mark.parametrize(
    'request_file',
    [
        'no_brand_composite_items_request.json',
        'no_place_composite_items_request.json',
        'no_items_request.json',
    ],
)
async def test_estimate_no_items_fail(
        taxi_eats_picking_time_estimator, load_order, request_file,
):
    await estimate_picking_time(
        taxi_eats_picking_time_estimator, load_order(request_file), 400,
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
        'api/v1/order/estimate',
        data,
        expected_status_code,
    )

    if expected_response_json:
        assert expected_response_json == response_json, (
            expected_response_json,
            response_json,
        )

    return response_json
