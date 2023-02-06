from dateutil import parser
import pytest

from eats_catalog import storage
from . import layout_utils

ENABLE_PROLONGATION = pytest.mark.config(
    EATS_CATALOG_OFFER={'prolongation': {'catalog_for_layout': True}},
)

DISABLE_PROLONGATION = pytest.mark.config(
    EATS_CATALOG_OFFER={'prolongation': {'catalog_for_layout': False}},
)


@pytest.mark.parametrize(
    'expected_prolong',
    [
        pytest.param(True, id='prolong expected, default config'),
        pytest.param(
            True, id='prolong expected by config', marks=ENABLE_PROLONGATION,
        ),
        pytest.param(
            False,
            id='no prolong expected by config',
            marks=DISABLE_PROLONGATION,
        ),
    ],
)
@pytest.mark.parametrize(
    'expiration, expected_slugs',
    [
        pytest.param(
            '2021-09-17T18:25:00+03:00',
            {'preorder'},
            id='valid offer preorder',
        ),
        pytest.param(
            '1990-01-01T00:00:00+03:00', {'asap'}, id='expirerd offer',
        ),
    ],
)
@pytest.mark.now('2021-09-17T14:19:00+03:00')
async def test_offer(
        catalog_for_layout,
        offers,
        eats_catalog_storage,
        expiration,
        expected_slugs,
        expected_prolong,
):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug='asap', brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-09-17T10:00:00+03:00'),
                    end=parser.parse('2021-09-17T18:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2, slug='preorder', brand=storage.Brand(brand_id=2),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=2,
            zone_id=2,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-09-17T18:00:00+03:00'),
                    end=parser.parse('2021-09-17T20:00:00+03:00'),
                ),
            ],
        ),
    )

    offers.match_request(
        {
            'need_prolong': expected_prolong,
            'parameters': {'location': [37.591503, 55.802998]},
            'session_id': 'blablabla',
        },
    )

    offers.match_response(
        status=200,
        body={
            'session_id': 'hello',
            'request_time': '2021-09-17T10:00:00+03:00',
            'expiration_time': expiration,
            'prolong_count': 1,
            'parameters': {
                'location': [37.591503, 55.802998],
                'delivery_time': '2021-09-17T19:19:00+03:00',
            },
            'payload': {},
            'status': 'NO_CHANGES',
        },
    )

    response = await catalog_for_layout(
        [{'id': 'open', 'type': 'open', 'disable_filters': False}],
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-User': 'user_id=123',
            'X-Eats-Session': 'blablabla',
            'cookie': 'cookie',
        },
    )
    assert response.status_code == 200
    assert offers.match_times_called == 1

    block = layout_utils.find_block('open', response.json())

    slugs = {place['payload']['slug'] for place in block}

    assert slugs == expected_slugs
