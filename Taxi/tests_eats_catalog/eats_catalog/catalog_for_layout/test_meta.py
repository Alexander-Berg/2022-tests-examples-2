# pylint: disable=C0302
from dateutil import parser
import pytest

from testsuite.utils import matching

from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import translations
from . import layout_utils


@pytest.mark.parametrize(
    'shipping_type', [pytest.param('delivery'), pytest.param('pickup')],
)
@pytest.mark.now('2021-01-01T12:00:00+00:00')
async def test_yandex_plus(
        catalog_for_layout, eats_catalog_storage, mockserver, shipping_type,
):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
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
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=11,
            place_id=1,
            shipping_type=storage.ShippingType.Pickup,
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

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def eats_plus(request):
        assert request.headers['X-Device-Id'] == 'test_simple'
        assert request.json == {
            'yandex_uid': 'testsuite',
            'place_ids': [1],
            'shipping_type': shipping_type,
        }

        return {'cashback': [{'place_id': 1, 'cashback': 97.8210}]}

    filters = []
    if shipping_type == 'pickup':
        filters = [{'type': 'pickup', 'slug': 'pickup'}]

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
            'x-yandex-uid': 'testsuite',
        },
        filters=filters,
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert eats_plus.times_called == 1
    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)
    meta = layout_utils.find_first_meta('yandex_plus', place)

    assert meta == {
        'id': matching.UuidString(),
        'type': 'yandex_plus',
        'payload': {
            'text': '97.821%',
            'icon_url': 'asset://yandex-plus',
            'styles': {'border': True, 'rainbow': True},
        },
    }


@pytest.mark.parametrize(
    'shipping_type', [pytest.param('delivery'), pytest.param('pickup')],
)
@pytest.mark.now('2021-01-01T12:00:00+00:00')
async def test_yandex_plus_meta_with_tooltip(
        catalog_for_layout, eats_catalog_storage, mockserver, shipping_type,
):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open', place_id=2, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=2,
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
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=11,
            place_id=2,
            shipping_type=storage.ShippingType.Pickup,
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

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def eats_plus(request):
        assert request.headers['X-Device-Id'] == 'test_simple'
        assert request.json == {
            'yandex_uid': 'testsuite',
            'place_ids': [2],
            'shipping_type': shipping_type,
        }

        return {
            'cashback': [
                {
                    'place_id': 2,
                    'cashback': 123.321,
                    'tooltip': {
                        'title': 'Tooltip title',
                        'description': 'Tooltip description',
                    },
                },
            ],
        }

    filters = []
    if shipping_type == 'pickup':
        filters = [{'type': 'pickup', 'slug': 'pickup'}]

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
            'x-yandex-uid': 'testsuite',
        },
        filters=filters,
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert eats_plus.times_called == 1
    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)
    meta = layout_utils.find_first_meta('yandex_plus', place)

    assert meta == {
        'id': matching.UuidString(),
        'type': 'yandex_plus',
        'payload': {
            'text': '123.321%',
            'icon_url': 'asset://yandex-plus',
            'styles': {'border': True, 'rainbow': True},
            'details_form': {
                'title': 'Tooltip title',
                'description': 'Tooltip description',
            },
        },
    }


@pytest.mark.parametrize(
    'business',
    [
        pytest.param(storage.Business.Restaurant),
        pytest.param(storage.Business.Shop),
    ],
)
@pytest.mark.parametrize(
    'shipping_type', [pytest.param('delivery'), pytest.param('pickup')],
)
@pytest.mark.now('2021-01-01T12:00:00+00:00')
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
                    consumer='eats-catalog-for-layout',
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
                    consumer='eats-catalog-for-layout',
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
                    consumer='eats-catalog-for-layout',
                ),
            ],
            id='hide meta for retail',
        ),
    ],
)
async def test_yandex_plus_meta_show_plus_exp(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        shipping_type,
        business,
        hide_yaplus_meta,
        hide_retail_yaplus_meta,
):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open',
            place_id=2,
            brand=storage.Brand(brand_id=1),
            business=business,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=2,
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
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=11,
            place_id=2,
            shipping_type=storage.ShippingType.Pickup,
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

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def eats_plus(request):
        assert request.headers['X-Device-Id'] == 'test_simple'
        assert request.json == {
            'yandex_uid': 'testsuite',
            'place_ids': [2],
            'shipping_type': shipping_type,
        }

        return {
            'cashback': [
                {
                    'place_id': 2,
                    'cashback': 123.321,
                    'tooltip': {
                        'title': 'Tooltip title',
                        'description': 'Tooltip description',
                    },
                    'plus_promo_info_actions': [
                        {
                            'icon_url': 'icon_url',
                            'accent_color': [
                                {'theme': 'dark', 'value': '#bada55'},
                            ],
                            'title': 'title',
                            'description': 'description',
                            'extended': {
                                'title': 'Бесплатные тесты',
                                'content': (
                                    'При написании фичи, тесты в подарок'
                                ),
                                'button': {
                                    'title': 'Посмотреть всё',
                                    'url': 'url',
                                },
                            },
                        },
                    ],
                },
            ],
        }

    filters = []
    if shipping_type == 'pickup':
        filters = [{'type': 'pickup', 'slug': 'pickup'}]

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
            'x-yandex-uid': 'testsuite',
        },
        filters=filters,
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert eats_plus.times_called == 1
    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)

    if (
            hide_yaplus_meta
            and business != storage.Business.Shop
            or hide_retail_yaplus_meta
            and business == storage.Business.Shop
    ):
        layout_utils.assert_no_meta(place, 'yandex_plus')
    else:
        layout_utils.assert_has_meta(place, 'yandex_plus')


RATING_META_CONFIG = {
    'low': {
        'icon': {
            'color': [
                {'theme': 'light', 'value': '#NO0000'},
                {'theme': 'dark', 'value': '#NO0000'},
            ],
            'url': 'asset://no_rating_star',
        },
        'text': {
            'color': [
                {'theme': 'light', 'value': '#NO0000'},
                {'theme': 'dark', 'value': '#NO0000'},
            ],
            'text': '_',
            'text_key': 'rating_meta.low',
        },
    },
    'new': {
        'icon': {'color': [], 'url': 'asset://rating_star_new'},
        'text': {
            'color': [
                {'theme': 'light', 'value': '#NEW000'},
                {'theme': 'dark', 'value': '#NEW000'},
            ],
            'text': '_',
            'text_key': 'rating_meta.new',
        },
    },
    'regular': {
        'count_description': {'min_count': 201, 'text': '200+'},
        'icon_url': 'asset://rating_star',
        'thresholds': [
            {
                'icon_color': [
                    {'theme': 'light', 'value': '#ZERO00'},
                    {'theme': 'dark', 'value': '#ZERO00'},
                ],
                'min_rating': 0,
                'text_color': [
                    {'theme': 'light', 'value': '#ZERO00'},
                    {'theme': 'dark', 'value': '#ZERO00'},
                ],
            },
            {
                'icon_color': [
                    {'theme': 'light', 'value': '#LOW000'},
                    {'theme': 'dark', 'value': '#LOW000'},
                ],
                'min_rating': 4.5,
                'text_color': [
                    {'theme': 'light', 'value': '#LOW000'},
                    {'theme': 'dark', 'value': '#LOW000'},
                ],
            },
            {
                'additional_description': '_',
                'additional_description_key': 'rating_meta.good',
                'icon_color': [
                    {'theme': 'light', 'value': '#GOOD00'},
                    {'theme': 'dark', 'value': '#GOOD00'},
                ],
                'min_rating': 4.7,
                'text_color': [
                    {'theme': 'light', 'value': '#GOOD00'},
                    {'theme': 'dark', 'value': '#GOOD00'},
                ],
            },
            {
                'additional_description': '_',
                'additional_description_key': 'rating_meta.great',
                'icon_color': [
                    {'theme': 'light', 'value': '#GREAT0'},
                    {'theme': 'dark', 'value': '#GREAT0'},
                ],
                'min_rating': 4.9,
                'text_color': [
                    {'theme': 'light', 'value': '#GREAT0'},
                    {'theme': 'dark', 'value': '#GREAT0'},
                ],
            },
        ],
    },
    'top': {
        'icon': {'color': [], 'url': 'asset://flame'},
        'tag': 'top_rating',
        'text': {
            'color': [
                {'theme': 'light', 'value': '#TOP000'},
                {'theme': 'dark', 'value': '#TOP000'},
            ],
            'text': '_',
            'text_key': 'rating_meta.top',
        },
    },
}


RATING_META_TRANSLATIONS = {
    'eats-catalog': {
        'rating_meta.top': {'ru': 'Входит в Топ'},
        'rating_meta.great': {'ru': 'Отлично'},
        'rating_meta.good': {'ru': 'Хорошо'},
        'rating_meta.new': {'ru': 'Новый'},
        'rating_meta.low': {'ru': 'Мало оценок'},
    },
}


@pytest.mark.now('2021-04-03T19:13:00+00:00')
@pytest.mark.config(EATS_CATALOG_RATING_META=RATING_META_CONFIG)
@pytest.mark.translations(**RATING_META_TRANSLATIONS)
async def test_rating_meta_color(catalog_for_layout, eats_catalog_storage):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='zero_rating',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            new_rating=storage.NewRating(show=True, rating=0, count=201),
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='low_rating',
            place_id=2,
            brand=storage.Brand(brand_id=2),
            new_rating=storage.NewRating(show=True, rating=4.6, count=201),
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='good_rating',
            place_id=3,
            brand=storage.Brand(brand_id=3),
            new_rating=storage.NewRating(show=True, rating=4.8, count=201),
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='great_rating',
            place_id=4,
            brand=storage.Brand(brand_id=4),
            new_rating=storage.NewRating(show=True, rating=4.92, count=201),
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='no_rating',
            place_id=5,
            brand=storage.Brand(brand_id=5),
            new_rating=storage.NewRating(show=False, count=201),
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('any', data)
    assert (
        {
            'id': matching.UuidString(),
            'type': 'rating',
            'payload': {
                'additional_text': {
                    'color': [
                        {'theme': 'light', 'value': '#ZERO00'},
                        {'theme': 'dark', 'value': '#ZERO00'},
                    ],
                    'text': '(200+)',
                },
                'description': {
                    'color': [
                        {'theme': 'light', 'value': '#ZERO00'},
                        {'theme': 'dark', 'value': '#ZERO00'},
                    ],
                    'text': '0.0',
                },
                'icon': {
                    'color': [
                        {'theme': 'light', 'value': '#ZERO00'},
                        {'theme': 'dark', 'value': '#ZERO00'},
                    ],
                    'uri': 'asset://rating_star',
                },
                'icon_url': 'asset://rating_star',
                'title': '0.0',
                'color': [
                    {'theme': 'light', 'value': '#ZERO00'},
                    {'theme': 'dark', 'value': '#ZERO00'},
                ],
            },
        }
        == layout_utils.find_first_meta(
            'rating', layout_utils.find_place_by_slug('zero_rating', block),
        )
    )

    assert (
        {
            'id': matching.UuidString(),
            'type': 'rating',
            'payload': {
                'additional_text': {
                    'color': [
                        {'theme': 'light', 'value': '#LOW000'},
                        {'theme': 'dark', 'value': '#LOW000'},
                    ],
                    'text': '(200+)',
                },
                'description': {
                    'color': [
                        {'theme': 'light', 'value': '#LOW000'},
                        {'theme': 'dark', 'value': '#LOW000'},
                    ],
                    'text': '4.6',
                },
                'icon': {
                    'color': [
                        {'theme': 'light', 'value': '#LOW000'},
                        {'theme': 'dark', 'value': '#LOW000'},
                    ],
                    'uri': 'asset://rating_star',
                },
                'icon_url': 'asset://rating_star',
                'title': '4.6',
                'color': [
                    {'theme': 'light', 'value': '#LOW000'},
                    {'theme': 'dark', 'value': '#LOW000'},
                ],
            },
        }
        == layout_utils.find_first_meta(
            'rating', layout_utils.find_place_by_slug('low_rating', block),
        )
    )

    assert (
        {
            'id': matching.UuidString(),
            'type': 'rating',
            'payload': {
                'additional_text': {
                    'color': [
                        {'theme': 'light', 'value': '#GOOD00'},
                        {'theme': 'dark', 'value': '#GOOD00'},
                    ],
                    'text': '(200+)',
                },
                'description': {
                    'color': [
                        {'theme': 'light', 'value': '#GOOD00'},
                        {'theme': 'dark', 'value': '#GOOD00'},
                    ],
                    'text': '4.8 Хорошо',
                },
                'icon': {
                    'color': [
                        {'theme': 'light', 'value': '#GOOD00'},
                        {'theme': 'dark', 'value': '#GOOD00'},
                    ],
                    'uri': 'asset://rating_star',
                },
                'title': '4.8 Хорошо',
                'icon_url': 'asset://rating_star',
                'color': [
                    {'theme': 'light', 'value': '#GOOD00'},
                    {'theme': 'dark', 'value': '#GOOD00'},
                ],
            },
        }
        == layout_utils.find_first_meta(
            'rating', layout_utils.find_place_by_slug('good_rating', block),
        )
    )

    assert (
        {
            'id': matching.UuidString(),
            'type': 'rating',
            'payload': {
                'additional_text': {
                    'color': [
                        {'theme': 'light', 'value': '#GREAT0'},
                        {'theme': 'dark', 'value': '#GREAT0'},
                    ],
                    'text': '(200+)',
                },
                'description': {
                    'color': [
                        {'theme': 'light', 'value': '#GREAT0'},
                        {'theme': 'dark', 'value': '#GREAT0'},
                    ],
                    'text': '4.9 Отлично',
                },
                'icon': {
                    'color': [
                        {'theme': 'light', 'value': '#GREAT0'},
                        {'theme': 'dark', 'value': '#GREAT0'},
                    ],
                    'uri': 'asset://rating_star',
                },
                'icon_url': 'asset://rating_star',
                'title': '4.9 Отлично',
                'color': [
                    {'theme': 'light', 'value': '#GREAT0'},
                    {'theme': 'dark', 'value': '#GREAT0'},
                ],
            },
        }
        == layout_utils.find_first_meta(
            'rating', layout_utils.find_place_by_slug('great_rating', block),
        )
    )

    assert (
        {
            'id': matching.UuidString(),
            'type': 'rating',
            'payload': {
                'description': {
                    'color': [
                        {'theme': 'light', 'value': '#NO0000'},
                        {'theme': 'dark', 'value': '#NO0000'},
                    ],
                    'text': 'Мало оценок',
                },
                'icon': {
                    'color': [
                        {'theme': 'light', 'value': '#NO0000'},
                        {'theme': 'dark', 'value': '#NO0000'},
                    ],
                    'uri': 'asset://no_rating_star',
                },
                'icon_url': 'asset://no_rating_star',
                'title': 'Мало оценок',
                'color': [
                    {'theme': 'light', 'value': '#NO0000'},
                    {'theme': 'dark', 'value': '#NO0000'},
                ],
            },
        }
        == layout_utils.find_first_meta(
            'rating', layout_utils.find_place_by_slug('no_rating', block),
        )
    )


@pytest.mark.now('2021-04-03T23:17:00+00:00')
@pytest.mark.config(EATS_CATALOG_RATING_META=RATING_META_CONFIG)
@pytest.mark.translations(**RATING_META_TRANSLATIONS)
async def test_rating_meta_new(catalog_for_layout, eats_catalog_storage):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='new',
            place_id=5,
            brand=storage.Brand(brand_id=5),
            launched_at=parser.parse('2021-04-01T13:30:00+00:00'),
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('any', data)

    assert (
        {
            'id': matching.UuidString(),
            'type': 'rating',
            'payload': {
                'description': {
                    'color': [
                        {'theme': 'light', 'value': '#NEW000'},
                        {'theme': 'dark', 'value': '#NEW000'},
                    ],
                    'text': 'Новый',
                },
                'icon': {'color': [], 'uri': 'asset://rating_star_new'},
                'icon_url': 'asset://rating_star_new',
                'title': 'Новый',
                'color': [
                    {'theme': 'light', 'value': '#NEW000'},
                    {'theme': 'dark', 'value': '#NEW000'},
                ],
            },
        }
        == layout_utils.find_first_meta(
            'rating', layout_utils.find_place_by_slug('new', block),
        )
    )


@pytest.mark.now('2021-04-03T23:17:00+00:00')
@pytest.mark.config(EATS_CATALOG_RATING_META=RATING_META_CONFIG)
@pytest.mark.translations(**RATING_META_TRANSLATIONS)
@experiments.TOP_RATING_TAG
@pytest.mark.parametrize(
    'expected_meta',
    [
        pytest.param(
            {
                'top_no_rating': {
                    'id': matching.UuidString(),
                    'type': 'rating',
                    'payload': {
                        'description': {
                            'color': [
                                {'theme': 'light', 'value': '#TOP000'},
                                {'theme': 'dark', 'value': '#TOP000'},
                            ],
                            'text': 'Входит в Топ',
                        },
                        'icon': {'color': [], 'uri': 'asset://flame'},
                        'icon_url': 'asset://flame',
                        'title': 'Входит в Топ',
                        'color': [
                            {'theme': 'light', 'value': '#TOP000'},
                            {'theme': 'dark', 'value': '#TOP000'},
                        ],
                    },
                },
                'top_with_rating': {
                    'id': matching.UuidString(),
                    'type': 'rating',
                    'payload': {
                        'description': {
                            'color': [
                                {'theme': 'light', 'value': '#TOP000'},
                                {'theme': 'dark', 'value': '#TOP000'},
                            ],
                            'text': '4.9 Входит в Топ',
                        },
                        'icon': {'color': [], 'uri': 'asset://flame'},
                        'icon_url': 'asset://flame',
                        'title': '4.9 Входит в Топ',
                        'color': [
                            {'theme': 'light', 'value': '#TOP000'},
                            {'theme': 'dark', 'value': '#TOP000'},
                        ],
                    },
                },
            },
            id='top enabled',
        ),
        pytest.param(
            {
                'top_no_rating': {
                    'id': matching.UuidString(),
                    'type': 'rating',
                    'payload': {
                        'description': {
                            'color': [
                                {'theme': 'light', 'value': '#NO0000'},
                                {'theme': 'dark', 'value': '#NO0000'},
                            ],
                            'text': 'Мало оценок',
                        },
                        'icon': {
                            'color': [
                                {'theme': 'light', 'value': '#NO0000'},
                                {'theme': 'dark', 'value': '#NO0000'},
                            ],
                            'uri': 'asset://no_rating_star',
                        },
                        'icon_url': 'asset://no_rating_star',
                        'title': 'Мало оценок',
                        'color': [
                            {'theme': 'light', 'value': '#NO0000'},
                            {'theme': 'dark', 'value': '#NO0000'},
                        ],
                    },
                },
                'top_with_rating': {
                    'id': matching.UuidString(),
                    'type': 'rating',
                    'payload': {
                        'description': {
                            'color': [
                                {'theme': 'light', 'value': '#NEW000'},
                                {'theme': 'dark', 'value': '#NEW000'},
                            ],
                            'text': 'Новый',
                        },
                        'icon': {
                            'color': [],
                            'uri': 'asset://rating_star_new',
                        },
                        'icon_url': 'asset://rating_star_new',
                        'title': 'Новый',
                        'color': [
                            {'theme': 'light', 'value': '#NEW000'},
                            {'theme': 'dark', 'value': '#NEW000'},
                        ],
                    },
                },
            },
            marks=experiments.DISABLE_TOP,
            id='top disabled',
        ),
    ],
)
async def test_rating_meta_top(
        catalog_for_layout, eats_catalog_storage, expected_meta,
):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='top_no_rating',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            new_rating=storage.NewRating(show=False, rating=0),
            tags=['top_rating'],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='top_with_rating',
            place_id=5,
            brand=storage.Brand(brand_id=5),
            launched_at=parser.parse('2021-04-01T13:30:00+00:00'),  # new
            new_rating=storage.NewRating(show=True, rating=4.92),
            tags=['top_rating'],
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('any', data)

    for place_slug, expected in expected_meta.items():
        place = layout_utils.find_place_by_slug(place_slug, block)
        assert (
            layout_utils.find_first_meta('rating', place) == expected
        ), place_slug


@pytest.mark.now('2021-04-03T23:17:00+00:00')
@pytest.mark.config(EATS_CATALOG_RATING_META=RATING_META_CONFIG)
@pytest.mark.translations(**RATING_META_TRANSLATIONS)
@experiments.TOP_RATING_TAG
async def test_rating_round_equal_slug(
        slug, catalog_for_layout, eats_catalog_storage,
):
    """
    EDACAT-814: проверяет, что округление рейтинга на CFL рабоатет так же
    как на слаге
    """

    expected_rating = 4.9

    eats_catalog_storage.add_place(
        storage.Place(
            slug='great_rating',
            place_id=4,
            brand=storage.Brand(brand_id=4),
            new_rating=storage.NewRating(show=True, rating=4.89),
        ),
    )

    response = await slug(
        'great_rating',
        query={'longitude': 37.591503, 'latitude': 55.802998},
        headers={'X-Eats-Session': 'blablabla'},
    )

    assert response.status_code == 200

    data = response.json()

    slug_rating = data['payload']['foundPlace']['place']['rating']
    assert slug_rating == expected_rating

    response = await catalog_for_layout(
        location={'longitude': 37.591503, 'latitude': 55.802998},
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('any', data)

    rating_meta = layout_utils.find_first_meta(
        'rating', layout_utils.find_place_by_slug('great_rating', block),
    )

    expected_text = '{} Отлично'.format(slug_rating)
    assert rating_meta['payload']['description']['text'] == expected_text


@pytest.mark.now('2021-04-03T19:13:00+00:00')
@pytest.mark.config(EATS_CATALOG_RATING_META=RATING_META_CONFIG)
@pytest.mark.translations(**RATING_META_TRANSLATIONS)
@pytest.mark.parametrize(
    'payload',
    [
        pytest.param(
            {
                'additional_text': {
                    'color': [
                        {'theme': 'light', 'value': '#GREAT0'},
                        {'theme': 'dark', 'value': '#GREAT0'},
                    ],
                    'text': '(200+)',
                },
                'description': {
                    'color': [
                        {'theme': 'light', 'value': '#GREAT0'},
                        {'theme': 'dark', 'value': '#GREAT0'},
                    ],
                    'text': '4.9 Отлично',
                },
                'icon': {
                    'color': [
                        {'theme': 'light', 'value': '#GREAT0'},
                        {'theme': 'dark', 'value': '#GREAT0'},
                    ],
                    'uri': 'asset://rating_star',
                },
                'icon_url': 'asset://rating_star',
                'title': '4.9 Отлично',
                'color': [
                    {'theme': 'light', 'value': '#GREAT0'},
                    {'theme': 'dark', 'value': '#GREAT0'},
                ],
            },
            id='from config',
        ),
        pytest.param(
            {
                'additional_text': {
                    'color': [
                        {'theme': 'light', 'value': '#EXP000'},
                        {'theme': 'dark', 'value': '#EXP000'},
                    ],
                    'text': '(200+)',
                },
                'description': {
                    'color': [
                        {'theme': 'light', 'value': '#EXP000'},
                        {'theme': 'dark', 'value': '#EXP000'},
                    ],
                    'text': '4.9 Так себе',
                },
                'icon': {
                    'color': [
                        {'theme': 'light', 'value': '#EXP000'},
                        {'theme': 'dark', 'value': '#EXP000'},
                    ],
                    'uri': 'asset://rating_star',
                },
                'icon_url': 'asset://rating_star',
                'title': '4.9 Так себе',
                'color': [
                    {'theme': 'light', 'value': '#EXP000'},
                    {'theme': 'dark', 'value': '#EXP000'},
                ],
            },
            marks=(
                experiments.new_rating(
                    thresholds=[
                        {
                            'min_rating': 4.9,
                            'additional_description': 'Так себе',
                            'icon_color': [
                                {'theme': 'light', 'value': '#EXP000'},
                                {'theme': 'dark', 'value': '#EXP000'},
                            ],
                            'text_color': [
                                {'theme': 'light', 'value': '#EXP000'},
                                {'theme': 'dark', 'value': '#EXP000'},
                            ],
                        },
                    ],
                )
            ),
            id='from experiment',
        ),
    ],
)
async def test_new_rating(catalog_for_layout, eats_catalog_storage, payload):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='great_rating',
            place_id=4,
            brand=storage.Brand(brand_id=4),
            new_rating=storage.NewRating(rating=4.9232, show=True, count=201),
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='great_rating_shop',
            place_id=5,
            brand=storage.Brand(brand_id=5),
            new_rating=storage.NewRating(rating=2.92, show=True, count=201),
            business=storage.Business.Shop,
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('any', data)

    restaurant = layout_utils.find_place_by_slug('great_rating', block)

    assert {
        'id': matching.UuidString(),
        'type': 'rating',
        'payload': payload,
    } == layout_utils.find_first_meta('rating', restaurant)

    shop = layout_utils.find_place_by_slug('great_rating_shop', block)

    assert {
        'id': matching.UuidString(),
        'type': 'rating',
        'payload': {
            'additional_text': {
                'color': [
                    {'theme': 'light', 'value': '#ZERO00'},
                    {'theme': 'dark', 'value': '#ZERO00'},
                ],
                'text': '(200+)',
            },
            'description': {
                'color': [
                    {'theme': 'light', 'value': '#ZERO00'},
                    {'theme': 'dark', 'value': '#ZERO00'},
                ],
                'text': '2.9',
            },
            'icon': {
                'color': [
                    {'theme': 'light', 'value': '#ZERO00'},
                    {'theme': 'dark', 'value': '#ZERO00'},
                ],
                'uri': 'asset://rating_star',
            },
            'icon_url': 'asset://rating_star',
            'title': '2.9',
            'color': [
                {'theme': 'light', 'value': '#ZERO00'},
                {'theme': 'dark', 'value': '#ZERO00'},
            ],
        },
    } == layout_utils.find_first_meta('rating', shop)


@pytest.mark.now('2021-04-03T19:13:00+00:00')
@pytest.mark.config(EATS_CATALOG_RATING_META=RATING_META_CONFIG)
@pytest.mark.translations(**RATING_META_TRANSLATIONS)
@experiments.HIDE_RATING_COUNT
@pytest.mark.parametrize(
    'payload',
    [
        pytest.param(
            {
                'description': {
                    'color': [
                        {'theme': 'light', 'value': '#GREAT0'},
                        {'theme': 'dark', 'value': '#GREAT0'},
                    ],
                    'text': '4.9 Отлично',
                },
                'icon': {
                    'color': [
                        {'theme': 'light', 'value': '#GREAT0'},
                        {'theme': 'dark', 'value': '#GREAT0'},
                    ],
                    'uri': 'asset://rating_star',
                },
                'icon_url': 'asset://rating_star',
                'title': '4.9 Отлично',
                'color': [
                    {'theme': 'light', 'value': '#GREAT0'},
                    {'theme': 'dark', 'value': '#GREAT0'},
                ],
            },
            id='old rating',
        ),
        pytest.param(
            {
                'description': {
                    'color': [
                        {'theme': 'light', 'value': '#EXP000'},
                        {'theme': 'dark', 'value': '#EXP000'},
                    ],
                    'text': '4.9 Так себе',
                },
                'icon': {
                    'color': [
                        {'theme': 'light', 'value': '#EXP000'},
                        {'theme': 'dark', 'value': '#EXP000'},
                    ],
                    'uri': 'asset://rating_star',
                },
                'icon_url': 'asset://rating_star',
                'title': '4.9 Так себе',
                'color': [
                    {'theme': 'light', 'value': '#EXP000'},
                    {'theme': 'dark', 'value': '#EXP000'},
                ],
            },
            marks=(
                experiments.new_rating(
                    thresholds=[
                        {
                            'min_rating': 4.9,
                            'additional_description': 'Так себе',
                            'icon_color': [
                                {'theme': 'light', 'value': '#EXP000'},
                                {'theme': 'dark', 'value': '#EXP000'},
                            ],
                            'text_color': [
                                {'theme': 'light', 'value': '#EXP000'},
                                {'theme': 'dark', 'value': '#EXP000'},
                            ],
                        },
                    ],
                )
            ),
            id='new rating',
        ),
    ],
)
async def test_hide_rating_count(
        catalog_for_layout, eats_catalog_storage, payload,
):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='great_rating',
            place_id=4,
            brand=storage.Brand(brand_id=4),
            new_rating=storage.NewRating(rating=4.9232, show=True),
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('any', data)

    restaurant = layout_utils.find_place_by_slug('great_rating', block)

    assert {
        'id': matching.UuidString(),
        'type': 'rating',
        'payload': payload,
    } == layout_utils.find_first_meta('rating', restaurant)


@pytest.mark.parametrize(
    'currency_sign',
    [
        pytest.param(
            'sign', marks=(experiments.currency_sign('sign')), id='override',
        ),
        pytest.param('₽', id='default'),
    ],
)
async def test_price_category(
        catalog_for_layout, eats_catalog_storage, currency_sign,
):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='place', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )

    eats_catalog_storage.add_zone(storage.Zone(place_id=1, zone_id=1))

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())
    place = layout_utils.find_place_by_slug('place', block)

    assert {
        'id': matching.UuidString(),
        'type': 'price_category',
        'payload': {
            'currency_sign': currency_sign,
            'highlighted_symbols': 3,
            'icon_url': 'asset://price_category',
            'total_symbols': 3,
        },
    } == layout_utils.find_first_meta('price_category', place)


@experiments.SHOW_PLACE_CATEGORIES
@translations.eats_catalog_ru(
    {'c4l.place_category.1': 'Завтраки', 'c4l.place_category.2': 'Обеды'},
)
async def test_place_category(catalog_for_layout, eats_catalog_storage):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='place',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            categories=[
                storage.Category(1, 'Завтраки'),
                storage.Category(2, 'Обеды'),
                storage.Category(3, 'Ужины'),
            ],
        ),
    )
    eats_catalog_storage.add_zone(storage.Zone(place_id=1, zone_id=1))

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())
    place = layout_utils.find_place_by_slug('place', block)

    assert {
        'id': matching.UuidString(),
        'type': 'info',
        'payload': {'icon_url': '', 'title': 'Завтраки, Обеды'},
    } == layout_utils.find_first_meta('info', place)
