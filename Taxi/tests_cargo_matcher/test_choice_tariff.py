import pytest

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(
        CARGO_MATCHER_CARS=[
            {
                'carrying_capacity_kg': 10,
                'enabled': True,
                'height_cm': 50,
                'length_cm': 80,
                'max_loaders': 0,
                'taxi_class': 'courier',
                'width_cm': 50,
            },
            {
                'carrying_capacity_kg': 20,
                'enabled': True,
                'height_cm': 50,
                'length_cm': 100,
                'max_loaders': 0,
                'taxi_class': 'express',
                'width_cm': 60,
            },
            {
                'cargo_type': 'van',
                'cargo_type_limits_key': 'van',
                'enabled': True,
                'max_loaders': 2,
                'taxi_class': 'cargo',
            },
        ],
        CARGO_TYPE_LIMITS={
            'van': {
                'carrying_capacity_max_kg': 2001,
                'carrying_capacity_min_kg': 300,
                'height_max_cm': 201,
                'height_min_cm': 90,
                'length_max_cm': 290,
                'length_min_cm': 170,
                'requirement_value': 1,
                'width_max_cm': 201,
                'width_min_cm': 96,
            },
        },
    ),
]


@pytest.mark.parametrize(
    ('request_json', 'expected_json'),
    (
        (
            {
                'items': [
                    {
                        'quantity': 1,
                        'size': {
                            'height': 0.113,
                            'length': 0.212,
                            'width': 0.167,
                        },
                        'weight': 0.48,
                    },
                ],
            },
            {'taxi_tariff': 'courier'},
        ),
        (
            {
                'items': [
                    {
                        'quantity': 1,
                        'size': {
                            'height': 0.113,
                            'length': 0.212,
                            'width': 0.167,
                        },
                        'weight': 15,
                    },
                ],
            },
            {'taxi_tariff': 'express'},
        ),
        (
            {
                'items': [
                    {
                        'quantity': 1,
                        'size': {
                            'height': 0.113,
                            'length': 0.212,
                            'width': 0.167,
                        },
                        'weight': 100,
                    },
                ],
            },
            {
                'taxi_tariff': 'cargo',
                'taxi_requirements': {'cargo_type': 'van'},
            },
        ),
    ),
)
async def test_choice_tariff_success(
        taxi_cargo_matcher, request_json: dict, expected_json: dict,
):
    response = await taxi_cargo_matcher.post(
        '/v1/choice-tariff', json=request_json,
    )

    assert response.status_code == 200
    assert response.json() == expected_json


async def test_choice_tariff_to_large(taxi_cargo_matcher):
    response = await taxi_cargo_matcher.post(
        '/v1/choice-tariff',
        json={
            'items': [
                {
                    'quantity': 1,
                    'size': {'height': 0.113, 'length': 0.212, 'width': 0.167},
                    'weight': 30000,
                },
            ],
        },
    )

    assert response.status_code == 409
