# pylint: disable=C0302
import asyncio
import dataclasses
import json
from typing import List
from typing import Optional

from dateutil import parser
# pylint: disable=import-error
from eats_analytics import eats_analytics
import eats_restapp_marketing_cache.models as ermc_models
# pylint: enable=import-error
import pytest

from eats_catalog import adverts
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import translations
from . import layout_utils

META_TEXT: str = 'testsuite_ads'
META_TEXT_COLOR: list = [
    {'theme': 'light', 'value': '010101'},
    {'theme': 'dark', 'value': '101010'},
]
META_BACKGROUND_COLOR: list = [
    {'theme': 'light', 'value': 'FFFFFF'},
    {'theme': 'dark', 'value': 'WWWWWW'},
]


@dataclasses.dataclass
class ResponsePlace:
    place_id: int
    has_ads: bool = False


def build_direct_premium_banner(banner_id: int):
    return {
        'bid': str(banner_id),
        'url': 'http://eda.yandex.ru/click/{}'.format(banner_id),
        'link_tail': '/view/{}'.format(banner_id),
    }


@pytest.mark.now('2022-03-21T14:20:00+03:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_advert_rest_metric(
        taxi_eats_catalog,
        catalog_for_layout,
        eats_catalog_storage,
        yabs,
        statistics,
):
    # EDACAT-2883: метрика записывающая количетво рекламных ресторанов
    # в выдаче по региону
    # стоит в начале тестов потому что иначе записывает все метрики сессии
    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2022-03-21T09:00:00+03:00'),
            end=parser.parse('2022-03-21T23:00:00+03:00'),
        ),
    ]

    for place_id in [1, 2, 3, 4, 5]:
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                region=storage.Region(region_id=42),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=working_intervals,
            ),
        )

    banners = [1, 2, 3]
    for banner_id in banners:
        yabs.add_banner(adverts.create_yabs_service_banner(banner_id))

    block_id = 'adverts'

    async with statistics.capture(taxi_eats_catalog) as capture:
        response = await catalog_for_layout(
            blocks=[
                {
                    'id': block_id,
                    'type': 'open',
                    'disable_filters': False,
                    'advert_settings': {
                        'ads_only': False,
                        'indexes': [0, 1, 2, 3, 4],
                    },
                },
            ],
        )

    response_json = response.json()

    assert response.status_code == 200
    assert yabs.times_called == 1
    assert len(response_json['blocks']) == 1
    assert len(response_json['blocks'][0]['list']) == 5

    # проверить результаты метрики не получится потому что
    # она записывает для всей сессии значения и тест
    # будет флапать если увеличить количество запросов

    zero_metric = 'zero.advert-places.open.213'
    non_zero_metric = 'non-zero.advert-places.open.213'

    assert zero_metric in capture.statistics, capture.statistics.keys()
    assert capture.statistics[zero_metric] == 3
    assert non_zero_metric in capture.statistics, capture.statistics.keys()
    assert capture.statistics[non_zero_metric] == 3


@pytest.mark.now('2021-03-18T11:00:00+00:00')
@pytest.mark.parametrize(
    'has_block',
    [
        pytest.param(False, id='no experiment'),
        pytest.param(
            False,
            marks=(
                pytest.mark.experiments3(
                    name='eats_catalog_advertisements',
                    is_config=True,
                    consumers=['eats-catalog-advertiser'],
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    clauses=[
                        {
                            'title': 'Always true',
                            'predicate': {'type': 'true'},
                            'value': {
                                'source': 'experiment',
                                'place_ids': [],
                                'brand_ids': [],
                            },
                        },
                    ],
                )
            ),
            id='empty targets',
        ),
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    name='eats_catalog_advertisements',
                    is_config=True,
                    consumers=['eats-catalog-advertiser'],
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    clauses=[
                        {
                            'title': 'Always true',
                            'predicate': {'type': 'true'},
                            'value': {
                                'source': 'experiment',
                                'place_ids': [1, 2],
                            },
                        },
                    ],
                )
            ),
            id='match places',
        ),
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    name='eats_catalog_advertisements',
                    is_config=True,
                    consumers=['eats-catalog-advertiser'],
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    clauses=[
                        {
                            'title': 'Always true',
                            'predicate': {'type': 'true'},
                            'value': {
                                'source': 'experiment',
                                'brand_ids': [2],
                            },
                        },
                    ],
                )
            ),
            id='match brands',
        ),
    ],
)
async def test_experiment_adverts(
        catalog_for_layout, eats_catalog_storage, has_block,
):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='first', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-18T10:00:00+00:00'),
                    end=parser.parse('2021-03-18T22:00:00+00:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='second', place_id=2, brand=storage.Brand(brand_id=2),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-18T10:00:00+00:00'),
                    end=parser.parse('2021-03-18T22:00:00+00:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        blocks=[
            {'id': 'ads', 'type': 'advertisements', 'disable_filters': False},
        ],
    )
    assert response.status == 200

    data = response.json()
    if has_block:
        layout_utils.find_block('ads', data)
    else:
        layout_utils.assert_no_block_or_empty('ads', data)


@pytest.mark.now('2021-03-19T11:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.parametrize(
    'banners, yabs_banners, yabs_calls, expected_places',
    [
        pytest.param([], [], 0, [], id='empty campaigns cache'),
        pytest.param(
            [ermc_models.PlaceBanner(place_id=50, banner_id=1)],
            [],
            0,
            [],
            id='no matching banners',
        ),
        pytest.param(
            [ermc_models.PlaceBanner(place_id=1, banner_id=1)],
            [],
            1,
            [],
            id='no yabs banners',
        ),
        pytest.param(
            [
                ermc_models.PlaceBanner(place_id=1, banner_id=1),
                ermc_models.PlaceBanner(place_id=3, banner_id=3),
            ],
            [
                {
                    'banner_id': '3',
                    'direct_data': {
                        'url': 'http://yandex.ru/click/3',
                        'link_head': 'http://yandex.ru',
                        'link_tail': '/view/3',
                    },
                },
                {
                    'banner_id': '1',
                    'direct_data': {
                        'url': 'http://yandex.ru/click/1',
                        'link_head': 'http://yandex.ru',
                        'link_tail': '/view/1',
                    },
                },
            ],
            1,
            [
                {
                    'id': 3,
                    'view_url': 'http://yandex.ru/view/3',
                    'click_url': 'http://yandex.ru/click/3',
                },
                {
                    'id': 1,
                    'view_url': 'http://yandex.ru/view/1',
                    'click_url': 'http://yandex.ru/click/1',
                },
            ],
            id='match and order banners',
        ),
        pytest.param(
            [ermc_models.PlaceBanner(place_id=2, banner_id=2)],
            [
                {
                    'banner_id': '3',
                    'direct_data': {
                        'url': 'http://yandex.ru/click/3',
                        'link_head': 'http://yandex.ru',
                        'link_tail': '/view/3',
                    },
                },
                {
                    'banner_id': '2',
                    'direct_data': {
                        'url': 'http://yandex.ru/click/2',
                        'link_head': 'http://yandex.ru',
                        'link_tail': '/view/2',
                    },
                },
            ],
            1,
            [
                {
                    'id': 2,
                    'view_url': 'http://yandex.ru/view/2',
                    'click_url': 'http://yandex.ru/click/2',
                },
            ],
            id='has more banners in response than expected',
        ),
    ],
)
async def test_layout_advertisements_yabs_service_banner(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        eats_restapp_marketing_cache_mock,
        banners: List[ermc_models.PlaceBanner],
        yabs_banners,
        yabs_calls,
        expected_places,
):
    for i in range(1, 4):
        eats_catalog_storage.add_place(
            storage.Place(place_id=i, brand=storage.Brand(brand_id=i)),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=i,
                place_id=i,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-03-19T10:00:00+00:00'),
                        end=parser.parse('2021-03-19T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    eats_restapp_marketing_cache_mock.add_banners(banners)

    @mockserver.json_handler('/yabs/page/1')
    def yabs_page(request):
        assert request.query
        return {'service_banner': yabs_banners}

    response = await catalog_for_layout(
        blocks=[
            {'id': 'ads', 'type': 'advertisements', 'disable_filters': False},
        ],
    )
    assert response.status == 200
    assert yabs_page.times_called == yabs_calls

    data = response.json()

    if not expected_places:
        assert not data['blocks']
        return

    ad_block = layout_utils.find_block('ads', data)
    assert len(ad_block) == len(expected_places)

    for expected, place in zip(expected_places, ad_block):
        assert expected['id'] == place['meta']['place_id']

        ads_feature = place['payload']['data']['features']['advertisement']
        assert ads_feature['view_url'] == expected['view_url']
        assert ads_feature['click_url'] == expected['click_url']


@pytest.mark.now('2021-03-23T11:00:00+00:00')
@experiments.advertisements(source='yabs')
@pytest.mark.parametrize(
    'page_ref',
    [
        pytest.param(
            None,
            marks=(
                experiments.yabs_settings(
                    adverts.YabsSettings(page_id=1, target_ref='testsuite'),
                )
            ),
            id='no page ref',
        ),
        pytest.param(
            'testsuite',
            marks=(
                experiments.yabs_settings(
                    adverts.YabsSettings(
                        page_id=1,
                        target_ref='testsuite',
                        page_ref='testsuite',
                    ),
                )
            ),
            id='with page ref',
        ),
    ],
)
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
        ermc_models.PlaceBanner(place_id=4, banner_id=4),
    ],
)
async def test_yabs_page_ref(
        catalog_for_layout,
        eats_catalog_storage,
        yabs,
        page_ref: Optional[str],
):
    """EDACAT-726: тест проверят, что параметр page-ref проставляется"""

    @yabs.request_assertion
    def _assert_page_ref(request):
        if not page_ref:
            assert 'page-ref' not in request.query
        else:
            assert page_ref == request.query['page-ref']

    for i in range(1, 4):
        eats_catalog_storage.add_place(
            storage.Place(place_id=i, brand=storage.Brand(brand_id=i)),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=i,
                place_id=i,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-03-23T10:00:00+00:00'),
                        end=parser.parse('2021-03-23T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    response = await catalog_for_layout(
        blocks=[
            {'id': 'ads', 'type': 'advertisements', 'disable_filters': False},
        ],
    )
    assert response.status == 200
    assert yabs.times_called == 1


@pytest.mark.now('2021-03-18T11:00:00+00:00')
@experiments.advertisements(source='experiment', brand_ids=[2])
async def test_ads_multiple_blocks(catalog_for_layout, eats_catalog_storage):
    """
    Проверяет что два блока рекламы в одной выдаче будут работать, хотя
    кажется это не имеет особого смысла.
    """

    eats_catalog_storage.add_place(
        storage.Place(
            slug='second', place_id=2, brand=storage.Brand(brand_id=2),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-18T10:00:00+00:00'),
                    end=parser.parse('2021-03-18T22:00:00+00:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'ads_1',
                'type': 'advertisements',
                'disable_filters': False,
            },
            {
                'id': 'ads_2',
                'type': 'advertisements',
                'disable_filters': False,
            },
        ],
    )
    assert response.status == 200

    data = response.json()
    layout_utils.find_block('ads_1', data)
    layout_utils.find_block('ads_2', data)


@pytest.mark.now('2021-04-21T17:00:00+00:00')
@experiments.advertisements(source='experiment', place_ids=[1])
@translations.eats_catalog_ru({'ads.meta': META_TEXT})
@experiments.eats_catalog_advertisement_meta(
    text_key='ads.meta',
    text_color=META_TEXT_COLOR,
    background=META_BACKGROUND_COLOR,
)
async def test_advertisement_meta(catalog_for_layout, eats_catalog_storage):
    """EDACAT-853: тест проверяет, что у рекламного ресторана есть рекламная
    мета."""
    for place_id in [1, 2]:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                slug='place_{}'.format(place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=place_id,
                zone_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-04-21T10:00:00+00:00'),
                        end=parser.parse('2021-04-21T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    response = await catalog_for_layout(
        blocks=[
            {'id': 'ads', 'type': 'advertisements', 'disable_filters': False},
            {'id': 'open', 'type': 'open', 'disable_filters': False},
        ],
    )
    assert response.status == 200

    open_block = layout_utils.find_block('open', response.json())
    assert len(open_block) == 2
    for place in open_block:
        layout_utils.assert_no_meta(place, 'advertisements')

    ads_block = layout_utils.find_block('ads', response.json())
    assert len(ads_block) == 1
    for place in ads_block:
        meta = layout_utils.find_first_meta('advertisements', place)
        assert meta['payload'] == {
            'text': {'text': META_TEXT, 'color': META_TEXT_COLOR},
            'background': META_BACKGROUND_COLOR,
        }


@pytest.mark.now('2021-04-13T12:00:00+00:00')
@experiments.advertisements(source='yabs')
@pytest.mark.parametrize(
    'expected_additional_banners',
    [
        pytest.param(
            [
                {'banner_id': 1, 'ignore_context': True},
                {'banner_id': 2, 'ignore_context': True},
                {'banner_id': 3, 'ignore_context': True},
            ],
            marks=(experiments.yabs_settings()),
            id='no value coeffs',
        ),
        pytest.param(
            [
                {
                    'banner_id': 1,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': 0.0, 'C': 0},
                },
                {
                    'banner_id': 2,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': 0.0, 'C': 0},
                },
                {
                    'banner_id': 3,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': 0.0, 'C': 0},
                },
            ],
            marks=(
                experiments.yabs_settings(
                    adverts.YabsSettings(
                        page_id=1,
                        target_ref='testsuite',
                        coefficients=adverts.Coefficients(
                            yabs_ctr=1,
                            send_relevance=True,
                            relevance_multiplier=1,
                        ),
                    ),
                ),
                experiments.eats_catalog_yabs_coefficients(
                    coefficients=adverts.Coefficients(
                        yabs_ctr=1,
                        send_relevance=True,
                        relevance_multiplier=1,
                    ),
                ),
            ),
            id='with value coeffs',
        ),
        pytest.param(
            [
                {
                    'banner_id': 1,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': 0.0, 'C': 0},
                },
                {
                    'banner_id': 2,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': 0.0, 'C': 0},
                },
                {
                    'banner_id': 3,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': 0.0, 'C': 0},
                },
            ],
            marks=(
                experiments.yabs_settings(
                    adverts.YabsSettings(
                        page_id=1,
                        target_ref='testsuite',
                        coefficients=adverts.Coefficients(
                            yabs_ctr=1,
                            send_relevance=True,
                            relevance_multiplier=10,
                        ),
                    ),
                ),
                experiments.eats_catalog_yabs_coefficients(
                    coefficients=adverts.Coefficients(
                        yabs_ctr=1,
                        send_relevance=True,
                        relevance_multiplier=10,
                    ),
                ),
            ),
            id='with value coeffs no eats relevance and relevance multiplier',
        ),
    ],
)
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_ads_yabs_value_coefficients(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        expected_additional_banners,
):
    """EDACAT-822: тест проверяет, что в yabs передаются коэффициенты
    релевантности, посчитанные ML."""

    for place_id in [1, 2, 3]:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-04-13T9:00:00+00:00'),
                        end=parser.parse('2021-04-13T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/yabs/page/1')
    def yabs_page(request):
        assert 'additional-banners' in request.query
        sorted_banners = sorted(
            json.loads(request.query['additional-banners']),
            key=lambda banner: banner['banner_id'],
        )
        assert sorted_banners == expected_additional_banners

        return {'service_banner': []}

    response = await catalog_for_layout(
        blocks=[
            {'id': 'ads', 'type': 'advertisements', 'disable_filters': False},
        ],
    )
    assert response.status == 200
    assert yabs_page.times_called == 1


@pytest.mark.now('2021-04-19T14:00:00+00:00')
@experiments.advertisements(source='experiment', place_ids=[1, 2, 3])
@pytest.mark.parametrize(
    'filters, filters_v2, place_slugs',
    [
        pytest.param(None, None, ['place_1', 'place_2'], id='delivery places'),
        pytest.param(
            [{'type': 'pickup', 'slug': 'pickup'}],
            None,
            ['place_1', 'place_3'],
            id='pickup filters v1 places',
        ),
        pytest.param(
            None,
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [{'type': 'pickup', 'slug': 'pickup'}],
                    },
                ],
            },
            ['place_1', 'place_3'],
            id='pickup filters v2 places',
        ),
    ],
)
async def test_shipping_type_advertisements(
        catalog_for_layout,
        eats_catalog_storage,
        filters,
        filters_v2,
        place_slugs,
):
    """
    EDACAT-881: тест проверяет, что в рекламный блок попадают только доступные
    для выбранного пользователем способа получения заказа (доставка/самовывоз).
    """
    schedule: list = [
        storage.WorkingInterval(
            start=parser.parse('2021-04-19T9:00:00+00:00'),
            end=parser.parse('2021-04-19T22:00:00+00:00'),
        ),
    ]

    # Добавляем 3 ресторана:
    # 1 доступен и для доставки и для самовывоза
    # 2 - только доставка
    # 3 - только самовывоз

    for place_id in [1, 2, 3]:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                slug='place_{}'.format(place_id),
                brand=storage.Brand(brand_id=place_id),
            ),
        )

    shipping_types = [
        storage.ShippingType.Delivery,
        storage.ShippingType.Pickup,
    ]
    for zone_id, shipping_type in zip([1, 2], shipping_types):
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=1,
                zone_id=zone_id,
                shipping_type=shipping_type,
                working_intervals=schedule,
            ),
        )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=2,
            zone_id=3,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=3,
            zone_id=4,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=schedule,
        ),
    )

    body: dict = {
        'location': {'longitude': 37.591503, 'latitude': 55.802998},
        'blocks': [
            {'id': 'ads', 'type': 'advertisements', 'disable_filters': False},
        ],
    }
    if filters:
        body['filters'] = filters
    if filters_v2:
        body['filters_v2'] = filters_v2

    response = await catalog_for_layout(**body)
    assert response.status == 200

    block = layout_utils.find_block('ads', response.json())
    assert len(block) == 2
    for slug in place_slugs:
        layout_utils.find_place_by_slug(slug, block)


@pytest.mark.now('2021-04-19T14:00:00+00:00')
@experiments.advertisements(source='experiment', place_ids=[1, 2, 3])
async def test_ads_block_predicate(catalog_for_layout, eats_catalog_storage):
    schedule = storage.WorkingInterval(
        start=parser.parse('2021-04-19T9:00:00+00:00'),
        end=parser.parse('2021-04-19T22:00:00+00:00'),
    )
    for place_id in [1, 3]:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                slug='place_{}'.format(place_id),
                brand=storage.Brand(brand_id=place_id),
            ),
        )

        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=place_id,
                zone_id=place_id,
                shipping_type=storage.ShippingType.Delivery,
                working_intervals=[schedule],
            ),
        )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            slug='place_2',
            brand=storage.Brand(brand_id=2),
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=2,
            zone_id=2,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[schedule],
        ),
    )

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'ads',
                'type': 'advertisements',
                'disable_filters': False,
                'condition': {
                    'type': 'neq',
                    'init': {
                        'arg_name': 'business',
                        'arg_type': 'string',
                        'value': 'shop',
                    },
                },
            },
        ],
    )
    assert response.status == 200

    block = layout_utils.find_block('ads', response.json())
    assert len(block) == 2
    for slug in ['place_1', 'place_3']:
        layout_utils.find_place_by_slug(slug, block)


@pytest.mark.now('2021-04-19T14:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_ads_block_predicate_ignore_yabs(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    schedule = storage.WorkingInterval(
        start=parser.parse('2021-04-19T9:00:00+00:00'),
        end=parser.parse('2021-04-19T22:00:00+00:00'),
    )
    for place_id in [1, 3]:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                slug='place_{}'.format(place_id),
                brand=storage.Brand(brand_id=place_id),
            ),
        )

        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=place_id,
                zone_id=place_id,
                shipping_type=storage.ShippingType.Delivery,
                working_intervals=[schedule],
            ),
        )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            slug='place_2',
            brand=storage.Brand(brand_id=2),
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=2,
            zone_id=2,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[schedule],
        ),
    )

    @mockserver.json_handler('/yabs/page/1')
    def yabs_page(request):
        assert 'additional-banners' in request.query
        ad_banners = json.loads(request.query['additional-banners'])
        for banner in ad_banners:
            if banner['banner_id'] == 2:
                assert False

        return {
            'service_banner': [
                {
                    'banner_id': '3',
                    'direct_data': {
                        'url': 'http://yandex.ru/click/3',
                        'link_head': 'http://yandex.ru',
                        'link_tail': '/view/3',
                    },
                },
                {
                    'banner_id': '1',
                    'direct_data': {
                        'url': 'http://yandex.ru/click/1',
                        'link_head': 'http://yandex.ru',
                        'link_tail': '/view/1',
                    },
                },
            ],
        }

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'ads',
                'type': 'advertisements',
                'disable_filters': False,
                'condition': {
                    'type': 'neq',
                    'init': {
                        'arg_name': 'business',
                        'arg_type': 'string',
                        'value': 'shop',
                    },
                },
            },
        ],
    )
    assert response.status == 200
    assert yabs_page.times_called == 1

    block = layout_utils.find_block('ads', response.json())
    assert len(block) == 2
    for slug in ['place_1', 'place_3']:
        layout_utils.find_place_by_slug(slug, block)


@pytest.mark.now('2021-04-19T14:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_service_handles_empty_yabs_response(
        catalog_for_layout, eats_catalog_storage, yabs,
):
    schedule = storage.WorkingInterval(
        start=parser.parse('2021-04-19T9:00:00+00:00'),
        end=parser.parse('2021-04-19T22:00:00+00:00'),
    )
    for place_id in [1, 2, 3]:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                slug='place_{}'.format(place_id),
                brand=storage.Brand(brand_id=place_id),
            ),
        )

        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=place_id,
                zone_id=place_id,
                shipping_type=storage.ShippingType.Delivery,
                working_intervals=[schedule],
            ),
        )

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'ads',
                'type': 'advertisements',
                'disable_filters': False,
                'condition': {
                    'type': 'neq',
                    'init': {
                        'arg_name': 'business',
                        'arg_type': 'string',
                        'value': 'shop',
                    },
                },
            },
        ],
    )
    assert response.status == 200
    assert yabs.times_called == 1

    layout_utils.assert_no_block_or_empty('ads', response.json())


@pytest.mark.now('2021-04-19T14:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_service_handles_yabs_no_content_response(
        catalog_for_layout, eats_catalog_storage, yabs,
):
    yabs.set_status_code(204)

    schedule = storage.WorkingInterval(
        start=parser.parse('2021-04-19T9:00:00+00:00'),
        end=parser.parse('2021-04-19T22:00:00+00:00'),
    )
    for place_id in [1, 2, 3]:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                slug='place_{}'.format(place_id),
                brand=storage.Brand(brand_id=place_id),
            ),
        )

        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=place_id,
                zone_id=place_id,
                shipping_type=storage.ShippingType.Delivery,
                working_intervals=[schedule],
            ),
        )

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'ads',
                'type': 'advertisements',
                'disable_filters': False,
                'condition': {
                    'type': 'neq',
                    'init': {
                        'arg_name': 'business',
                        'arg_type': 'string',
                        'value': 'shop',
                    },
                },
            },
        ],
    )
    assert response.status == 200
    assert yabs.times_called == 1

    layout_utils.assert_no_block_or_empty('ads', response.json())


@pytest.mark.now('2021-06-02T17:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.parametrize(
    'yabs_response, expected_places',
    [
        pytest.param(
            {
                'direct_premium': [
                    {
                        'bid': '3',
                        'url': 'http://yandex.ru/click/3',
                        'link_tail': '/view/3',
                    },
                    {
                        'bid': '1',
                        'url': 'http://yandex.ru/click/1',
                        'link_tail': '/view/1',
                    },
                ],
                'stat': [],
            },
            [],
            id='empty stat in response',
        ),
        pytest.param(
            {
                'direct_premium': [
                    {
                        'bid': '3',
                        'url': 'http://yandex.ru/click/3',
                        'link_tail': '/view/3',
                    },
                    {
                        'bid': '1',
                        'url': 'http://yandex.ru/click/1',
                        'link_tail': '/view/1',
                    },
                ],
                'stat': [{'link_head': 'http://yandex.ru'}],
            },
            [
                {
                    'id': 3,
                    'view_url': 'http://yandex.ru/view/3',
                    'click_url': 'http://yandex.ru/click/3',
                },
                {
                    'id': 1,
                    'view_url': 'http://yandex.ru/view/1',
                    'click_url': 'http://yandex.ru/click/1',
                },
            ],
            id='match and order banners',
        ),
        pytest.param(
            {
                'direct_premium': [
                    {
                        'bid': '4',
                        'url': 'http://yandex.ru/click/4',
                        'link_tail': '/view/4',
                    },
                    {
                        'bid': '2',
                        'url': 'http://yandex.ru/click/2',
                        'link_tail': '/view/2',
                    },
                ],
                'stat': [{'link_head': 'http://yandex.ru'}],
            },
            [
                {
                    'id': 2,
                    'view_url': 'http://yandex.ru/view/2',
                    'click_url': 'http://yandex.ru/click/2',
                },
            ],
            id='has more banners in response than expected',
        ),
        pytest.param(
            {
                'stat': [{'direct_premium': 0}],
                'direct_premium': [
                    {
                        'bid': '2',
                        'url': 'http://yandex.ru/click/2',
                        'link_tail': '/view/2',
                    },
                ],
            },
            None,
            id='no link_head',
        ),
    ],
)
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_layout_advertisements_yabs_direct_premium(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        yabs_response,
        expected_places,
):
    for i in range(1, 4):
        eats_catalog_storage.add_place(
            storage.Place(place_id=i, brand=storage.Brand(brand_id=i)),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=i,
                place_id=i,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-06-02T10:00:00+00:00'),
                        end=parser.parse('2021-06-02T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/yabs/page/1')
    def _yabs_page(_):
        return yabs_response

    response = await catalog_for_layout(
        blocks=[
            {'id': 'ads', 'type': 'advertisements', 'disable_filters': False},
        ],
    )
    assert response.status == 200

    data = response.json()

    if not expected_places:
        assert not data['blocks']
        return

    ad_block = layout_utils.find_block('ads', data)
    assert len(ad_block) == len(expected_places)

    for expected, place in zip(expected_places, ad_block):
        assert expected['id'] == place['meta']['place_id']

        ads_feature = place['payload']['data']['features']['advertisement']
        assert ads_feature['view_url'] == expected['view_url']
        assert ads_feature['click_url'] == expected['click_url']


@pytest.mark.now('2021-06-02T17:00:00+00:00')
@experiments.advertisements(source='yabs')
@pytest.mark.parametrize(
    'yabs_response, expected_urls',
    [
        pytest.param(
            {
                'service_banner': [
                    {
                        'banner_id': '1',
                        'direct_data': {
                            'url': 'http://yabs.yandex.ru/count/click/1',
                            'link_head': 'http://yabs.yandex.ru/count',
                            'link_tail': '/view/1',
                        },
                    },
                ],
            },
            {
                'view_url': 'http://yabs.yandex.ru/count/view/1',
                'click_url': 'http://yabs.yandex.ru/count/click/1',
            },
            marks=(experiments.yabs_settings()),
            id='service_banner insecure',
        ),
        pytest.param(
            {
                'service_banner': [
                    {
                        'banner_id': '1',
                        'direct_data': {
                            'url': 'http://yabs.yandex.ru/count/click/1',
                            'link_head': 'http://yabs.yandex.ru/count',
                            'link_tail': '/view/1',
                        },
                    },
                ],
            },
            {
                'view_url': 'https://yabs.yandex.ru/count/view/1',
                'click_url': 'https://yabs.yandex.ru/count/click/1',
            },
            marks=(
                experiments.yabs_settings(
                    adverts.YabsSettings(
                        page_id=1,
                        target_ref='testsuite',
                        secure_urls_schema=True,
                    ),
                )
            ),
            id='service_banner secure',
        ),
        pytest.param(
            {
                'direct_premium': [
                    {
                        'bid': '1',
                        'url': 'http://yabs.yandex.ru/count/click/1',
                        'link_tail': '/view/1',
                    },
                ],
                'stat': [{'link_head': 'http://yabs.yandex.ru/count'}],
            },
            {
                'view_url': 'http://yabs.yandex.ru/count/view/1',
                'click_url': 'http://yabs.yandex.ru/count/click/1',
            },
            marks=(experiments.yabs_settings()),
            id='direct_premium insecure',
        ),
        pytest.param(
            {
                'direct_premium': [
                    {
                        'bid': '1',
                        'url': 'http://yabs.yandex.ru/count/click/1',
                        'link_tail': '/view/1',
                    },
                ],
                'stat': [{'link_head': 'http://yabs.yandex.ru/count'}],
            },
            {
                'view_url': 'https://yabs.yandex.ru/count/view/1',
                'click_url': 'https://yabs.yandex.ru/count/click/1',
            },
            marks=(
                experiments.yabs_settings(
                    adverts.YabsSettings(
                        page_id=1,
                        target_ref='testsuite',
                        secure_urls_schema=True,
                    ),
                )
            ),
            id='direct_premium secure',
        ),
    ],
)
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[ermc_models.PlaceBanner(place_id=1, banner_id=1)],
)
async def test_layout_advertisements_yabs_secure_url_schema(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        yabs_response,
        expected_urls,
):
    place_id = 1
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=place_id, brand=storage.Brand(brand_id=place_id),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=place_id,
            place_id=place_id,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-02T10:00:00+00:00'),
                    end=parser.parse('2021-06-02T22:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler('/yabs/page/1')
    def _yabs_page(_):
        return yabs_response

    response = await catalog_for_layout(
        blocks=[
            {'id': 'ads', 'type': 'advertisements', 'disable_filters': False},
        ],
    )
    assert response.status == 200

    data = response.json()

    ad_block = layout_utils.find_block('ads', data)
    assert len(ad_block) == 1

    urls = ad_block[0]['payload']['data']['features']['advertisement']
    assert urls == expected_urls


@pytest.mark.now('2021-07-13T13:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@translations.eats_catalog_ru({'ads.meta': META_TEXT})
@experiments.eats_catalog_advertisement_meta(
    text_key='ads.meta',
    text_color=META_TEXT_COLOR,
    background=META_BACKGROUND_COLOR,
)
@pytest.mark.parametrize(
    'yabs_response, block, expected_places',
    [
        pytest.param(
            {
                'direct_premium': [
                    build_direct_premium_banner(1),
                    build_direct_premium_banner(2),
                    build_direct_premium_banner(3),
                ],
                'stat': [{'link_head': 'http://eda.yandex.ru'}],
            },
            {
                'id': 'block_1',
                'type': 'advertisements',
                'disable_filters': False,
            },
            [
                {
                    'place_id': 1,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/1',
                        'click_url': 'http://eda.yandex.ru/click/1',
                    },
                },
                {
                    'place_id': 2,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/2',
                        'click_url': 'http://eda.yandex.ru/click/2',
                    },
                },
                {
                    'place_id': 3,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/3',
                        'click_url': 'http://eda.yandex.ru/click/3',
                    },
                },
            ],
            id='advertisements block with no advert settings',
        ),
        pytest.param(
            {
                'direct_premium': [
                    build_direct_premium_banner(1),
                    build_direct_premium_banner(2),
                    build_direct_premium_banner(3),
                ],
                'stat': [{'link_head': 'http://eda.yandex.ru'}],
            },
            {
                'id': 'block_1',
                'type': 'advertisements',
                'disable_filters': False,
                'advert_settings': {'ads_only': True},
            },
            [
                {
                    'place_id': 1,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/1',
                        'click_url': 'http://eda.yandex.ru/click/1',
                    },
                },
                {
                    'place_id': 2,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/2',
                        'click_url': 'http://eda.yandex.ru/click/2',
                    },
                },
                {
                    'place_id': 3,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/3',
                        'click_url': 'http://eda.yandex.ru/click/3',
                    },
                },
            ],
            id='advertisements block with advert settings',
        ),
        pytest.param(
            {
                'direct_premium': [
                    build_direct_premium_banner(1),
                    build_direct_premium_banner(2),
                    build_direct_premium_banner(3),
                ],
                'stat': [{'link_head': 'http://eda.yandex.ru'}],
            },
            {
                'id': 'block_1',
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {
                    'ads_only': True,
                    'indexes': [0, 5, 10],  # those would be ignored
                },
            },
            [
                {
                    'place_id': 1,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/1',
                        'click_url': 'http://eda.yandex.ru/click/1',
                    },
                },
                {
                    'place_id': 2,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/2',
                        'click_url': 'http://eda.yandex.ru/click/2',
                    },
                },
                {
                    'place_id': 3,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/3',
                        'click_url': 'http://eda.yandex.ru/click/3',
                    },
                },
            ],
            id='open block with advert settings and ads only',
        ),
        pytest.param(
            {
                'direct_premium': [
                    build_direct_premium_banner(1),
                    build_direct_premium_banner(2),
                    build_direct_premium_banner(3),
                ],
                'stat': [{'link_head': 'http://eda.yandex.ru'}],
            },
            {
                'id': 'block_1',
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {'ads_only': False, 'indexes': [0, 1, 2]},
            },
            [
                {
                    'place_id': 1,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/1',
                        'click_url': 'http://eda.yandex.ru/click/1',
                    },
                },
                {
                    'place_id': 2,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/2',
                        'click_url': 'http://eda.yandex.ru/click/2',
                    },
                },
                {
                    'place_id': 3,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/3',
                        'click_url': 'http://eda.yandex.ru/click/3',
                    },
                },
                {
                    'place_id': (
                        5  # normal place without ads with order persisted
                    ),
                },
                {
                    'place_id': (
                        4  # normal place without ads with order persisted
                    ),
                },
            ],
            id='open block with advert settings and unique indexes',
        ),
        pytest.param(
            {
                'direct_premium': [
                    build_direct_premium_banner(1),
                    build_direct_premium_banner(2),
                    build_direct_premium_banner(3),
                ],
                'stat': [{'link_head': 'http://eda.yandex.ru'}],
            },
            {
                'id': 'block_1',
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {'ads_only': False, 'indexes': [3, 10, 11]},
            },
            [
                {'place_id': 5},
                {'place_id': 4},
                {'place_id': 3},
                {
                    'place_id': 1,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/1',
                        'click_url': 'http://eda.yandex.ru/click/1',
                    },
                },
                {'place_id': 2},
            ],
            id='open block with advert settings and indexes out of range',
        ),
        pytest.param(
            {
                'direct_premium': [
                    build_direct_premium_banner(1),
                    build_direct_premium_banner(2),
                    build_direct_premium_banner(3),
                ],
                'stat': [{'link_head': 'http://eda.yandex.ru'}],
            },
            {
                'id': 'block_1',
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {'ads_only': False, 'indexes': [0]},
            },
            [
                {
                    'place_id': 1,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/1',
                        'click_url': 'http://eda.yandex.ru/click/1',
                    },
                },
                {'place_id': 5},
                {'place_id': 4},
                {'place_id': 3},
                {'place_id': 2},
            ],
            id='open block with advert settings and single index',
        ),
        pytest.param(
            {
                'direct_premium': [
                    build_direct_premium_banner(5),
                    build_direct_premium_banner(1),
                    build_direct_premium_banner(2),
                ],
                'stat': [{'link_head': 'http://eda.yandex.ru'}],
            },
            {
                'id': 'block_1',
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {'ads_only': False, 'indexes': [0, 1, 2]},
            },
            [
                {'place_id': 5},
                {
                    'place_id': 1,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/1',
                        'click_url': 'http://eda.yandex.ru/click/1',
                    },
                },
                {
                    'place_id': 2,
                    'advertisement': {
                        'view_url': 'http://eda.yandex.ru/view/2',
                        'click_url': 'http://eda.yandex.ru/click/2',
                    },
                },
                {'place_id': 4},
                {'place_id': 3},
            ],
            id='do not pessimize positions',
        ),
    ],
)
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
        ermc_models.PlaceBanner(place_id=4, banner_id=4),
        ermc_models.PlaceBanner(place_id=5, banner_id=5),
    ],
)
async def test_block_advert_settings(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        yabs_response,
        block,
        expected_places,
):
    """
    EDACAT-1298: тест проверяет поведение рекламы при использовании рекламных
    настроек блока.
    """

    place_ids: list = [1, 2, 3, 4, 5]

    for place_id in place_ids:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-07-13T10:00:00+00:00'),
                        end=parser.parse('2021-07-13T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/yabs/page/1')
    def _yabs_page(_):
        return yabs_response

    response = await catalog_for_layout(blocks=[block])
    assert response.status == 200

    response_block = layout_utils.find_block(block['id'], response.json())
    assert len(response_block) == len(expected_places)

    for actual, expected in zip(response_block, expected_places):
        assert actual['meta']['place_id'] == expected['place_id']

        features = actual['payload']['data']['features']
        if 'advertisement' not in expected:
            assert 'advertisement' not in features
            layout_utils.assert_no_meta(actual, 'advertisements')
        else:
            assert expected['advertisement'] == features['advertisement']
            meta = layout_utils.find_first_meta('advertisements', actual)
            assert meta['payload'] == {
                'text': {'text': META_TEXT, 'color': META_TEXT_COLOR},
                'background': META_BACKGROUND_COLOR,
            }


@pytest.mark.now('2021-07-13T13:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.parametrize(
    'num_blocks, threshold',
    [
        pytest.param(1, None, id='sigle block with no threshold'),
        pytest.param(1, 0, id='single block with zero threshold'),
        pytest.param(2, None, id='two blocks with no threshold'),
        pytest.param(2, 1, id='two blocks with threshold of one'),
        pytest.param(20, 5, id='many blocks with low threshold'),
        pytest.param(5, 20, id='several blocks with high threshold'),
    ],
)
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
        ermc_models.PlaceBanner(place_id=4, banner_id=4),
        ermc_models.PlaceBanner(place_id=5, banner_id=5),
    ],
)
async def test_advert_auction_config(
        catalog_for_layout,
        taxi_config,
        eats_catalog_storage,
        mockserver,
        num_blocks,
        threshold,
):
    """
    EDACAT-1298: проверяет, что количество аукционов соответствует ограничению
    из конфига EATS_CATALOG_ADVERT_AUCTION_QOS.
    """

    config: dict = {'max_requests_inflight': 1}
    if threshold:
        config['max_auctions'] = threshold

    taxi_config.set_values({'EATS_CATALOG_ADVERT_AUCTION_QOS': config})

    place_ids: list = [1, 2, 3, 4, 5]

    yabs_response: dict = {
        'direct_premium': [],
        'stat': [{'link_head': 'http://eda.yandex.ru'}],
    }
    for place_id in place_ids:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-07-13T10:00:00+00:00'),
                        end=parser.parse('2021-07-13T22:00:00+00:00'),
                    ),
                ],
            ),
        )
        yabs_response['direct_premium'].append(
            build_direct_premium_banner(place_id),
        )

    @mockserver.json_handler('/yabs/page/1')
    def yabs_page(_):
        return yabs_response

    request_blocks: list = []
    for block_id in range(num_blocks):
        request_blocks.append(
            {
                'id': 'block_{}'.format(block_id + 1),
                'type': 'open',
                'advert_settings': {'ads_only': True},
                'disable_filters': False,
            },
        )

    response = await catalog_for_layout(blocks=request_blocks)
    assert response.status == 200

    if not threshold:
        assert yabs_page.times_called == num_blocks
        assert yabs_page.times_called == len(response.json()['blocks'])
    else:
        count = min(threshold, num_blocks)
        assert yabs_page.times_called == count


@pytest.mark.now('2021-07-26T15:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
        ermc_models.PlaceBanner(place_id=4, banner_id=4),
        ermc_models.PlaceBanner(place_id=5, banner_id=5),
    ],
)
async def test_block_with_yabs_params(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    """
    EDACAT-1408: тест проверяет, что в случае, когда в блоке переданы настройки
    аукциона, то используются они.
    """

    place_ids: list = [1, 2, 3, 4, 5]
    blocks_places = {'block_1': place_ids[:3], 'block_2': place_ids[3:]}

    for place_id in place_ids:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-07-26T10:00:00+00:00'),
                        end=parser.parse('2021-07-26T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/yabs/page/1')
    def first_yabs_page(_):
        yabs_response: dict = {
            'direct_premium': [],
            'stat': [{'link_head': 'http://eda.yandex.ru'}],
        }
        for place_id in blocks_places['block_1']:
            yabs_response['direct_premium'].append(
                build_direct_premium_banner(place_id),
            )

        return yabs_response

    @mockserver.json_handler('/yabs/page/2')
    def second_yabs_page(_):
        yabs_response: dict = {
            'direct_premium': [],
            'stat': [{'link_head': 'http://eda.yandex.ru'}],
        }
        for place_id in blocks_places['block_2']:
            yabs_response['direct_premium'].append(
                build_direct_premium_banner(place_id),
            )
        return yabs_response

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'block_1',
                'type': 'open',
                'advert_settings': {'ads_only': True},
                'disable_filters': False,
            },
            {
                'id': 'block_2',
                'type': 'open',
                'advert_settings': {
                    'ads_only': True,
                    'yabs_params': {'page_id': 2, 'target_ref': 'testsuite'},
                },
                'disable_filters': False,
            },
        ],
    )
    assert response.status == 200
    assert first_yabs_page.times_called == 1
    assert second_yabs_page.times_called == 1

    payload = response.json()
    for block_id in blocks_places:
        block = layout_utils.find_block(block_id, payload)
        assert len(blocks_places[block_id]) == len(block)


@pytest.mark.now('2021-03-23T11:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings(
    adverts.YabsSettings(
        page_id=1, target_ref='testsuite', page_ref='testsuite',
    ),
)
@pytest.mark.parametrize(
    'banners_count',
    [
        pytest.param(0, id='no ad banners'),
        pytest.param(3, id='with ad banners'),
    ],
)
async def test_ads_metrics(
        catalog_for_layout,
        taxi_eats_catalog,
        eats_catalog_storage,
        mockserver,
        eats_restapp_marketing_cache_mock,
        taxi_eats_catalog_monitor,
        banners_count,
):
    """EDACAT-1051: тест проверят, что метрики yabs считаются корректно"""

    place_ids = range(1, banners_count + 1)

    for place_id in place_ids:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-03-23T10:00:00+00:00'),
                        end=parser.parse('2021-03-23T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    eats_restapp_marketing_cache_mock.add_banners(
        [
            ermc_models.PlaceBanner(place_id=place_id, banner_id=place_id)
            for place_id in place_ids
        ],
    )

    @mockserver.json_handler('/yabs/page/1')
    def yabs_page(request):
        assert 'page-ref' in request.query
        assert request.query['page-ref'] == 'testsuite'
        banners = [
            build_direct_premium_banner(place_id) for place_id in place_ids
        ]
        return {
            'direct_premium': banners,
            'stat': [{'link_head': 'http://eda.yandex.ru'}],
        }

    await taxi_eats_catalog.tests_control(reset_metrics=True)

    response_metrics = (
        await taxi_eats_catalog_monitor.get_metric('response')
    )['catalog-for-layout']
    assert response_metrics['yabs-response-size'] == {}
    assert response_metrics['ads-places-count'] == {}

    response = await catalog_for_layout(
        blocks=[
            {'id': 'ads', 'type': 'advertisements', 'disable_filters': False},
        ],
    )

    assert response.status == 200

    data = response.json()
    places_in_response = 0
    if place_ids:
        assert yabs_page.times_called == 1
        ad_block = layout_utils.find_block('ads', data)
        places_in_response = len(ad_block)
        assert places_in_response == len(place_ids)
    else:
        layout_utils.assert_no_block_or_empty('ads', data)

    slow_metrics_test = False
    if not slow_metrics_test:
        return

    # Мы используем метрики 'RecentPeriod', где одна эпоха длится 5 секунд.
    # Ждём 6 секунд чтобы текущая эпоха точно была добавлена в метрику.
    await asyncio.sleep(6)

    response_metrics = (
        await taxi_eats_catalog_monitor.get_metric('response')
    )['catalog-for-layout']

    if banners_count != 0:
        yabs_response_size = response_metrics['yabs-response-size']['1min']
        assert yabs_response_size['min'] == 0
        assert yabs_response_size['max'] == banners_count
        assert 0 <= yabs_response_size['avg'] <= banners_count
    else:
        assert response_metrics['yabs-response-size'] == {}

    if places_in_response != 0:
        ads_places_count = response_metrics['ads-places-count']['1min']
        assert ads_places_count['min'] == 0
        assert ads_places_count['max'] == places_in_response
        assert 0 <= ads_places_count['avg'] <= places_in_response
    else:
        assert response_metrics['ads-places-count'] == {}


@pytest.mark.now('2021-09-23T16:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.parametrize(
    'expected_banner_ids, yabs_calls',
    [
        pytest.param([1, 2, 3, 4, 5], 1, id='no filter config'),
        pytest.param(
            [1, 2, 3, 4, 5],
            1,
            marks=(experiments.advert_auction_filter()),
            id='empty filter config',
        ),
        pytest.param(
            [1, 2, 3, 4, 5],
            1,
            marks=(experiments.advert_auction_filter(place_ids=[6])),
            id='no suitable filter config',
        ),
        pytest.param(
            [2, 3, 4, 5],
            1,
            marks=(experiments.advert_auction_filter(place_ids=[1])),
            id='filter place 1',
        ),
        pytest.param(
            [],
            0,
            marks=(
                experiments.advert_auction_filter(place_ids=[1, 2, 3, 4, 5])
            ),
            id='filter all places',
        ),
        pytest.param(
            [2, 3, 4, 5],
            1,
            marks=(experiments.advert_auction_filter(brand_ids=[1])),
            id='filter brand 1',
        ),
        pytest.param(
            [],
            0,
            marks=(
                experiments.advert_auction_filter(brand_ids=[1, 2, 3, 4, 5])
            ),
            id='filter all brands',
        ),
        pytest.param(
            [3],
            1,
            marks=(
                experiments.advert_auction_filter(
                    place_ids=[4, 5], brand_ids=[1, 2],
                )
            ),
            id='filter places and brands',
        ),
    ],
)
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
        ermc_models.PlaceBanner(place_id=4, banner_id=4),
        ermc_models.PlaceBanner(place_id=5, banner_id=5),
    ],
)
async def test_advert_auction_filter_config(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        expected_banner_ids,
        yabs_calls,
):
    """
    EDACAT-1743: проверяет, что конфиг отфильровывает из запроса аукциона
    некоторые рестораны.
    """
    for place_id in [1, 2, 3, 4, 5]:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-09-23T10:00:00+00:00'),
                        end=parser.parse('2021-09-23T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/yabs/page/1')
    def yabs_page(request):
        assert 'additional-banners' in request.query
        banner_ids: list = []
        for banner in json.loads(request.query['additional-banners']):
            banner_ids.append(banner['banner_id'])

        assert sorted(banner_ids) == sorted(expected_banner_ids)

        return {'direct_premium': [], 'stat': []}

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'block_1',
                'type': 'open',
                'advert_settings': {'ads_only': True},
                'disable_filters': False,
            },
        ],
    )
    assert response.status == 200
    assert yabs_page.times_called == yabs_calls


@pytest.mark.now('2021-11-01T16:40:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.parametrize(
    'places, expected_banner_ids',
    [
        pytest.param(
            [
                storage.Place(place_id=1, brand=storage.Brand(brand_id=1)),
                storage.Place(place_id=2, brand=storage.Brand(brand_id=2)),
                storage.Place(place_id=3, brand=storage.Brand(brand_id=3)),
            ],
            [1, 3],
            marks=experiments.advert_auction_filter(
                predicate={
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'place_id',
                        'set_elem_type': 'int',
                        'set': [1, 3],
                    },
                },
            ),
            id='by place id',
        ),
        pytest.param(
            [
                storage.Place(place_id=1, brand=storage.Brand(brand_id=1)),
                storage.Place(place_id=2, brand=storage.Brand(brand_id=2)),
                storage.Place(place_id=3, brand=storage.Brand(brand_id=3)),
            ],
            [2],
            marks=experiments.advert_auction_filter(
                predicate={
                    'type': 'eq',
                    'init': {
                        'arg_name': 'brand_id',
                        'arg_type': 'int',
                        'value': 2,
                    },
                },
            ),
            id='by brand id',
        ),
        pytest.param(
            [
                storage.Place(
                    place_id=1,
                    brand=storage.Brand(brand_id=1),
                    business=storage.Business.Shop,
                ),
                storage.Place(
                    place_id=2,
                    brand=storage.Brand(brand_id=2),
                    business=storage.Business.Store,
                ),
                storage.Place(
                    place_id=3,
                    brand=storage.Brand(brand_id=3),
                    business=storage.Business.Restaurant,
                ),
            ],
            [3],
            marks=experiments.advert_auction_filter(
                predicate={
                    'type': 'not',
                    'predicates': [
                        {
                            'type': 'in_set',
                            'init': {
                                'arg_name': 'business',
                                'set_elem_type': 'string',
                                'set': ['shop', 'store'],
                            },
                        },
                    ],
                },
            ),
            id='by businnes',
        ),
    ],
)
async def test_advert_auction_filter_config_predicate(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        eats_restapp_marketing_cache_mock,
        places: List[storage.Place],
        expected_banner_ids,
):
    """
    EDACAT-199: проверяет, что конфиг отфильровывает из запроса аукциона
    некоторые рестораны, попадающие под предикат.
    """

    for place in places:
        place_id: int = place['id']
        eats_catalog_storage.add_place(place)
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-11-01T10:00:00+00:00'),
                        end=parser.parse('2021-11-01T22:00:00+00:00'),
                    ),
                ],
            ),
        )
        eats_restapp_marketing_cache_mock.add_banner(
            ermc_models.PlaceBanner(place_id=place_id, banner_id=place_id),
        )

    @mockserver.json_handler('/yabs/page/1')
    def _yabs_page(request):
        assert 'additional-banners' in request.query
        banner_ids: list = []
        for banner in json.loads(request.query['additional-banners']):
            banner_ids.append(banner['banner_id'])

        assert sorted(banner_ids) == sorted(expected_banner_ids)

        return {'direct_premium': [], 'stat': []}

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'block_1',
                'type': 'open',
                'advert_settings': {'ads_only': True},
                'disable_filters': False,
            },
        ],
    )
    assert response.status == 200


@pytest.mark.now('2021-12-15T12:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.parametrize(
    'yabs_banners, response_places',
    [
        pytest.param(
            [
                adverts.create_yabs_service_banner(5),
                adverts.create_yabs_service_banner(1),
            ],
            [
                ResponsePlace(5),
                ResponsePlace(1, has_ads=True),
                ResponsePlace(4),
                ResponsePlace(3),
                ResponsePlace(2),
            ],
            id='first place is not advertised because no relaxed dedup exp',
        ),
        pytest.param(
            [
                adverts.create_yabs_service_banner(5),
                adverts.create_yabs_service_banner(1),
            ],
            [
                ResponsePlace(5, has_ads=True),
                ResponsePlace(1, has_ads=True),
                ResponsePlace(4),
                ResponsePlace(3),
                ResponsePlace(2),
            ],
            marks=experiments.relaxed_ads_dedubliation(),
            id='first place advertised because of relaxed dedup exp',
        ),
    ],
)
async def test_adverts_relaxed_dedublication(
        catalog_for_layout,
        eats_catalog_storage,
        eats_restapp_marketing_cache_mock,
        yabs,
        yabs_banners: List[adverts.YabsServiceBanner],
        response_places: List[ResponsePlace],
):
    """
    EDACAT-2190: проверяет, что при включении эксперимента с расслабленной
    рекламной дедубликацией, ресторан становится рекламным, если не меняет
    позицию в блоке.
    """

    yabs.add_banners(yabs_banners)

    place_ids = [1, 2, 3, 4, 5]
    for place_id in place_ids:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-12-15T10:00:00+00:00'),
                        end=parser.parse('2021-12-15T22:00:00+00:00'),
                    ),
                ],
            ),
        )
        eats_restapp_marketing_cache_mock.add_banner(
            ermc_models.PlaceBanner(place_id=place_id, banner_id=place_id),
        )

    block_id: str = 'ads'
    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {
                    'ads_only': False,
                    'indexes': [0, 1, 2, 3, 4],
                },
            },
        ],
    )
    assert response.status == 200
    assert yabs.times_called == 1

    block = layout_utils.find_block(block_id, response.json())
    assert len(block) == len(response_places)
    for block_place, response_place in zip(block, response_places):
        assert block_place['meta']['place_id'] == response_place.place_id
        features = block_place['payload']['data']['features']
        if response_place.has_ads:
            assert 'advertisement' in features
        else:
            assert 'advertisement' not in features


@pytest.mark.now('2021-03-19T11:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
async def test_layout_yandexuid_in_yabs_request(
        catalog_for_layout, eats_catalog_storage, mockserver,
):

    """
    EDACAT-2355: проверяет, что yandexuid корректно пробрасывается
    из куки в Yabs
    """

    for i in range(1, 4):
        eats_catalog_storage.add_place(
            storage.Place(place_id=i, brand=storage.Brand(brand_id=i)),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=i,
                place_id=i,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-03-19T10:00:00+00:00'),
                        end=parser.parse('2021-03-19T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler(
        '/eats-restapp-marketing/internal/marketing/v1/ad/campaigns',
    )
    def restapp_campaigns(_):
        return {'cursor': '', 'campaigns': [{'place_id': 1, 'banner_id': 1}]}

    @mockserver.json_handler('/yabs/page/1')
    def yabs_page(request):
        assert request.query
        assert 'new_yandexuid' in request.query
        assert request.query['new_yandexuid'] == '12345'

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'Cookie': 'yandexuid=12345',
        },
        blocks=[
            {'id': 'ads', 'type': 'advertisements', 'disable_filters': False},
        ],
    )

    assert response.status == 200
    assert restapp_campaigns.times_called == 1
    assert yabs_page.times_called == 1


@pytest.mark.now('2022-03-04T12:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings(
    adverts.YabsSettings(
        page_id=1,
        target_ref='testsuite',
        coefficients=adverts.Coefficients(yabs_ctr=0, send_ctr=True),
    ),
)
@experiments.eats_catalog_yabs_coefficients(
    coefficients=adverts.Coefficients(yabs_ctr=0, send_ctr=True),
)
@experiments.advert_ctr_source(adverts.CTRSource.VIEWED_TO_OPENED)
@pytest.mark.parametrize(
    'places_stats, expected_additional_banners',
    [
        pytest.param(
            [],
            [
                {
                    'banner_id': 1,
                    'ignore_context': True,
                    'value_coefs': {'A': 0, 'B': 0, 'C': 0},
                },
                {
                    'banner_id': 2,
                    'ignore_context': True,
                    'value_coefs': {'A': 0, 'B': 0, 'C': 0},
                },
                {
                    'banner_id': 3,
                    'ignore_context': True,
                    'value_coefs': {'A': 0, 'B': 0, 'C': 0},
                },
            ],
            id='no places stats in cache',
        ),
        pytest.param(
            [
                adverts.PlaceStats(brand_id=1),
                adverts.PlaceStats(brand_id=2),
                adverts.PlaceStats(brand_id=3),
            ],
            [
                {
                    'banner_id': 1,
                    'ignore_context': True,
                    'value_coefs': {'A': 0, 'B': 0, 'C': 0},
                },
                {
                    'banner_id': 2,
                    'ignore_context': True,
                    'value_coefs': {'A': 0, 'B': 0, 'C': 0},
                },
                {
                    'banner_id': 3,
                    'ignore_context': True,
                    'value_coefs': {'A': 0, 'B': 0, 'C': 0},
                },
            ],
            id='no data for places in cache',
        ),
        pytest.param(
            [
                adverts.PlaceStats(brand_id=1, viewed_to_opened=0.5),
                adverts.PlaceStats(brand_id=2, viewed_to_opened=0.4),
                adverts.PlaceStats(brand_id=3, viewed_to_opened=0.3),
            ],
            [
                {
                    'banner_id': 1,
                    'ignore_context': True,
                    'value_coefs': {'A': 0, 'B': 0, 'C': 0.5},
                },
                {
                    'banner_id': 2,
                    'ignore_context': True,
                    'value_coefs': {'A': 0, 'B': 0, 'C': 0.4},
                },
                {
                    'banner_id': 3,
                    'ignore_context': True,
                    'value_coefs': {'A': 0, 'B': 0, 'C': 0.3},
                },
            ],
            id='has data in cache',
        ),
    ],
)
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_ads_yabs_ctr_from_place_stats_cache(
        taxi_eats_catalog,
        eats_catalog_storage,
        mockserver,
        place_stats_cache,
        places_stats: List[adverts.PlaceStats],
        expected_additional_banners,
):
    """
    EDACAT-1130: проверяет, что отправляется ctr из кэша.
    """

    for place_id in [1, 2, 3]:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2022-03-04T09:00:00+00:00'),
                        end=parser.parse('2022-03-04T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    place_stats_cache.add_places_stats(places_stats)
    await place_stats_cache.flush()

    @mockserver.json_handler('/yabs/page/1')
    def yabs_page(request):
        assert 'additional-banners' in request.query

        additional_banners = json.loads(request.query['additional-banners'])
        additional_banners = sorted(
            additional_banners, key=lambda x: x['banner_id'],
        )
        expected = sorted(
            expected_additional_banners, key=lambda x: x['banner_id'],
        )
        assert additional_banners == expected

        return {'service_banner': []}

    response = await taxi_eats_catalog.post(
        '/internal/v1/catalog-for-layout',
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
        },
        json={
            'location': {'longitude': 37.591503, 'latitude': 55.802998},
            'blocks': [
                {
                    'id': 'ads',
                    'type': 'advertisements',
                    'disable_filters': False,
                },
            ],
        },
    )
    assert response.status == 200
    assert yabs_page.times_called == 1


@pytest.mark.now('2022-03-25T14:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.adverts_use_strong_indexing(enabled=True)
@experiments.yabs_settings(
    adverts.YabsSettings(
        page_id=1, target_ref='testsuite', page_ref='testsuite',
    ),
)
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_adverts_use_strong_indexing(
        catalog_for_layout, eats_catalog_storage, yabs,
):
    """
    EDACAT-2612: проверяет, что эксперимент с со строгой стратегией рекламы
    размещает рекламу даже с пониженеим органики.
    """

    yabs.add_banners(
        [
            adverts.create_yabs_service_banner(1),
            adverts.create_yabs_service_banner(2),
            adverts.create_yabs_service_banner(3),
        ],
    )

    place_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for place_id in place_ids:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2022-03-25T09:00:00+00:00'),
                        end=parser.parse('2022-03-25T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    indexes = [0, 5, 9]
    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'ads',
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {'ads_only': False, 'indexes': indexes},
            },
        ],
    )
    assert response.status == 200
    assert yabs.times_called == 1
    block = layout_utils.find_block('ads', response.json())
    assert len(block) == len(place_ids)

    for idx, place in enumerate(block):
        advert = idx in indexes
        if advert:
            assert 'advertisement' in place['payload']['data']['features']
        else:
            assert 'advertisement' not in place['payload']['data']['features']


@pytest.mark.now('2022-03-31T12:00:00+00:00')
@pytest.mark.parametrize(
    'block, expected_slugs',
    [
        pytest.param(
            {'type': 'open', 'disable_filters': False},
            [f'place_{i}' for i in range(1, 4)],
            id='block with no ads has data (sanity check)',
        ),
        pytest.param(
            {'type': 'advertisements', 'disable_filters': False},
            [],
            id=(
                'deprecated advertisements block type filters out all places '
                'when no ads found'
            ),
        ),
        pytest.param(
            {
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {
                    'ads_only': True,
                    'indexes': [i for i in range(0, 10)],
                },
            },
            [],
            id='ads only filters out block (valid behaviour)',
        ),
        pytest.param(
            {
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {
                    'ads_only': False,
                    'indexes': [i for i in range(0, 10)],
                },
            },
            [f'place_{i}' for i in range(1, 4)],
            id='block presents when no ads for mixin found',
        ),
        pytest.param(
            {
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {
                    'ads_only': False,
                    'indexes': [i for i in range(0, 10)],
                },
            },
            [f'place_{i}' for i in range(1, 4)],
            marks=(experiments.adverts_use_strong_indexing(enabled=True)),
            id='block presents when no ads for strong indexes found',
        ),
    ],
)
async def test_auction_filter_out_block(
        catalog_for_layout,
        eats_catalog_storage,
        block: dict,
        expected_slugs: List[str],
):
    """
    EDACAT-2612: тест проверяет, что блок будет присутствовать в выдаче, если
    реклама не пришла или не нашлась для блока.
    """

    for place_id in range(1, 4):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                slug=f'place_{place_id}',
                brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2022-03-31T09:00:00+00:00'),
                        end=parser.parse('2022-03-31T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    block_id = 'ads'
    block['id'] = block_id
    response = await catalog_for_layout(blocks=[block])
    assert response.status == 200

    data = response.json()

    if not expected_slugs:
        layout_utils.assert_no_block_or_empty(block_id, data)
    else:
        actual_block = layout_utils.find_block(block_id, data)
        actual_slugs = layout_utils.get_block_slugs(actual_block)
        assert len(expected_slugs) == len(actual_slugs)


@pytest.mark.now('2022-03-31T14:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings(
    adverts.YabsSettings(
        page_id=1, target_ref='testsuite', page_ref='testsuite',
    ),
)
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[ermc_models.PlaceBanner(place_id=1, banner_id=1)],
)
async def test_ad_flag_analytics_context(
        catalog_for_layout, eats_catalog_storage, yabs,
):
    yabs.add_banner(adverts.create_yabs_service_banner(1))

    place_ids = [1, 2]
    for place_id in place_ids:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                slug=f'slug_{place_id}',
                name=f'name_{place_id}',
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2022-03-31T09:00:00+00:00'),
                        end=parser.parse('2022-03-31T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    block_id = 'ads'
    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {'ads_only': False, 'indexes': [0]},
            },
        ],
    )

    assert response.status == 200
    assert yabs.times_called == 1

    actual_block = layout_utils.find_block(block_id, response.json())
    assert len(place_ids) == len(actual_block)
    advert_place = layout_utils.find_place_by_slug('slug_1', actual_block)

    assert 'advertisement' in advert_place['payload']['data']['features']
    assert (
        eats_analytics.decode(advert_place['payload']['analytics'])
        == eats_analytics.AnalyticsContext(
            item_id='1',
            item_name='name_1',
            item_slug='slug_1',
            item_type=eats_analytics.ItemType.PLACE,
            place_eta=eats_analytics.DeliveryEta(min=25, max=35),
            place_business=(eats_analytics.Business.RESTAURANT),
            is_ad=True,
        )
    )


@experiments.DISABLE_ADVERTS
async def test_adverts_off_in_layout(
        catalog_for_layout, mockserver, eats_catalog_storage,
):
    """
    Проверяет, что эксперимент, отключающий рекламу, работает
    """

    for i in range(1, 4):
        eats_catalog_storage.add_place(
            storage.Place(place_id=i, brand=storage.Brand(brand_id=i)),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=i,
                place_id=i,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-03-19T10:00:00+00:00'),
                        end=parser.parse('2021-03-19T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/yabs/page/1')
    def yabs_page(request):
        assert False

    response = await catalog_for_layout(
        blocks=[
            {'id': 'ads', 'type': 'advertisements', 'disable_filters': False},
        ],
    )
    assert response.status == 200
    assert yabs_page.times_called == 0

    data = response.json()

    blocks = data['blocks']
    assert not blocks


@experiments.DISABLE_ADVERTS
@pytest.mark.now('2021-12-15T12:00:00+00:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
async def test_adverts_no_ads_on_positions(
        catalog_for_layout,
        eats_catalog_storage,
        eats_restapp_marketing_cache_mock,
        yabs,
):
    """
    Проверяет, что если с экспом по отключению рекламы расставить рекламу
    на заданные места, то вернутся только рестораны без рекламы
    """

    yabs_banners = [
        adverts.create_yabs_service_banner(5),
        adverts.create_yabs_service_banner(1),
    ]

    response_places = [
        ResponsePlace(5, has_ads=True),
        ResponsePlace(4),
        ResponsePlace(3),
        ResponsePlace(2),
        ResponsePlace(1, has_ads=True),
    ]

    yabs.add_banners(yabs_banners)

    place_ids = [1, 2, 3, 4, 5]
    for place_id in place_ids:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id, brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-12-15T10:00:00+00:00'),
                        end=parser.parse('2021-12-15T22:00:00+00:00'),
                    ),
                ],
            ),
        )
        eats_restapp_marketing_cache_mock.add_banner(
            ermc_models.PlaceBanner(place_id=place_id, banner_id=place_id),
        )

    block_id: str = 'ads'
    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {
                    'ads_only': False,
                    'indexes': [0, 1, 2, 3, 4],
                },
            },
        ],
    )
    assert response.status == 200
    assert yabs.times_called == 0

    block = layout_utils.find_block(block_id, response.json())
    assert len(block) == len(response_places)
    for block_place, response_place in zip(block, response_places):
        assert block_place['meta']['place_id'] == response_place.place_id
        features = block_place['payload']['data']['features']
        assert 'advertisement' not in features


@pytest.mark.now('2022-04-08T13:10:00+03:00')
@pytest.mark.config(
    EATS_CATALOG_LOG_SETTINGS={'advert_places_params': {'enabled': True}},
)
@experiments.advertisements(source='yabs')
@experiments.yabs_settings(
    adverts.YabsSettings(
        coefficients=adverts.Coefficients(
            relevance_multiplier=1, send_relevance=True,
        ),
    ),
)
@pytest.mark.parametrize(
    'yabs_called,log_called',
    (
        pytest.param(
            0, 1, marks=[experiments.DISABLE_ADVERTS], id='adverts_is_off',
        ),
        pytest.param(1, 0, marks=[], id='adverts_is_on'),
    ),
)
async def test_advert_places_log(
        testpoint,
        eats_restapp_marketing_cache_mock,
        catalog_for_layout,
        eats_catalog_storage,
        yabs,
        yabs_called,
        log_called,
):

    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2022-04-08T09:00:00+03:00'),
            end=parser.parse('2022-04-08T23:00:00+03:00'),
        ),
    ]

    places = [1, 2, 3, 4, 5]

    for place_id in [1, 2, 3, 4, 5]:
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=working_intervals,
            ),
        )
        if place_id < 4:
            eats_restapp_marketing_cache_mock.add_banner(
                ermc_models.PlaceBanner(place_id=place_id, banner_id=place_id),
            )

    banners = [1, 2, 3]
    for banner_id in banners:
        yabs.add_banner(adverts.create_yabs_service_banner(banner_id))

    @testpoint('yt_log_advert_places')
    def _yt_log_advert_places(message):
        data = message['data']
        assert data['request_id'] == 'hello'
        assert data['device_id'] == 'test_simple'
        assert data['trace_id'] != ''
        assert data['handler'] == 'catalog-for-layout'
        assert sorted(data['advert_places']) == sorted([1, 2, 3])

    block_id = 'adverts'
    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {
                    'ads_only': False,
                    'indexes': [0, 1, 2, 3, 4],
                },
            },
        ],
    )

    response_json = response.json()

    assert response.status_code == 200
    assert yabs.times_called == yabs_called
    assert _yt_log_advert_places.times_called == log_called
    assert len(response_json['blocks']) == 1
    assert len(response_json['blocks'][0]['list']) == len(places)


@pytest.mark.now('2022-04-08T13:10:00+03:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings(
    adverts.YabsSettings(
        coefficients=adverts.Coefficients(
            relevance_multiplier=1, send_relevance=True,
        ),
    ),
)
@pytest.mark.parametrize(
    'sort, yabs_called, expected_places_len',
    (
        pytest.param(
            'cheap_first',
            0,
            0,
            marks=[
                experiments.eats_catalog_sort_adverts(
                    True, sort_types=['default'],
                ),
            ],
            id='sort disable adverts is on with sort',
        ),
        pytest.param(
            'default',
            1,
            3,
            marks=[
                experiments.eats_catalog_sort_adverts(
                    True, sort_types=['default'],
                ),
            ],
            id='sort disable adverts is on without sort',
        ),
        pytest.param(
            'cheap_first',
            1,
            3,
            marks=[
                experiments.eats_catalog_sort_adverts(
                    False, sort_types=['default'],
                ),
            ],
            id='sort disable adverts is on with sort',
        ),
        pytest.param(
            'default',
            1,
            3,
            marks=[
                experiments.eats_catalog_sort_adverts(
                    False, sort_types=['default'],
                ),
            ],
            id='sort disable adverts is off without sort',
        ),
        pytest.param(
            'default',
            0,
            0,
            marks=[
                experiments.eats_catalog_sort_adverts(
                    True, sort_types=['default'],
                ),
                experiments.DISABLE_ADVERTS,
            ],
            id='sort disable adverts is off without sort',
        ),
        pytest.param(
            'cheap_first',
            0,
            0,
            marks=[
                experiments.eats_catalog_sort_adverts(
                    True, sort_types=['default'],
                ),
                experiments.DISABLE_ADVERTS,
            ],
            id='sort disable adverts is off with sort',
        ),
        pytest.param(
            'cheap_first',
            1,
            3,
            marks=[
                experiments.eats_catalog_sort_adverts(
                    True, sort_types=['default', 'cheap_first'],
                ),
            ],
            id='sort disable adverts is on with non default sort',
        ),
    ),
)
async def test_sort_adverts(
        eats_restapp_marketing_cache_mock,
        catalog_for_layout,
        eats_catalog_storage,
        yabs,
        sort,
        yabs_called,
        expected_places_len,
):
    """
    EDACAT-2944: проверяет отключение рекламы при передачи сортировки
    Тест кейсы:
    - Эксперимент включен, сортировка передана - рекламы нет
    - Эксперимент включен, сортировка не передана - реклама есть
    - Эксперимент выключен, сортировка передана - реклама есть
    - Эксперимент выключен, сортировка не передана - реклама есть
    - Эксперимент отключения рекламы включен, эксперимент
        сортировки включен и сортировка не передана - рекламы нет
    - Эксперимент отключения рекламы включен, эксперимент
        сортировки включен и сортировка передана - рекламы нет
    """
    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2022-04-08T09:00:00+03:00'),
            end=parser.parse('2022-04-08T23:00:00+03:00'),
        ),
    ]

    places = [1, 2, 3, 4, 5]

    for place_id in places:
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=working_intervals,
            ),
        )
        if place_id < 4:
            eats_restapp_marketing_cache_mock.add_banner(
                ermc_models.PlaceBanner(place_id=place_id, banner_id=place_id),
            )

    banners = [1, 2, 3]
    for banner_id in banners:
        yabs.add_banner(adverts.create_yabs_service_banner(banner_id))

    block = {
        'id': 'adverts',
        'type': 'open',
        'disable_filters': False,
        'advert_settings': {'ads_only': True, 'indexes': [0, 1, 2, 3, 4]},
    }

    response = await catalog_for_layout(blocks=[block], sort=sort)

    response_json = response.json()

    assert response.status_code == 200
    assert yabs.times_called == yabs_called
    blocks = response_json['blocks']
    if expected_places_len:
        assert len(blocks) == 1
        assert len(blocks[0]['list']) == expected_places_len
    else:
        assert not blocks
