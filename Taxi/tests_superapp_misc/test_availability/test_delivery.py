import pytest

from tests_superapp_misc.test_availability import consts
from tests_superapp_misc.test_availability import helpers


@pytest.mark.experiments3(
    # pay attention to superapp_delivery_availability predicate
    filename='exp3_delivery_availability.json',
)
@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['express', 'econom']},
)
@pytest.mark.parametrize(
    'expected_delivery_availability',
    [
        pytest.param(
            True,
            id='existing_delivery_category',
            marks=pytest.mark.config(
                SUPERAPP_MISC_DELIVERY_CATEGORIES=['express'],
            ),
        ),
        pytest.param(
            False,
            id='nonexisting_category',
            marks=pytest.mark.config(
                SUPERAPP_MISC_DELIVERY_CATEGORIES=[
                    'some_non_existing_category',
                ],
            ),
        ),
    ],
)
async def test_delivery_availability(
        taxi_superapp_misc, expected_delivery_availability,
):
    response = await taxi_superapp_misc.post(
        consts.URL,
        helpers.build_payload(),
        headers={'X-YaTaxi-UserId': 'user_id'},
    )
    assert response.status_code == 200
    delivery_mode = helpers.build_mode('delivery', available=True)
    delivery_available = delivery_mode in response.json()['modes']
    assert delivery_available == expected_delivery_availability
