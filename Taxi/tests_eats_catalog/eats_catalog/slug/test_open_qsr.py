from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage


def check_pickup(response, is_expected=True):
    available_types = response['payload']['foundPlace']['locationParams'][
        'availableShippingTypes'
    ]

    assert ({'type': 'pickup'} in available_types) == is_expected


@pytest.mark.now('2021-03-10T13:50:00+00:00')
@experiments.qsr_pickup_user('special_user')
@experiments.couriers_pickup(brand_ids=[2])
@pytest.mark.parametrize(
    'request_slug, personal_phone_id, is_pickup_available',
    [
        pytest.param(
            'regular_pickup_place',
            'regular_user',
            True,
            id='regular user can see pickup in regular place',
        ),
        pytest.param(
            'special_pickup_place',
            'regular_user',
            False,
            id='regular user cannot see pickup in special place',
        ),
        pytest.param(
            'regular_pickup_place',
            'special_user',
            True,
            id='special user can see pickup in regular place',
        ),
        pytest.param(
            'special_pickup_place',
            'special_user',
            True,
            id='special user can see pickup in special place',
        ),
    ],
)
async def test_open_qsr_pickup(
        slug,
        eats_catalog_storage,
        request_slug,
        personal_phone_id,
        is_pickup_available,
):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='regular_pickup_place',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-10T10:00:00+00:00'),
                    end=parser.parse('2021-03-10T16:00:00+00:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='special_pickup_place',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-10T10:00:00+00:00'),
                    end=parser.parse('2021-03-10T16:00:00+00:00'),
                ),
            ],
        ),
    )

    response = await slug(
        request_slug,
        headers={
            'X-Eats-User': f'personal_phone_id={personal_phone_id}',
            'X-Eats-Session': 'blablabla',
        },
    )

    assert response.status_code == 200

    data = response.json()
    check_pickup(data, is_pickup_available)
