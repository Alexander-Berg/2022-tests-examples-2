import pytest


@pytest.mark.parametrize(
    'lat,lon,depot_state,expected',
    [
        pytest.param(
            55,
            37,
            'available',
            {'exists': True, 'available': True},
            id='Open depot found',
        ),
        pytest.param(
            55,
            37,
            'closed',
            {'exists': True, 'available': False},
            id='Closed depot found',
        ),
        pytest.param(
            55,
            37,
            None,
            {'exists': False, 'available': False},
            id='No depot found',
        ),
    ],
)
async def test_availability(
        taxi_grocery_api, overlord_catalog, lat, lon, depot_state, expected,
):
    if depot_state is not None:
        overlord_catalog.add_location(
            location=[lon, lat],
            legacy_depot_id='100',
            depot_id='TheDepot',
            state=depot_state,
        )
        overlord_catalog.set_depot_status(depot_state)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/availability?latitude={}&longitude={}'.format(
            lat, lon,
        ),
    )

    assert response.json() == expected
