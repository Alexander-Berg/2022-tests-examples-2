# pylint: disable=C5521
# pylint: disable=C0302
import datetime

from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage

NOW = parser.parse('2021-01-01T12:00:00+03:00')

LOGO = [
    {
        'theme': 'dark',
        'value': [
            {
                'logo_url': (
                    'https://avatars.mds.yandex.net/get-eda/aaaaaa/214x140'
                ),
                'size': 'small',
            },
        ],
    },
]


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.eats_regions_cache(file='regions.json')
async def test_with_position_and_yandex_plus_widget(
        slug, mockserver, eats_catalog_storage,
):
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-01-01T10:00:00+03:00'),
            end=parser.parse('2021-01-01T14:00:00+03:00'),
        ),
        storage.WorkingInterval(
            start=parser.parse('2021-01-02T10:00:00+03:00'),
            end=parser.parse('2021-01-02T14:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            launched_at=NOW - datetime.timedelta(days=5),
            new_rating=storage.NewRating(show=False),
            features=storage.Features(
                constraints=[
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderPrice, 50000,
                    ),
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderWeight, 12,
                    ),
                ],
            ),
            timing=storage.PlaceTiming(extra_preparation=60.0),
            working_intervals=schedule,
        ),
    )
    eats_catalog_storage.add_zone(storage.Zone(working_intervals=schedule))

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
        }

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={'latitude': 0, 'longitude': 0},
        headers={
            'X-Yandex-UID': '3456723',
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-User': 'user_id=123',
            'X-Eats-Session': 'blablabla',
        },
    )

    assert response.status_code == 200

    no_promos_matched = {'promos': [], 'promoTypes': []}
    place = response.json()['payload']['foundPlace']['place']
    assert no_promos_matched.items() <= place.items()
    assert place['features']['yandexPlus'] is not None


@pytest.mark.parametrize(
    'business',
    [
        pytest.param(storage.Business.Restaurant),
        pytest.param(storage.Business.Shop),
    ],
)
@pytest.mark.parametrize(
    'hide_yaplus_meta, hide_retail_yaplus_meta',
    [
        pytest.param(
            True,
            True,
            marks=[
                experiments.eats_catalog_show_plus(
                    hide_plus=True,
                    hide_when_matched=False,
                    hide_when_matched_for_retail=False,
                    consumer='eats-catalog-slug',
                ),
            ],
            id='always hide meta',
        ),
        pytest.param(
            True,
            False,
            marks=[
                experiments.eats_catalog_show_plus(
                    hide_plus=False,
                    hide_when_matched=True,
                    hide_when_matched_for_retail=False,
                    consumer='eats-catalog-slug',
                ),
            ],
            id='hide meta for restaraunts',
        ),
        pytest.param(
            False,
            True,
            marks=[
                experiments.eats_catalog_show_plus(
                    hide_plus=False,
                    hide_when_matched=False,
                    hide_when_matched_for_retail=True,
                    consumer='eats-catalog-slug',
                ),
            ],
            id='hide meta for retail',
        ),
    ],
)
@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.eats_regions_cache(file='regions.json')
async def test_plus_promo_hide_yaplus_feature(
        slug,
        mockserver,
        eats_catalog_storage,
        business,
        hide_yaplus_meta,
        hide_retail_yaplus_meta,
):
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-01-01T10:00:00+03:00'),
            end=parser.parse('2021-01-01T14:00:00+03:00'),
        ),
        storage.WorkingInterval(
            start=parser.parse('2021-01-02T10:00:00+03:00'),
            end=parser.parse('2021-01-02T14:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            launched_at=NOW - datetime.timedelta(days=5),
            new_rating=storage.NewRating(show=False),
            features=storage.Features(
                constraints=[
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderPrice, 50000,
                    ),
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderWeight, 12,
                    ),
                ],
            ),
            timing=storage.PlaceTiming(extra_preparation=60.0),
            working_intervals=schedule,
            business=business,
        ),
    )
    eats_catalog_storage.add_zone(storage.Zone(working_intervals=schedule))

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

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={'latitude': 0, 'longitude': 0},
        headers={
            'X-Yandex-UID': '3456723',
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-User': 'user_id=123',
            'X-Eats-Session': 'blablabla',
        },
    )

    assert response.status_code == 200

    matched_plus_promos = {
        'promos': [
            {
                'description': 'Кешбек в счастливые часы!',
                'id': 1,
                'name': 'Счастливые Часы для Плюсистов!',
                'type': {
                    'detailedPictureUrl': None,
                    'id': 200,
                    'name': 'Счастливые Часы для Плюсистов!',
                    'pictureUri': 'picture_uri',
                },
            },
        ],
        'promoTypes': [
            {
                'detailedPictureUrl': None,
                'id': 200,
                'name': 'Счастливые Часы для Плюсистов!',
                'pictureUri': 'picture_uri',
            },
        ],
    }

    assert (
        matched_plus_promos.items()
        <= response.json()['payload']['foundPlace']['place'].items()
    )

    place = response.json()['payload']['foundPlace']['place']

    hiden_yaplus_meta = place['features']['yandexPlus'] is None

    if business == storage.Business.Shop:
        assert hiden_yaplus_meta == hide_retail_yaplus_meta
    else:
        assert hiden_yaplus_meta == hide_yaplus_meta
