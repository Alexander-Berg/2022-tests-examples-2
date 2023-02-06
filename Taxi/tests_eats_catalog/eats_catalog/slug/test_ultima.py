from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage


TRANSLATIONS = {
    'eats-catalog': {
        'slug.ultima.action_text': {
            'ru': 'Ехала Ультма через Ультиму видит...',
        },
    },
}


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2022-06-27T10:52:43+03:00')
@configs.ultima_places(
    menu={
        'action': {
            'image': {
                'light': 'http://example.org/menu-light.png',
                'dark': 'http://example.org/menu-dark.png',
            },
            'deeplink': {
                'app': 'eda.yandex://ultima',
                'web': 'http://eda.yandex.ru/ultima',
            },
        },
    },
    places={
        'ultima_place': {
            'image': 'http://example.org/catlaog-image.png',
            'menu_image': {
                'light': 'http://example.org/menu-hero-photo-light.png',
                'dark': 'http://example.org/menu-hero-photo-dark.png',
            },
            'carousel_settings': {'items': []},
        },
    },
)
@pytest.mark.parametrize(
    'with_position',
    [
        pytest.param(True, id='with position'),
        pytest.param(False, id='no position'),
    ],
)
async def test_ultima_slug(slug, eats_catalog_storage, with_position):
    """
    Проверяет, что для заведений Ультима, при наличии переводов и конфигов
    возвращается экшн и изображение из конфига в ручке слага.
    """

    eats_catalog_storage.add_place(
        storage.Place(place_id=1, slug='ultima_place'),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2022-06-27T08:00:00+03:00'),
                    end=parser.parse('2022-06-27T12:00:00+03:00'),
                ),
            ],
            features=storage.ZoneFeatures(is_ultima=True),
        ),
    )

    query = {'latitude': 55.802998, 'longitude': 37.591503}
    if not with_position:
        query = {'latitude': None, 'longitude': None}

    response = await slug(slug='ultima_place', query=query)
    assert response.status_code == 200

    data = response.json()

    place = data['payload']['foundPlace']['place']

    assert place['image'] == {
        'light': {
            'ratio': 1.33,
            'uri': 'http://example.org/menu-hero-photo-light.png',
        },
        'dark': {
            'ratio': 1.33,
            'uri': 'http://example.org/menu-hero-photo-dark.png',
        },
    }

    expected_action = {
        'deeplink': {
            'app': 'eda.yandex://ultima',
            'web': 'http://eda.yandex.ru/ultima',
        },
        'text': 'Ехала Ультма через Ультиму видит...',
        'title': {
            'image': {
                'dark': 'http://example.org/menu-dark.png',
                'light': 'http://example.org/menu-light.png',
            },
        },
    }

    assert place['ultima_action'] == expected_action
    assert place['legacy_ultima_action'] == expected_action


UPPERCASE_NAME = experiments.always_match(
    is_config=True,
    name='eats_catalog_name_uppercase',
    consumer='eats-catalog-slug',
    value={'enabled': True},
)


@pytest.mark.parametrize(
    'name,expected_name',
    [
        pytest.param('nазваnиe 1', 'nазваnиe 1', id='normal'),
        pytest.param(
            'nазваnиe 2', 'NАЗВАNИE 2', marks=UPPERCASE_NAME, id='uppercase',
        ),
    ],
)
async def test_slug_uppercase_name(
        slug, eats_catalog_storage, name, expected_name,
):
    """
    Проверяет, что при включенном эксперименте название заведения приводится
    к верхнему регистру.
    """

    place_slug = 'test_place'

    eats_catalog_storage.add_place(
        storage.Place(place_id=1, slug=place_slug, name=name),
    )
    eats_catalog_storage.add_zone(storage.Zone(place_id=1, zone_id=1))

    response = await slug(slug=place_slug)

    data = response.json()

    assert data['payload']['foundPlace']['place']['name'] == expected_name


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.parametrize(
    'is_ultima,expected_delivery_class',
    (
        pytest.param(False, None, id='not_ultima'),
        pytest.param(True, 'ultima', id='ultima'),
    ),
)
async def test_slug_pricing_delivery_class(
        slug,
        eats_catalog_storage,
        delivery_price,
        is_ultima,
        expected_delivery_class,
):
    """
    Проверяет, что для ультимативного ресторана в прайсинг отправляется
    delivery_class_ultima
    """

    place_slug = 'test_place'

    eats_catalog_storage.add_place(storage.Place(place_id=1, slug=place_slug))
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            features=storage.ZoneFeatures(is_ultima=is_ultima),
        ),
    )

    @delivery_price.request_assertion
    def _pricing_request(request):
        assert request.json.get('delivery_class') == expected_delivery_class

    delivery_price.set_delivery_conditions(
        [
            {'order_price': 0, 'delivery_cost': 2023},
            {'order_price': 100, 'delivery_cost': 401},
            {'order_price': 10000, 'delivery_cost': 2},
        ],
    )

    response = await slug(slug=place_slug)

    assert delivery_price.times_called == 1
    assert response.status_code == 200
