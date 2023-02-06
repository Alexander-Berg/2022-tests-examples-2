import pytest


@pytest.mark.parametrize(
    'request_query, request_body, response_expected',
    [
        pytest.param(
            {'place_id': 1234},
            None,
            {'delivery_cost': 100.0},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '200',
                        'delivery_slot_interval': 240,
                        'skip_delivery_slots_count': 1,
                        'place_starts_work_at': '09:00',
                        'place_finishes_work_at': '22:00',
                    },
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET_OVERRIDE={
                        'overrides': [
                            {
                                'place_id': 1234,
                                'settings': {
                                    'delivery_cost': '100',
                                    'delivery_slot_interval': 120,
                                    'skip_delivery_slots_count': 0,
                                    'place_starts_work_at': '08:00',
                                    'place_finishes_work_at': '20:00',
                                },
                            },
                        ],
                    },
                ),
            ],
            id='no thresholds, integer, override',
        ),
        pytest.param(
            None,
            None,
            {'delivery_cost': 100.0},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '20:00',
                    },
                ),
            ],
            id='no thresholds, integer',
        ),
        pytest.param(
            None,
            None,
            {'delivery_cost': 100.0},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100.00',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '20:00',
                    },
                ),
            ],
            id='no thresholds, fractional with trailing zeros',
        ),
        pytest.param(
            None,
            None,
            {'delivery_cost': 99.99},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '99.99',
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='no thresholds, fractional',
        ),
        pytest.param(
            None,
            None,
            {'delivery_cost': 99.99},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '99.99',
                        'delivery_thresholds': [],
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='thresholds empty',
        ),
        pytest.param(
            None,
            None,
            {'delivery_cost': 100.0},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_thresholds': [
                            {'cart_cost': '0', 'delivery_cost': '100'},
                            {'cart_cost': '2999', 'delivery_cost': '0'},
                        ],
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='thresholds, no items',
        ),
        pytest.param(
            None,
            {
                'items': [
                    {'offerId': '1', 'price': 0, 'count': 300},
                    {'offerId': '2', 'price': 2999, 'count': 1},
                ],
            },
            {'delivery_cost': 0.0},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_thresholds': [
                            {'cart_cost': '0', 'delivery_cost': '100'},
                            {'cart_cost': '2999', 'delivery_cost': '0'},
                        ],
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='thresholds, item price is zero',
        ),
        pytest.param(
            None,
            {
                'items': [
                    {'offerId': '1', 'price': 300, 'count': 0},
                    {'offerId': '2', 'price': 2999, 'count': 1},
                ],
            },
            {'delivery_cost': 0.0},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_thresholds': [
                            {'cart_cost': '0', 'delivery_cost': '100'},
                            {'cart_cost': '2999', 'delivery_cost': '0'},
                        ],
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='thresholds, item count is zero',
        ),
        pytest.param(
            None,
            {'items': [{'offerId': '1', 'price': 0, 'count': 0}]},
            {'delivery_cost': 100.0},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_thresholds': [
                            {'cart_cost': '0', 'delivery_cost': '100'},
                            {'cart_cost': '2999', 'delivery_cost': '0'},
                        ],
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='thresholds, item price and count is zero',
        ),
        pytest.param(
            None,
            {
                'items': [
                    {'offerId': '1', 'price': 324.523, 'count': 3},
                    {'offerId': '2', 'price': 3.23, 'count': 3},
                ],
            },
            {'delivery_cost': 100.0},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_thresholds': [
                            {'cart_cost': '0', 'delivery_cost': '100'},
                            {'cart_cost': '2999', 'delivery_cost': '0'},
                        ],
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='thresholds, delivery cost 100',
        ),
        pytest.param(
            None,
            {
                'items': [
                    {'offerId': '1', 'price': 3000, 'count': 1},
                    {'offerId': '2', 'price': 3720, 'count': 1},
                ],
            },
            {'delivery_cost': 600.0},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_thresholds': [
                            {'cart_cost': '2999.9999', 'delivery_cost': '0'},
                            {'cart_cost': '100', 'delivery_cost': '200'},
                            {'cart_cost': '8000', 'delivery_cost': '400'},
                            {'cart_cost': '6000', 'delivery_cost': '600'},
                            {'cart_cost': '0', 'delivery_cost': '700'},
                        ],
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='thresholds sort, delivery cost 100',
        ),
        pytest.param(
            None,
            {'items': [{'offerId': '1', 'price': 2998.9999, 'count': 1}]},
            {'delivery_cost': 100},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_thresholds': [
                            {'cart_cost': '0', 'delivery_cost': '100'},
                            {'cart_cost': '2999', 'delivery_cost': '0'},
                        ],
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='thresholds boundary, delivery cost 100',
        ),
        pytest.param(
            None,
            {'items': [{'offerId': '1', 'price': 2999, 'count': 100}]},
            {'delivery_cost': 0},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_thresholds': [
                            {'cart_cost': '0', 'delivery_cost': '100.1111'},
                            {'cart_cost': '2999', 'delivery_cost': '0'},
                        ],
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='thresholds, delivery free',
        ),
        pytest.param(
            None,
            {'items': [{'offerId': '1', 'price': 2999, 'count': 100}]},
            {'delivery_cost': 100},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_thresholds': [
                            {'cart_cost': '0', 'delivery_cost': '100'},
                        ],
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='thresholds, delivery cost 100 only',
        ),
    ],
)
async def test_market_delivery_cost(
        taxi_eda_dynamic_delivery_fee,
        request_query,
        request_body,
        response_expected,
):
    if request_query:
        query = (
            '/v1/eda-dynamic-delivery-fee/market/delivery_cost?'
            'place_id={place_id}'.format(place_id=request_query['place_id'])
        )
    else:
        query = '/v1/eda-dynamic-delivery-fee/market/delivery_cost'

    response = await taxi_eda_dynamic_delivery_fee.post(
        query, headers={'Content-Type': 'application/json'}, json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == response_expected


@pytest.mark.parametrize(
    'request_body',
    [
        pytest.param(
            {'items': [{'offerId': '1', 'price': -100, 'count': 1}]},
            marks=[
                pytest.mark.config(
                    EDA_DYNAMIC_DELIVERY_FEE_MARKET={
                        'delivery_cost': '100',
                        'delivery_thresholds': [
                            {'cart_cost': '0', 'delivery_cost': '100'},
                            {'cart_cost': '2999', 'delivery_cost': '0'},
                        ],
                        'delivery_slot_interval': 120,
                        'skip_delivery_slots_count': 0,
                        'place_starts_work_at': '08:00',
                        'place_finishes_work_at': '23:00',
                    },
                ),
            ],
            id='thresholds, item negative price',
        ),
    ],
)
async def test_market_delivery_cost_400(
        taxi_eda_dynamic_delivery_fee, request_body,
):
    response = await taxi_eda_dynamic_delivery_fee.post(
        '/v1/eda-dynamic-delivery-fee/market/delivery_cost',
        headers={'Content-Type': 'application/json'},
        json=request_body,
    )
    assert response.status_code == 400
