from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import umlaas


ENABLE_PROLONGATION = pytest.mark.config(
    EATS_CATALOG_OFFER={'prolongation': {'brand_slug': True}},
)

DISABLE_PROLONGATION = pytest.mark.config(
    EATS_CATALOG_OFFER={'prolongation': {'brand_slug': False}},
)


@pytest.mark.now('2021-11-16T12:25:00+03:00')
@pytest.mark.eats_regions_cache(
    [
        {
            'bbox': [35.918658, 54.805858, 39.133684, 56.473673],
            'center': [37.642806, 55.724266],
            'genitive': 'Moscow',
            'id': 1,
            'isAvailable': True,
            'isDefault': True,
            'name': 'Moscow',
            'slug': 'moscow',
            'sort': 1,
            'timezone': 'Europe/Moscow',
            'yandexRegionIds': [],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
    ],
)
@pytest.mark.parametrize(
    'query, umlaas_location',
    [
        pytest.param(
            {'latitude': 55.73442, 'longitude': 37.583948},
            {'lat': 55.73442, 'lon': 37.583948},
            id='with position',
        ),
        pytest.param(
            {'latitude': None, 'longitude': None},
            {'lat': 55.724266, 'lon': 37.642806},
            id='without position',
        ),
    ],
)
@experiments.always_match(
    name='eats_eta_provider',
    consumer='eats-catalog-time-prediction',
    value={
        'base_url': {'$mockserver': '/umlaas-eats'},
        'tvm_name': 'umlaas-eats',
    },
    is_config=True,
)
async def test_brand_slug(
        brand_slug, eats_catalog_storage, umlaas_eta, query, umlaas_location,
):

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-11-16T10:00:00+03:00'),
            end=parser.parse('2021-11-16T14:00:00+03:00'),
        ),
    ]

    for i in range(1, 11):
        umlaas_eta.set_eta(
            umlaas.UmlaasEta(place_id=i, eta_min=10, eta_max=20),
        )
        umlaas_eta.set_relevance(place_id=i, relevance=1000.0 - i)

        eats_catalog_storage.add_place(
            storage.Place(
                place_id=i,
                slug=f'place_slug_{i}',
                brand=storage.Brand(slug='test_brand_slug', brand_id=100),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(place_id=i, zone_id=i, working_intervals=schedule),
        )

    def check_umlaas_request(request):
        assert request.json['location'] == umlaas_location

    umlaas_eta.set_request_assert(check_umlaas_request)

    response = await brand_slug('test_brand_slug', query=query)

    assert response.status_code == 200
    assert umlaas_eta.times_called == 1

    data = response.json()
    place = data['payload']['foundPlace']['place']

    assert place['id'] == 1
    assert place['slug'] == 'place_slug_1'
    assert place['brand']['slug'] == 'test_brand_slug'


@pytest.mark.parametrize(
    'expected_prolong',
    [
        pytest.param(True, id='offer prolong expected, default config'),
        pytest.param(
            True,
            id='offer prolong expected by config',
            marks=ENABLE_PROLONGATION,
        ),
        pytest.param(
            False,
            id='no offer prolong expected by config',
            marks=DISABLE_PROLONGATION,
        ),
    ],
)
@experiments.always_match(
    name='eats_eta_provider',
    consumer='eats-catalog-time-prediction',
    value={
        'base_url': {'$mockserver': '/umlaas-eats'},
        'tvm_name': 'umlaas-eats',
    },
    is_config=True,
)
async def test_offer_prolongation_config(brand_slug, offers, expected_prolong):
    offers.match_request(
        {
            'need_prolong': expected_prolong,
            'parameters': {'location': [37.591503, 55.802998]},
            'session_id': 'blablabla',
        },
    )

    response = await brand_slug(
        'test_brand_slug',
        query={'longitude': 37.591503, 'latitude': 55.802998},
        headers={'X-Eats-User': 'user_id=123', 'X-Eats-Session': 'blablabla'},
    )

    assert response.status_code == 404
    assert offers.match_times_called == 1


@pytest.mark.now('2021-12-10T15:37:00+03:00')
@pytest.mark.parametrize(
    ['user_agent', 'strategy', 'response_code'],
    [
        pytest.param(
            'MagnitApp_Android/2.0.8',
            'whitelabel_only',
            200,
            id='magnitapp + whitelabel_only = 200',
        ),
        pytest.param(
            'MagnitApp_Android/2.0.8',
            'default',
            404,
            id='magnitapp + default = 404',
        ),
        pytest.param(
            'android_app', 'default', 200, id='android_app + default = 200',
        ),
        pytest.param(
            'android_app',
            'whitelabel_only',
            404,
            id='android_app + whitelabel_only = 404',
        ),
    ],
)
@experiments.always_match(
    name='eats_eta_provider',
    consumer='eats-catalog-time-prediction',
    value={
        'base_url': {'$mockserver': '/umlaas-eats'},
        'tvm_name': 'umlaas-eats',
    },
    is_config=True,
)
async def test_availablity_strategy(
        eats_catalog_storage, brand_slug, user_agent, strategy, response_code,
):
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-12-10T10:37:00+03:00'),
            end=parser.parse('2021-12-10T20:37:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            slug='test_place',
            brand=storage.Brand(slug='test_brand_slug', brand_id=100),
            features=storage.Features(availability_strategy=strategy),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(place_id=1, working_intervals=schedule),
    )

    response = await brand_slug(
        'test_brand_slug',
        query={'longitude': 37.591503, 'latitude': 55.802998},
        headers={'user-agent': user_agent},
    )

    assert response.status_code == response_code
