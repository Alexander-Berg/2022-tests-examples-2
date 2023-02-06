from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage


@pytest.mark.config(
    EATS_CATALOG_RESOLVER={
        'return_not_found_error': True,
        'is_pricing_enabled': False,
    },
)
@experiments.pickup_availability(new_flow=True)
@pytest.mark.parametrize(
    'delivery_time,status_code',
    [
        pytest.param(
            None,
            200,
            marks=pytest.mark.now('2022-01-31T16:40:00+03:00'),
            id='simple',
        ),
        pytest.param(
            '2022-01-31T13:47:00+03:00',
            404,
            marks=pytest.mark.now('2022-01-31T13:31:00+03:00'),
            id='preorder wont be ready',
        ),
        pytest.param(
            None,
            200,
            marks=pytest.mark.now('2022-01-31T13:31:00+03:00'),
            id='asap wont be ready',
        ),
        pytest.param(
            '2022-01-31T13:45:00+03:00',
            404,
            marks=pytest.mark.now('2022-01-31T13:20:00+03:00'),
            id='preorder before place open',
        ),
        pytest.param(
            None,
            200,
            marks=pytest.mark.now('2022-01-31T18:35:00+03:00'),
            id='less then 30 minutes before closing',
        ),
    ],
)
async def test_new_pickup_availability(
        taxi_eats_catalog, eats_catalog_storage, delivery_time, status_code,
):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, timing=storage.PlaceTiming(preparation=20 * 60),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2022-01-31T13:30:00+03:00'),
                    end=parser.parse('2022-01-31T19:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await taxi_eats_catalog.post(
        '/internal/v1/delivery-zones/resolve',
        json={
            'place_id': 1,
            'location': [37.591503, 55.802998],
            'delivery_time': delivery_time,
            'shipping_type': 'pickup',
        },
    )

    assert response.status_code == status_code
