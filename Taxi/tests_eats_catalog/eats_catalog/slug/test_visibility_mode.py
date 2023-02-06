from dateutil import parser
import pytest

from eats_catalog import storage


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@pytest.mark.parametrize(
    'visibility_mode, query, status_code, add_zone',
    [
        pytest.param(
            'preview',
            {'latitude': 55.73442, 'longitude': 37.583948},
            200,
            False,
            id='preview should show with position',
        ),
        pytest.param(
            'preview',
            None,
            200,
            False,
            id='preview should show without position',
        ),
        pytest.param(
            'preview',
            {'latitude': 55.73442, 'longitude': 37.583948},
            200,
            True,
            id='preview with zone should show with position',
        ),
        pytest.param(
            'preview',
            None,
            200,
            True,
            id='preview with zoneshould show without position',
        ),
        pytest.param(
            'on',
            {'latitude': 55.73442, 'longitude': 37.583948},
            404,
            False,
            id='on should not show without position',
        ),
        pytest.param(
            'on', None, 404, False, id='on should not show without position',
        ),
        pytest.param(
            'on',
            {'latitude': 55.73442, 'longitude': 37.583948},
            404,
            True,
            id='on with zone should not show without position',
        ),
        pytest.param(
            'on',
            None,
            404,
            True,
            id='on with zone should not show without position',
        ),
        pytest.param(
            'off',
            {'latitude': 55.73442, 'longitude': 37.583948},
            404,
            False,
            id='off should not show without position',
        ),
        pytest.param(
            'off', None, 404, False, id='off should show without position',
        ),
        pytest.param(
            'off',
            {'latitude': 55.73442, 'longitude': 37.583948},
            404,
            True,
            id='off with zone should not show without position',
        ),
        pytest.param(
            'off',
            None,
            404,
            True,
            id='off with zone should show without position',
        ),
    ],
)
async def test_visibility_mode(
        taxi_eats_catalog,
        eats_catalog_storage,
        visibility_mode,
        query,
        status_code,
        add_zone,
):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='disabled',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            features=storage.Features(visibility_mode=visibility_mode),
            enabled=False,
        ),
    )

    if add_zone:
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=10,
                place_id=1,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-01-01T10:00:00+00:00'),
                        end=parser.parse('2021-01-01T14:00:00+00:00'),
                    ),
                    storage.WorkingInterval(
                        start=parser.parse('2021-01-02T10:00:00+00:00'),
                        end=parser.parse('2021-01-02T14:00:00+00:00'),
                    ),
                ],
            ),
        )

    response = await taxi_eats_catalog.get(
        '/eats-catalog/v1/slug/disabled',
        params=query,
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
        },
    )

    assert response.status_code == status_code

    if status_code == 200:
        data = response.json()
        assert data['payload']['foundPlace']['place']['slug'] == 'disabled'
