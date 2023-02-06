import datetime

from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage

CONSUMER = 'eats-catalog-internal-place-promos'

NOW = '2022-07-04T17:57:08+03:00'

INFORMER_EXPERIMENT = experiments.always_match(
    name='eats_catalog_informer_testsuite',
    consumer=CONSUMER,
    value={
        'action': {
            'payload': {
                'text': 'exp text',
                'title': 'exp title',
                'type': 'bottom_sheet',
            },
            'type': 'bottom_sheet',
        },
        'background': {
            'dark': {'blue': 120, 'green': 242, 'red': 228},
            'light': {'blue': 210, 'green': 242, 'red': 228},
        },
        'icon': {'dark': 'http://expharold', 'light': 'http://exp/harold'},
        'id': 'promo_1',
        'text': {
            'color': {'dark': '#555555', 'light': '#FFFFFF'},
            'value': 'from experiment',
        },
    },
)

INFORMER_CONFIG = pytest.mark.config(
    PROMO_INFORMER_STYLE={
        '__default__': {
            'regular': {
                'text_color': {'light': '#72AA52', 'dark': '#72AA52'},
                'background_color': {
                    'dark': {'blue': 220, 'green': 242, 'red': 228},
                    'light': {'blue': 220, 'green': 242, 'red': 228},
                },
            },
            'ultima': {
                'text_color': {'light': '#21201F', 'dark': '#F5F4F2'},
                'background_color': {
                    'light': {'red': 228, 'green': 242, 'blue': 220},
                    'dark': {'red': 18, 'green': 18, 'blue': 17},
                },
                'icon': {
                    'light': 'http://ultima-promo-light',
                    'dark': 'http://ultima-promo-dark',
                },
            },
        },
    },
)


def informer_experiment(name: str):
    return experiments.always_match(
        name='eats_catalog_informer_' + name,
        consumer=CONSUMER,
        value={
            'action': {
                'payload': {
                    'text': 'exp text',
                    'title': 'exp title',
                    'type': 'bottom_sheet',
                },
                'type': 'bottom_sheet',
            },
            'background': {
                'dark': {'blue': 120, 'green': 242, 'red': 228},
                'light': {'blue': 210, 'green': 242, 'red': 228},
            },
            'icon': {'dark': 'http://expharold', 'light': 'http://exp/harold'},
            'id': 'promo_1',
            'text': {
                'color': {'dark': '#555555', 'light': '#FFFFFF'},
                'value': 'from experiment',
            },
        },
    )


def informers_limit(limit: int):
    return experiments.always_match(
        is_config=True,
        name='eats_catalog_informers',
        consumer=CONSUMER,
        value={'limit': limit},
    )


@pytest.fixture(name='place')
def create_place_fixture(eats_catalog_storage):

    current_time = parser.parse(NOW)
    start = current_time - datetime.timedelta(hours=3)
    end = current_time + datetime.timedelta(hours=3)

    def create_place(place_id: int, slug: str, is_ultima: bool = False):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                slug=slug,
                brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(start=start, end=end),
                ],
                features=storage.ZoneFeatures(is_ultima=is_ultima),
            ),
        )

    return create_place


@pytest.fixture(name='discount')
def create_discont_fixture(eats_discounts_applicator):
    hierarchy = 'place_delivery_discounts'

    def create_discount(place_id: int):
        eats_discounts_applicator.add_discount(
            discount_id='666',
            hierarchy_name=hierarchy,
            extra={
                'money_value': {
                    'menu_value': {'value_type': 'absolute', 'value': '10'},
                },
            },
        )
        eats_discounts_applicator.bind_discount(
            str(place_id), '666', hierarchy,
        )

    return create_discount


@pytest.mark.now(NOW)
@experiments.EATS_DISCOUNTS_ENABLE
@pytest.mark.parametrize(
    'expected_icon',
    [
        pytest.param(
            {'dark': 'picture_uri', 'light': 'picture_uri'},
            marks=INFORMER_CONFIG,
            id='icon_from_promo',
        ),
        pytest.param(
            {
                'light': 'http://icon-config-override/ligth',
                'dark': 'http://icon-config-override/dark',
            },
            marks=pytest.mark.config(
                PROMO_INFORMER_STYLE={
                    '__default__': {
                        'regular': {
                            'text_color': {
                                'light': '#72AA52',
                                'dark': '#72AA52',
                            },
                            'background_color': {
                                'dark': {
                                    'blue': 220,
                                    'green': 242,
                                    'red': 228,
                                },
                                'light': {
                                    'blue': 220,
                                    'green': 242,
                                    'red': 228,
                                },
                            },
                            'icon': {
                                'light': 'http://icon-config-override/ligth',
                                'dark': 'http://icon-config-override/dark',
                            },
                        },
                    },
                },
            ),
            id='icon_override',
        ),
    ],
)
async def test_informers_from_discounts(
        internal_place_promo, place, discount, expected_icon,
):
    """
    Проверяет, что скидка, заведенная в eats-discounts, вернется в информерах,
    в ручке /internal/v1/place/promo
    """

    place(place_id=1, slug='test_discounts')
    discount(place_id=1)

    response = await internal_place_promo(
        'test_discounts', {'lon': 37.591503, 'lat': 55.802998},
    )

    assert response.status_code == 200
    assert response.json() == {
        'informers': [
            {
                'action': {
                    'payload': {
                        'text': 'description',
                        'title': 'name',
                        'type': 'bottom_sheet',
                    },
                    'type': 'bottom_sheet',
                },
                'background': {
                    'dark': {'blue': 220, 'green': 242, 'red': 228},
                    'light': {'blue': 220, 'green': 242, 'red': 228},
                },
                'icon': expected_icon,
                'id': 'promo_101',
                'text': {
                    'color': {'dark': '#72AA52', 'light': '#72AA52'},
                    'value': 'name \u2013 description',
                },
            },
        ],
    }


@INFORMER_CONFIG
@pytest.mark.now(NOW)
@experiments.EATS_DISCOUNTS_ENABLE
async def test_informers_from_discounts_ultima(
        internal_place_promo, place, discount,
):
    """
    Проверяет, что скидка, заведенная в eats-discounts, вернется в информерах,
    в ручке /internal/v1/place/promo
    """

    place(102, 'test_discounts_ultima', True)
    discount(102)

    response = await internal_place_promo(
        'test_discounts_ultima', {'lon': 37.591503, 'lat': 55.802998},
    )

    assert response.status_code == 200
    assert response.json() == {
        'informers': [
            {
                'action': {
                    'payload': {
                        'text': 'description',
                        'title': 'name',
                        'type': 'bottom_sheet',
                    },
                    'type': 'bottom_sheet',
                },
                'background': {
                    'light': {'red': 228, 'green': 242, 'blue': 220},
                    'dark': {'red': 18, 'green': 18, 'blue': 17},
                },
                'icon': {
                    'light': 'http://ultima-promo-light',
                    'dark': 'http://ultima-promo-dark',
                },
                'id': 'promo_101',
                'text': {
                    'color': {'light': '#21201F', 'dark': '#F5F4F2'},
                    'value': 'name – description',
                },
            },
        ],
    }


@INFORMER_CONFIG
@pytest.mark.now(NOW)
async def test_informers_from_core_promos(
        internal_place_promo, mockserver, place,
):
    """
    Проверяет, что промка, заведенная в core, вернется в информерах,
    в ручке /internal/v1/place/promo
    """

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 1,
                    'name': 'Бесплатные тесты',
                    'description': 'При написании фичи, тесты в подарок',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 2, 'disabled_by_surge': False}],
                },
            ],
        }

    place(2, 'test_core_promos')

    response = await internal_place_promo(
        'test_core_promos', {'lon': 37.591503, 'lat': 55.802998},
    )

    assert response.status_code == 200
    assert response.json() == {
        'informers': [
            {
                'action': {
                    'payload': {
                        'text': 'При написании фичи, тесты в подарок',
                        'title': 'Бесплатные тесты',
                        'type': 'bottom_sheet',
                    },
                    'type': 'bottom_sheet',
                },
                'background': {
                    'dark': {'blue': 220, 'green': 242, 'red': 228},
                    'light': {'blue': 220, 'green': 242, 'red': 228},
                },
                'icon': {
                    'dark': 'http://istock/harold',
                    'light': 'http://istock/harold',
                },
                'id': 'promo_1',
                'text': {
                    'color': {'dark': '#72AA52', 'light': '#72AA52'},
                    'value': (
                        'Бесплатные тесты – При написании фичи, '
                        'тесты в подарок'
                    ),
                },
            },
        ],
    }


@pytest.mark.now(NOW)
@informer_experiment('testsuite')
async def test_informers_from_experiment(internal_place_promo, place):
    """
    Проверяет, информер, описанный в эксперименте, вернется в ручке
    /internal/v1/place/promo
    """

    place(3, 'test_experiments_promos')

    response = await internal_place_promo(
        'test_experiments_promos', {'lon': 37.591503, 'lat': 55.802998},
    )

    assert response.status_code == 200
    assert response.json() == {
        'informers': [
            {
                'action': {
                    'payload': {
                        'text': 'exp text',
                        'title': 'exp title',
                        'type': 'bottom_sheet',
                    },
                    'type': 'bottom_sheet',
                },
                'background': {
                    'dark': {'blue': 120, 'green': 242, 'red': 228},
                    'light': {'blue': 210, 'green': 242, 'red': 228},
                },
                'icon': {
                    'dark': 'http://expharold',
                    'light': 'http://exp/harold',
                },
                'id': 'promo_1',
                'text': {
                    'color': {'dark': '#555555', 'light': '#FFFFFF'},
                    'value': 'from experiment',
                },
            },
        ],
    }


@pytest.mark.now(NOW)
@INFORMER_CONFIG
async def test_informers_from_plus(internal_place_promo, place, mockserver):
    """
    Проверяет, что промка, заведенная в plus, вернется в информерах,
    в ручке /internal/v1/place/promo
    """

    place(4, 'test_plus_promo')

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/place',
    )
    def _eats_plus(_):
        return {
            'cashback': 18.0,
            'title': 'Баллами',
            'description': 'Вернём баллами на&nbsp;Плюс',
            'icon_url': 'asset://yandex_plus',
            'plus_details_form': {
                'title': 'Выгоднее с Плюсом',
                'description': (
                    'Подключите Яндекс Плюс, '
                    'чтобы получать кэшбэк за каждый заказ '
                    '(без учёта доставки и работы сервиса) '
                    'и обменивать баллы на покупки.'
                ),
                'button': {
                    'title': 'Подключить Плюс',
                    'deeplink': 'eda.yandex://plus/home',
                },
            },
            'plus_promos': [
                {
                    'id': 1,
                    'promo_type': {
                        'id': 200,
                        'name': 'Счастливые Часы для Плюсистов!',
                        'picture_uri': 'picture_uri',
                    },
                    'name': 'Счастливые Часы для Плюсистов!',
                    'description': 'Кешбек в счастливые часы!',
                },
            ],
        }

    response = await internal_place_promo(
        'test_plus_promo',
        {'lon': 37.591503, 'lat': 55.802998},
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'ios_app',
            'x-app-version': '6.1.0',
            'x-yandex-uid': '3456723',
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'informers': [
            {
                'action': {
                    'payload': {
                        'text': 'Кешбек в счастливые часы!',
                        'title': 'Счастливые Часы для Плюсистов!',
                        'type': 'bottom_sheet',
                    },
                    'type': 'bottom_sheet',
                },
                'background': {
                    'dark': {'blue': 220, 'green': 242, 'red': 228},
                    'light': {'blue': 220, 'green': 242, 'red': 228},
                },
                'icon': {'dark': 'picture_uri', 'light': 'picture_uri'},
                'id': 'promo_1',
                'text': {
                    'color': {'dark': '#72AA52', 'light': '#72AA52'},
                    'value': (
                        'Счастливые Часы для Плюсистов! – '
                        'Кешбек в счастливые часы!'
                    ),
                },
            },
        ],
    }


@pytest.mark.now(NOW)
@INFORMER_CONFIG
@informer_experiment('testsuite_1')
@informer_experiment('testsuite_2')
@informer_experiment('testsuite_3')
@informer_experiment('testsuite_4')
@pytest.mark.parametrize(
    'expected_count',
    [
        pytest.param(4, id='no limit'),
        pytest.param(0, marks=informers_limit(0), id='limit = 0'),
        pytest.param(2, marks=informers_limit(2), id='limit = 2'),
        pytest.param(4, marks=informers_limit(10), id='limit > size'),
    ],
)
async def test_informers_limit(internal_place_promo, place, expected_count):
    place(4, 'test_limit')

    response = await internal_place_promo(
        'test_limit', {'lon': 37.591503, 'lat': 55.802998},
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data['informers']) == expected_count
