# pylint: disable=C0302
import json
import typing

# pylint: disable=import-error
import eats_restapp_marketing_cache.models as ermc_models
# pylint: enable=import-error
import pytest

from . import catalog
from . import experiments
from . import utils


ELASTIC_INDEX = 'menu_items'

SOURCE_YABS = 'yabs'
SOURCE_CONFIG = 'config'


def make_saas_business(business: catalog.Business) -> int:
    return {
        catalog.Business.Restaurant: 0,
        catalog.Business.Store: 1,
        catalog.Business.Shop: 2,
        catalog.Business.Pharmacy: 3,
        catalog.Business.Zapravki: 4,
    }[business]


def create_saas_group(
        place_id: int,
        business: catalog.Business = catalog.Business.Restaurant,
) -> dict:
    title = 'Рест {}'.format(place_id)
    slug = 'slug_{}'.format(place_id)
    return {
        'CategoryName': '',
        'Document': [
            {
                'ArchiveInfo': {
                    'Charset': 'utf-8',
                    'GtaRelatedAttribute': [
                        {'Key': 'i_type', 'Value': '0'},
                        {'Key': 'i_pid', 'Value': str(place_id)},
                        {'Key': 's_place_slug', 'Value': slug},
                        {'Key': 'title', 'Value': title},
                        {
                            'Key': 'i_business',
                            'Value': str(make_saas_business(business)),
                        },
                        {'Key': 'i_rating', 'Value': '10'},
                        {'Key': 'i_region_id', 'Value': '1'},
                        {
                            'Key': 's_launched_at',
                            'Value': '2017-11-23T00:00:00+03:00',
                        },
                    ],
                    'Headline': '',
                    'IndexGeneration': 0,
                    'Mtime': 1613630349,
                    'Size': 35,
                    'Title': title,
                    'Url': '/' + slug,
                },
                'DocId': '',
                'InternalPriority': 0,
                'Priority': 4,
                'Relevance': 103665208,
                'SInternalPriority': 4,
                'SPriority': 4,
                'SRelevance': 103665208,
            },
        ],
    }


def get_advertiser_settings(settings: dict):
    return pytest.mark.experiments3(
        name='eats_fts_advertiser_settings',
        consumers=['eats-full-text-search/advertiser'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': settings,
            },
        ],
        is_config=True,
    )


def get_advertiser_source(source: str):
    return get_advertiser_settings({'source': source})


def get_place_block_settings(advert_positions: list):
    return pytest.mark.experiments3(
        name='eats_fts_place_block_settings',
        consumers=['eats-full-text-search/catalog-search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'advert_positions': advert_positions},
            },
        ],
    )


def get_yabs_settings(
        page_id: int = 1,
        coefficients: dict = None,
        log_response: bool = False,
        secure_urls_schema: bool = False,
):
    """
    Возвращает конфиг с настройками походда в БК.
    """

    experiment = {
        'page_id': page_id,
        'target_ref': 'testsuite',
        'log_response': log_response,
        'secure_urls_schema': secure_urls_schema,
    }

    if coefficients:
        experiment['coefficients'] = coefficients

    return pytest.mark.experiments3(
        name='eats_fts_yabs_settings',
        consumers=['eats-full-text-search/advertiser'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': experiment,
            },
        ],
        is_config=True,
    )


def get_eats_fts_colors(adverts_label: dict = None):
    value = {
        'adverts_label': {
            'text': 'Рекламная реклама',
            'color': [
                {'theme': 'light', 'color': 'light_color'},
                {'theme': 'dark', 'color': 'dark_color'},
            ],
            'background': [
                {'theme': 'light', 'color': 'light_background'},
                {'theme': 'dark', 'color': 'dark_background'},
            ],
        },
    }

    if adverts_label:
        value['adverts_label'] = adverts_label

    return pytest.mark.experiments3(
        name='eats_fts_colors',
        consumers=['eats-full-text-search/catalog-search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': value,
            },
        ],
        is_config=True,
    )


def advert_auction_filter(
        place_ids: typing.List[int] = None, brand_ids: typing.List[int] = None,
):
    """
    Возвращает эксперимент по фильтрации ресторанов из аукциона.
    """
    return pytest.mark.experiments3(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='advert_auction_filter',
        consumers=['eats-full-text-search/advertiser'],
        clauses=[
            {
                'title': 'Always match',
                'predicate': {'type': 'true'},
                'value': {
                    'brand_ids': brand_ids or [],
                    'place_ids': place_ids or [],
                },
            },
        ],
        is_config=True,
    )


def create_catalog_place(
        place_id: int,
        brand_id: typing.Optional[int] = None,
        business: catalog.Business = catalog.Business.Restaurant,
) -> catalog.Place:
    brand_id_ = brand_id or place_id
    return catalog.Place(
        id=place_id,
        slug=f'slug_{place_id}',
        brand=catalog.Brand(id=brand_id_),
        business=business,
    )


def get_catalog_places() -> typing.List[catalog.Place]:
    places = []
    places.append(
        create_catalog_place(place_id=1, business=catalog.Business.Shop),
    )
    places.append(
        create_catalog_place(place_id=2, business=catalog.Business.Restaurant),
    )
    places.append(
        create_catalog_place(place_id=3, business=catalog.Business.Restaurant),
    )
    places.append(
        create_catalog_place(place_id=4, business=catalog.Business.Restaurant),
    )
    return places


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@get_advertiser_source(SOURCE_YABS)
@pytest.mark.parametrize(
    'banners, yabs_calls, yabs_banners',
    [
        pytest.param([], 0, [], id='no campaigns to call yabs'),
        pytest.param(
            [ermc_models.PlaceBanner(place_id=1, banner_id=1)],
            0,
            [],
            marks=(get_place_block_settings([]),),
            id='no advert positions to call yabs',
        ),
        pytest.param(
            [ermc_models.PlaceBanner(place_id=1, banner_id=1)],
            0,
            [],
            marks=(get_place_block_settings([{'index': 0}]),),
            id='no yabs config',
        ),
        pytest.param(
            [ermc_models.PlaceBanner(place_id=1, banner_id=1)],
            1,
            [],
            marks=(
                get_place_block_settings([{'index': 0}]),
                get_yabs_settings(),
            ),
            id='no yabs banners in response',
        ),
        pytest.param(
            [ermc_models.PlaceBanner(place_id=1, banner_id=1)],
            1,
            [
                {
                    'banner_id': '100',
                    'direct_data': {
                        'url': 'hello',
                        'link_head': 'head',
                        'link_tail': 'tail',
                    },
                },
            ],
            marks=(
                get_place_block_settings([{'index': 0}]),
                get_yabs_settings(),
            ),
            id='different response banners',
        ),
        pytest.param(
            [ermc_models.PlaceBanner(place_id=10, banner_id=10)],
            0,
            [],
            marks=(
                get_place_block_settings([{'index': 0}]),
                get_yabs_settings(),
            ),
            id='no suitable campaigns',
        ),
    ],
)
async def test_search_no_changes(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        load_json,
        banners,
        yabs_calls,
        yabs_banners,
):
    """
    EDACAT-897: проверяет, что ответ сервиса не изменился из-за похода в Yabs.
    """

    places = []
    places.append(
        catalog.Place(id=1, slug='slug_1', business=catalog.Business.Shop),
    )
    places.append(
        catalog.Place(
            id=2, slug='slug_2', business=catalog.Business.Restaurant,
        ),
    )
    places.append(
        catalog.Place(
            id=3, slug='slug_3', business=catalog.Business.Restaurant,
        ),
    )

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    eats_restapp_marketing_cache_mock.add_banners(banners)

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        response = load_json('nomenclature_response.json')
        response['categories'] = [
            {'category_id': str(category_id)}
            for category_id in request.json['categories']
        ]
        return response

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return load_json('umlaas_response.json')

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        return {'service_banner': yabs_banners}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert nomenclature.times_called > 0
    assert umlaas_eats.times_called > 0
    assert eats_restapp_marketing_cache_mock.times_called > 0

    assert yabs.times_called == yabs_calls

    assert response.status == 200
    block = response.json()['blocks'][0]['payload']
    for place in places:
        utils.assert_has_catalog_place(block, place)


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@get_yabs_settings()
@get_advertiser_source(SOURCE_YABS)
@pytest.mark.parametrize(
    'yabs_banners, slugs',
    [
        pytest.param(
            [
                {
                    'banner_id': '1',
                    'direct_data': {
                        'url': 'click',
                        'link_head': 'head_',
                        'link_tail': 'tail',
                    },
                },
            ],
            ['slug_1', 'slug_3', 'slug_2', 'slug_4'],
            marks=(get_place_block_settings([{'index': 0}]),),
            id='single banner in response',
        ),
        pytest.param(
            [
                {
                    'banner_id': '1',
                    'direct_data': {
                        'url': 'click',
                        'link_head': 'head_',
                        'link_tail': 'tail',
                    },
                },
            ],
            ['slug_3', 'slug_1', 'slug_2', 'slug_4'],
            marks=(get_place_block_settings([{'index': 1}]),),
            id='single banner in response on second place',
        ),
        pytest.param(
            [
                {
                    'banner_id': '1',
                    'direct_data': {
                        'url': 'click',
                        'link_head': 'head_',
                        'link_tail': 'tail',
                    },
                },
                {
                    'banner_id': '2',
                    'direct_data': {
                        'url': 'click_2',
                        'link_head': 'head_',
                        'link_tail': 'tail_2',
                    },
                },
            ],
            ['slug_3', 'slug_1', 'slug_2', 'slug_4'],
            marks=(get_place_block_settings([{'index': 1}, {'index': 2}]),),
            id='banners on predefined indexes',
        ),
        pytest.param(
            [
                {
                    'banner_id': '1',
                    'direct_data': {
                        'url': 'click',
                        'link_head': 'head_',
                        'link_tail': 'tail',
                    },
                },
                {
                    'banner_id': '3',
                    'direct_data': {
                        'url': 'click_3',
                        'link_head': 'head_',
                        'link_tail': 'tail_2',
                    },
                },
            ],
            ['slug_3', 'slug_1', 'slug_2', 'slug_4'],
            marks=(get_place_block_settings([{'index': 1}, {'index': 5}]),),
            id='ad position index out of places bounds',
        ),
    ],
)
async def test_search_yabs_ranking(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        eats_restapp_marketing_cache_mock,
        load_json,
        yabs_banners,
        slugs,
):
    """
    EDACAT-897: тест проверяет ранжирование с помощью Yabs.
    """

    places = get_catalog_places()
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        return load_json('nomenclature_response.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return load_json('umlaas_response.json')

    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
    )
    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    )

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        return {'service_banner': yabs_banners}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called == 1
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert nomenclature.times_called > 0
    assert umlaas_eats.times_called > 0
    assert eats_restapp_marketing_cache_mock.times_called > 0

    assert yabs.times_called == 1

    assert response.status == 200

    blocks = response.json()['blocks'][0]['payload']
    assert len(blocks) == len(slugs)
    for block, slug in zip(blocks, slugs):
        assert block['slug'] == slug


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@get_eats_fts_colors()
@get_yabs_settings()
@get_advertiser_source(SOURCE_YABS)
@get_place_block_settings([{'index': 0}])
async def test_search_yabs_links(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        load_json,
):
    """
    EDACAT-897: тест проверяет, что у рекламных ресторанов проставляются
    ссылки на счетчики просмотров и переходов.
    """

    places = get_catalog_places()
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        return load_json('nomenclature_response.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return load_json('umlaas_response.json')

    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
    )
    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    )

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        return {
            'service_banner': [
                {
                    'banner_id': '1',
                    'direct_data': {
                        'url': 'http://ya.ru/ads/slug_1/click',
                        'link_head': 'http://ya.ru/ads',
                        'link_tail': '/slug_1/view',
                    },
                },
            ],
        }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert nomenclature.times_called > 0
    assert umlaas_eats.times_called > 0
    assert eats_restapp_marketing_cache_mock.times_called > 0

    assert yabs.times_called == 1

    assert response.status == 200
    block = response.json()['blocks'][0]['payload']

    place = block.pop(0)
    assert place['slug'] == 'slug_1'
    assert 'advertisements' in place
    assert place['advertisements'] == {
        'view_url': 'http://ya.ru/ads/slug_1/view',
        'click_url': 'http://ya.ru/ads/slug_1/click',
        'label': {
            'text': 'Рекламная реклама',
            'color': [
                {'theme': 'light', 'value': 'light_color'},
                {'theme': 'dark', 'value': 'dark_color'},
            ],
            'background': [
                {'theme': 'light', 'value': 'light_background'},
                {'theme': 'dark', 'value': 'dark_background'},
            ],
        },
    }

    for place in block:
        assert 'advertisements' not in place


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@get_place_block_settings([{'index': 0}])
@get_advertiser_source(SOURCE_YABS)
@pytest.mark.parametrize(
    'expected_banners',
    [
        pytest.param(
            [
                {'banner_id': 3, 'ignore_context': True},
                {'banner_id': 1, 'ignore_context': True},
            ],
            marks=(get_yabs_settings()),
            id='no coefs',
        ),
        pytest.param(
            [
                {
                    'banner_id': 3,
                    'ignore_context': True,
                    'value_coefs': {'A': 1, 'B': 0, 'C': 0},
                },
                {
                    'banner_id': 1,
                    'ignore_context': True,
                    'value_coefs': {'A': 1, 'B': 0, 'C': 0},
                },
            ],
            marks=(
                get_yabs_settings(
                    coefficients={
                        'yabs_ctr': 1,
                        'eats_ctr': 0,
                        'send_relevance': False,
                        'relevance_multiplier': 1,
                    },
                ),
            ),
            id='with yabs ctr',
        ),
        pytest.param(
            [
                {
                    'banner_id': 3,
                    'ignore_context': True,
                    'value_coefs': {'A': 1, 'B': 0, 'C': 2},
                },
                {
                    'banner_id': 1,
                    'ignore_context': True,
                    'value_coefs': {'A': 1, 'B': 0, 'C': 2},
                },
            ],
            marks=(
                get_yabs_settings(
                    coefficients={
                        'yabs_ctr': 1,
                        'eats_ctr': 2,
                        'send_relevance': False,
                        'relevance_multiplier': 1,
                    },
                ),
            ),
            id='with all ctr',
        ),
        pytest.param(
            [
                {
                    'banner_id': 3,
                    'ignore_context': True,
                    'value_coefs': {'A': 1, 'B': 0.95, 'C': 2},
                },
                {
                    'banner_id': 1,
                    'ignore_context': True,
                    'value_coefs': {'A': 1, 'B': 0.55, 'C': 2},
                },
            ],
            marks=(
                get_yabs_settings(
                    coefficients={
                        'yabs_ctr': 1,
                        'eats_ctr': 2,
                        'send_relevance': True,
                        'relevance_multiplier': 1,
                    },
                ),
            ),
            id='with all ctr and relevance',
        ),
        pytest.param(
            [
                {
                    'banner_id': 3,
                    'ignore_context': True,
                    'value_coefs': {'A': 1, 'B': 9.5, 'C': 2},
                },
                {
                    'banner_id': 1,
                    'ignore_context': True,
                    'value_coefs': {'A': 1, 'B': 5.5, 'C': 2},
                },
            ],
            marks=(
                get_yabs_settings(
                    coefficients={
                        'yabs_ctr': 1,
                        'eats_ctr': 2,
                        'send_relevance': True,
                        'relevance_multiplier': 10,
                    },
                ),
            ),
            id='with all ctr and relevance multiplied',
        ),
    ],
)
async def test_search_yabs_coefs(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        load_json,
        expected_banners,
):
    places = get_catalog_places()
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        return load_json('nomenclature_response.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return load_json('umlaas_response.json')

    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
    )
    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    )

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        assert 'additional-banners' in request.query
        assert (
            json.loads(request.query['additional-banners']) == expected_banners
        )
        return {
            'service_banner': [
                {
                    'banner_id': '1',
                    'direct_data': {
                        'url': 'http://ya.ru/ads/slug_1/click',
                        'link_head': 'http://ya.ru/ads',
                        'link_tail': '/slug_1/view',
                    },
                },
            ],
        }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert nomenclature.times_called > 0
    assert umlaas_eats.times_called > 0
    assert eats_restapp_marketing_cache_mock.times_called > 0

    assert yabs.times_called == 1

    assert response.status == 200


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@get_place_block_settings([{'index': 0}])
@get_yabs_settings()
@get_advertiser_source(SOURCE_YABS)
async def test_search_yabs_empty_service_banner(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        load_json,
):
    """
    EDACAT-897: тест проверяет, что у рекламных ресторанов проставляются
    ссылки на счетчики просмотров и переходов.
    """

    places = get_catalog_places()
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        return load_json('nomenclature_response.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return load_json('umlaas_response.json')

    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
    )
    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    )

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        return {}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert nomenclature.times_called > 0
    assert umlaas_eats.times_called > 0
    assert eats_restapp_marketing_cache_mock.times_called > 0

    assert yabs.times_called == 1

    assert response.status == 200
    for block in response.json()['blocks']:
        if block['type'] != 'places':
            pass

        for place in block['payload']:
            assert 'advertisements' not in place


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@get_eats_fts_colors()
@get_yabs_settings()
@get_advertiser_source(SOURCE_YABS)
@get_place_block_settings([{'index': 0}])
async def test_search_yabs_direct_premium_response(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        load_json,
):
    places = get_catalog_places()
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        return load_json('nomenclature_response.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return load_json('umlaas_response.json')

    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
    )
    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    )

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        return {
            'direct_premium': [
                {
                    'bid': '1',
                    'url': 'http://ya.ru/ads/slug_1/click',
                    'link_tail': '/slug_1/view',
                },
            ],
            'stat': [{'link_head': 'http://ya.ru/ads'}],
        }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert nomenclature.times_called > 0
    assert umlaas_eats.times_called > 0
    assert eats_restapp_marketing_cache_mock.times_called > 0

    assert yabs.times_called == 1

    assert response.status == 200
    block = response.json()['blocks'][0]['payload']

    place = block.pop(0)
    assert place['slug'] == 'slug_1'
    assert 'advertisements' in place
    assert place['advertisements'] == {
        'view_url': 'http://ya.ru/ads/slug_1/view',
        'click_url': 'http://ya.ru/ads/slug_1/click',
        'label': {
            'text': 'Рекламная реклама',
            'color': [
                {'theme': 'light', 'value': 'light_color'},
                {'theme': 'dark', 'value': 'dark_color'},
            ],
            'background': [
                {'theme': 'light', 'value': 'light_background'},
                {'theme': 'dark', 'value': 'dark_background'},
            ],
        },
    }

    for place in block:
        assert 'advertisements' not in place


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@pytest.mark.parametrize(
    'slugs',
    [
        pytest.param(
            ['slug_1', 'slug_3', 'slug_2', 'slug_4'],
            marks=(
                get_advertiser_settings(
                    {'source': SOURCE_CONFIG, 'place_ids': [1, 3, 2]},
                ),
                get_place_block_settings(
                    [{'index': 0}, {'index': 1}, {'index': 2}],
                ),
            ),
            id='place ids in order',
        ),
        pytest.param(
            ['slug_1', 'slug_4', 'slug_2', 'slug_3'],
            marks=(
                get_advertiser_settings(
                    {'source': SOURCE_CONFIG, 'brand_ids': [1, 4]},
                ),
                get_place_block_settings([{'index': 0}, {'index': 1}]),
            ),
            id='brand ids in order',
        ),
    ],
)
async def test_advertise_with_config(
        taxi_eats_full_text_search, mockserver, eats_catalog, load_json, slugs,
):
    """
    EDACAT-1131: тест проверяет, что рестораны рекламируются с помощью конфига.
    """

    places = get_catalog_places()
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        group: list = []

        for place in places:
            group.append(
                create_saas_group(place_id=place.id, business=place.business),
            )

        return {
            'Grouping': [
                {
                    'Attr': '',
                    'Group': group,
                    'Mode': 0,
                    'NumDocs': [len(places), 0, 0],
                    'NumGroups': [1, 0, 0],
                },
            ],
        }

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return {'exp_list': [], 'request_id': 'MY_REQ_ID', 'result': []}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert umlaas_eats.times_called > 0

    assert response.status == 200

    blocks = response.json()['blocks'][0]['payload']
    assert len(blocks) == len(slugs)
    for block, slug in zip(blocks, slugs):
        assert block['slug'] == slug


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@get_advertiser_source(SOURCE_YABS)
@get_place_block_settings([{'index': 0}])
@pytest.mark.parametrize(
    'log_times_called',
    [
        pytest.param(
            0,
            marks=(get_yabs_settings(log_response=False)),
            id='log disabled',
        ),
        pytest.param(
            1, marks=(get_yabs_settings(log_response=True)), id='log enabled',
        ),
    ],
)
async def test_search_yabs_log_response(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        load_json,
        testpoint,
        log_times_called,
):
    """
    EDACAT-1209: проверяет, что был залоггирован ответ БК.
    """

    places = get_catalog_places()
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        return load_json('nomenclature_response.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return load_json('umlaas_response.json')

    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
    )
    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    )

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        return {
            'direct_premium': [
                {
                    'bid': '1',
                    'url': 'http://ya.ru/ads/slug_1/click',
                    'link_tail': '/slug_1/view',
                },
            ],
            'stat': [{'link_head': 'http://ya.ru/ads'}],
        }

    @testpoint('yt_yabs_log_message')
    def log_yabs_response(data):
        pass

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert nomenclature.times_called > 0
    assert umlaas_eats.times_called > 0
    assert eats_restapp_marketing_cache_mock.times_called > 0

    assert yabs.times_called == 1
    assert log_yabs_response.times_called == log_times_called

    assert response.status == 200


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@get_place_block_settings([{'index': 0}])
@get_advertiser_source(SOURCE_YABS)
@get_yabs_settings()
async def test_yabs_stat_must_have_link_head(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        load_json,
):
    """
    EDACAT-1287: тест проверяет, что проверяется опциональное поле
    `stat[].link_head` в ответе БК.
    """

    places = get_catalog_places()
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        response = load_json('nomenclature_response.json')
        response['categories'] = [
            {'category_id': str(category_id)}
            for category_id in request.json['categories']
        ]
        return response

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return load_json('umlaas_response.json')

    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
    )
    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    )

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        return {'stat': [{'direct_premium': 0, 'direct_guarantee': 0}]}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert nomenclature.times_called > 0
    assert umlaas_eats.times_called > 0
    assert eats_restapp_marketing_cache_mock.times_called > 0

    assert yabs.times_called == 1

    assert response.status == 200
    block = response.json()['blocks'][0]['payload']
    for place in places:
        utils.assert_has_catalog_place(block, place)


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@get_place_block_settings([{'index': 0}])
@get_advertiser_source(SOURCE_YABS)
@pytest.mark.parametrize(
    'yabs_response, view_url, click_url',
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
            'http://yabs.yandex.ru/count/view/1',
            'http://yabs.yandex.ru/count/click/1',
            marks=(get_yabs_settings()),
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
            'https://yabs.yandex.ru/count/view/1',
            'https://yabs.yandex.ru/count/click/1',
            marks=(get_yabs_settings(secure_urls_schema=True)),
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
            'http://yabs.yandex.ru/count/view/1',
            'http://yabs.yandex.ru/count/click/1',
            marks=(get_yabs_settings()),
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
            'https://yabs.yandex.ru/count/view/1',
            'https://yabs.yandex.ru/count/click/1',
            marks=(get_yabs_settings(secure_urls_schema=True)),
            id='direct_premium secure',
        ),
    ],
)
async def test_yabs_secure_urls_schema(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        yabs_response,
        view_url,
        click_url,
):
    """
    EDACAT-1316: проверяет, что флаг secure_urls_schema меняет http на https
    в counter-ссылках из БК.
    """

    catalog_places = []
    catalog_places.append(catalog.Place(business=catalog.Business.Shop))
    eats_catalog.add_block(
        catalog.Block(id='open', type='open', list=catalog_places),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return {
            'Grouping': [
                {
                    'Attr': '',
                    'Group': [create_saas_group(place_id=1)],
                    'Mode': 0,
                    'NumDocs': [1, 0, 0],
                    'NumGroups': [1, 0, 0],
                },
            ],
        }

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return {'exp_list': [], 'request_id': 'MY_REQ_ID', 'result': []}

    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
    )

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        return yabs_response

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert umlaas_eats.times_called > 0
    assert eats_restapp_marketing_cache_mock.times_called == 1

    assert yabs.times_called == 1

    assert response.status == 200

    blocks = response.json()['blocks'][0]['payload']
    assert len(blocks) == 1

    place = blocks[0]
    assert place['advertisements']['view_url'] == view_url
    assert place['advertisements']['click_url'] == click_url


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': False},
)
@get_place_block_settings([{'index': 0}])
@get_advertiser_settings({'source': SOURCE_CONFIG, 'place_ids': [1]})
@pytest.mark.parametrize(
    'label',
    [
        pytest.param(None, id='no advert color config'),
        pytest.param(
            {'text': 'тестовая реклама', 'color': [], 'background': []},
            marks=(
                get_eats_fts_colors(
                    adverts_label={
                        'text': 'тестовая реклама',
                        'color': [],
                        'background': [],
                    },
                )
            ),
            id='no color and bg config',
        ),
        pytest.param(
            {
                'text': 'тестовая реклама',
                'color': [
                    {'theme': 'light', 'value': '#light'},
                    {'theme': 'dark', 'value': '#dark'},
                ],
                'background': [
                    {'theme': 'light', 'value': '#light'},
                    {'theme': 'dark', 'value': '#dark'},
                ],
            },
            marks=(
                get_eats_fts_colors(
                    adverts_label={
                        'text': 'тестовая реклама',
                        'color': [
                            {'theme': 'light', 'color': '#light'},
                            {'theme': 'dark', 'color': '#dark'},
                        ],
                        'background': [
                            {'theme': 'light', 'color': '#light'},
                            {'theme': 'dark', 'color': '#dark'},
                        ],
                    },
                )
            ),
            id='full config',
        ),
    ],
)
async def test_yabs_advert_color_exp(
        taxi_eats_full_text_search, mockserver, eats_catalog, load_json, label,
):
    """
    EDACAT-1316: проверяет, что флаг secure_urls_schema меняет http на https
    в counter-ссылках из БК.
    """

    catalog_places = []
    catalog_places.append(catalog.Place(business=catalog.Business.Shop))
    eats_catalog.add_block(
        catalog.Block(id='open', type='open', list=catalog_places),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return {
            'Grouping': [
                {
                    'Attr': '',
                    'Group': [
                        {
                            'CategoryName': '',
                            'Document': [
                                {
                                    'ArchiveInfo': {
                                        'Charset': 'utf-8',
                                        'GtaRelatedAttribute': [
                                            {
                                                'Key': 'i_region_id',
                                                'Value': '1',
                                            },
                                            {'Key': 'i_rating', 'Value': '10'},
                                            {
                                                'Key': 'title',
                                                'Value': 'Рест 1',
                                            },
                                            {
                                                'Key': 's_launched_at',
                                                'Value': (
                                                    '2017-11-23T00:00:00+03:00'
                                                ),
                                            },
                                            {
                                                'Key': 'i_business',
                                                'Value': '0',
                                            },
                                            {
                                                'Key': 's_place_slug',
                                                'Value': 'slug_1',
                                            },
                                            {'Key': 'i_pid', 'Value': '1'},
                                            {'Key': 'i_type', 'Value': '0'},
                                        ],
                                        'Headline': '',
                                        'IndexGeneration': 0,
                                        'Mtime': 1613630349,
                                        'Size': 35,
                                        'Title': 'Рест 1',
                                        'Url': '/slug_1',
                                    },
                                    'DocId': '0-1-Z68D440FCE7591BA4',
                                    'InternalPriority': 0,
                                    'Priority': 4,
                                    'Relevance': 103665208,
                                    'SInternalPriority': 4,
                                    'SPriority': 4,
                                    'SRelevance': 103665208,
                                },
                            ],
                        },
                    ],
                    'Mode': 0,
                    'NumDocs': [1, 0, 0],
                    'NumGroups': [1, 0, 0],
                },
            ],
        }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0

    assert response.status == 200

    blocks = response.json()['blocks'][0]['payload']
    assert len(blocks) == 1

    adverts = blocks[0]['advertisements']
    if not label:
        assert 'label' not in adverts
    else:
        assert adverts['label'] == label


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': False,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': False},
)
@get_place_block_settings([{'index': 0}])
@get_yabs_settings()
@pytest.mark.parametrize(
    'yabs_calls, expected_banners',
    [
        pytest.param(
            0,
            {},
            marks=(
                get_advertiser_settings(
                    {
                        'source': SOURCE_YABS,
                        'excluded_businesses': [
                            catalog.Business.Restaurant,
                            catalog.Business.Store,
                            catalog.Business.Shop,
                            catalog.Business.Pharmacy,
                        ],
                    },
                ),
            ),
            id='exclude every business',
        ),
        pytest.param(
            1,
            {1},
            marks=(
                get_advertiser_settings(
                    {
                        'source': SOURCE_YABS,
                        'excluded_businesses': [
                            catalog.Business.Store,
                            catalog.Business.Shop,
                            catalog.Business.Pharmacy,
                        ],
                    },
                ),
            ),
            id='exclude all but restaurant',
        ),
        pytest.param(
            1,
            {1, 2},
            marks=(
                get_advertiser_settings(
                    {
                        'source': SOURCE_YABS,
                        'excluded_businesses': [
                            catalog.Business.Shop,
                            catalog.Business.Pharmacy,
                        ],
                    },
                ),
            ),
            id='exclude all but restaurant and store',
        ),
        pytest.param(
            1,
            {1, 2, 3, 4},
            marks=(
                get_advertiser_settings(
                    {'source': SOURCE_YABS, 'excluded_businesses': []},
                ),
            ),
            id='empty exclude businesses',
        ),
        pytest.param(
            1,
            {1, 2, 3, 4},
            marks=(get_advertiser_settings({'source': SOURCE_YABS}),),
            id='do not exclude anything',
        ),
    ],
)
async def test_advertiser_exclude_businesses(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        yabs_calls,
        expected_banners,
):
    """
    EDACAT-1368: исключает из запроса в рекламу рестораны определнных типов.
    """

    places: list = [
        catalog.Place(
            id=1,
            slug='slug_1',
            brand=catalog.Brand(id=1),
            business=catalog.Business.Restaurant,
        ),
        catalog.Place(
            id=2,
            slug='slug_2',
            brand=catalog.Brand(id=2),
            business=catalog.Business.Store,
        ),
        catalog.Place(
            id=3,
            slug='slug_3',
            brand=catalog.Brand(id=3),
            business=catalog.Business.Shop,
        ),
        catalog.Place(
            id=4,
            slug='slug_4',
            brand=catalog.Brand(id=4),
            business=catalog.Business.Pharmacy,
        ),
    ]

    for place in places:
        eats_restapp_marketing_cache_mock.add_banner(
            ermc_models.PlaceBanner(place_id=place.id, banner_id=place.id),
        )

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        group: list = []

        for place in places:
            place_id = place.id
            business = place.business

            group.append(create_saas_group(place_id, business))

        return {
            'Grouping': [
                {
                    'Attr': '',
                    'Group': group,
                    'Mode': 0,
                    'NumDocs': [len(places), 0, 0],
                    'NumGroups': [1, 0, 0],
                },
            ],
        }

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        assert 'additional-banners' in request.query
        for banner in json.loads(request.query['additional-banners']):
            banner_id: int = banner['banner_id']
            assert banner_id in expected_banners

        return {'direct_premium': [], 'stat': []}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert yabs.times_called == yabs_calls

    assert response.status == 200


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': False,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': False},
)
@get_place_block_settings([{'index': 0}])
@get_yabs_settings()
@get_advertiser_source(SOURCE_YABS)
@pytest.mark.parametrize(
    'expected_banner_ids, yabs_calls',
    [
        pytest.param([1, 2, 3, 4, 5], 1, id='no filter config'),
        pytest.param(
            [1, 2, 3, 4, 5],
            1,
            marks=(advert_auction_filter()),
            id='empty filter config',
        ),
        pytest.param(
            [1, 2, 3, 4, 5],
            1,
            marks=(advert_auction_filter(place_ids=[6])),
            id='no suitable filter config',
        ),
        pytest.param(
            [2, 3, 4, 5],
            1,
            marks=(advert_auction_filter(place_ids=[1])),
            id='filter place 1',
        ),
        pytest.param(
            [],
            0,
            marks=(advert_auction_filter(place_ids=[1, 2, 3, 4, 5])),
            id='filter all places',
        ),
        pytest.param(
            [2, 3, 4, 5],
            1,
            marks=(advert_auction_filter(brand_ids=[1])),
            id='filter brand 1',
        ),
        pytest.param(
            [],
            0,
            marks=(advert_auction_filter(brand_ids=[1, 2, 3, 4, 5])),
            id='filter all brands',
        ),
        pytest.param(
            [3],
            1,
            marks=(advert_auction_filter(place_ids=[4, 5], brand_ids=[1, 2])),
            id='filter places and brands',
        ),
    ],
)
async def test_advert_auction_filter_config(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        expected_banner_ids,
        yabs_calls,
):
    """
    EDACAT-1743: проверяет, что конфиг отфильровывает из запроса аукциона
    некоторые рестораны.
    """

    place_ids: list = [1, 2, 3, 4, 5]
    places = []
    for place_id in place_ids:
        eats_restapp_marketing_cache_mock.add_banner(
            ermc_models.PlaceBanner(place_id=place_id, banner_id=place_id),
        )
        places.append(
            catalog.Place(
                id=place_id,
                slug=f'slug_{place_id}',
                business=catalog.Business.Restaurant,
                brand=catalog.Brand(id=place_id),
            ),
        )

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        group: list = []

        for place_id in place_ids:
            group.append(create_saas_group(place_id))

        return {
            'Grouping': [
                {
                    'Attr': '',
                    'Group': group,
                    'Mode': 0,
                    'NumDocs': [len(place_ids), 0, 0],
                    'NumGroups': [1, 0, 0],
                },
            ],
        }

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        assert 'additional-banners' in request.query
        banner_ids: list = []
        for banner in json.loads(request.query['additional-banners']):
            banner_id: int = banner['banner_id']
            banner_ids.append(banner_id)

        assert sorted(banner_ids) == sorted(expected_banner_ids)

        return {'direct_premium': [], 'stat': []}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert yabs.times_called == yabs_calls

    assert response.status == 200


@pytest.mark.now('2021-09-21T11:16:00+03:00')
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': False,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': False},
)
@get_place_block_settings([{'index': 0}])
@get_yabs_settings()
@get_advertiser_source(SOURCE_YABS)
async def test_ads_ranking_filter_out_unavailable_places(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
):
    """
    EDACAT-1606: проверяет, что в запросаукциона не попадают недоступные
    рестораны.
    """

    places: list = [
        {'place_id': 1, 'available': True},
        {'place_id': 2, 'available': False},
        {'place_id': 3, 'available': True},
        {'place_id': 4, 'available': False},
        {'place_id': 5, 'available': True},
    ]

    catalog_places = []
    for place in places:
        place_id = place['place_id']
        available = place['available']
        eats_restapp_marketing_cache_mock.add_banner(
            ermc_models.PlaceBanner(place_id=place_id, banner_id=place_id),
        )
        catalog_places.append(
            catalog.Place(
                id=place_id,
                slug=f'slug_{place_id}',
                brand=catalog.Brand(id=place_id),
                availability=catalog.Availability(is_available=available),
            ),
        )

    eats_catalog.add_block(
        catalog.Block(id='open', type='open', list=catalog_places),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        group: list = []

        for place in places:
            place_id: int = place['place_id']
            group.append(create_saas_group(place_id))

        return {
            'Grouping': [
                {
                    'Attr': '',
                    'Group': group,
                    'Mode': 0,
                    'NumDocs': [len(places), 0, 0],
                    'NumGroups': [1, 0, 0],
                },
            ],
        }

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        assert 'additional-banners' in request.query
        banner_ids: list = []
        for banner in json.loads(request.query['additional-banners']):
            banner_id: int = banner['banner_id']
            banner_ids.append(banner_id)

        available: list = []
        for place in places:
            if place['available']:
                available.append(place['place_id'])

        assert sorted(banner_ids) == sorted(available)

        return {'direct_premium': [], 'stat': []}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert yabs.times_called == 1

    assert response.status == 200


@pytest.mark.now('2021-09-21T17:10:00+03:00')
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': False,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': False},
)
@get_place_block_settings([{'index': 0}])
@get_yabs_settings()
@get_advertiser_source(SOURCE_YABS)
@pytest.mark.parametrize(
    'delivery_time, yabs_calls',
    [
        pytest.param(None, 1, id='no delivery time means asap'),
        pytest.param(
            '2021-09-21T17:10:00+03:00', 1, id='asap delivery time string',
        ),
        pytest.param(
            {'time': '2021-09-21T17:10:00+03:00', 'zone': 10800},
            1,
            id='asap delivery time object',
        ),
        pytest.param(
            '2021-09-22T17:10:00+03:00', 0, id='preorder delivery time string',
        ),
        pytest.param(
            {'time': '2021-09-21T18:10:00+03:00', 'zone': 10800},
            0,
            id='preorder delivery time object',
        ),
    ],
)
async def test_ads_ranking_ignore_preorder(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        delivery_time,
        yabs_calls,
):
    """
    EDACAT-1606: проверяет, что реклама не запрашивается для предзаказа.
    """

    place_ids: list = [1, 2, 3, 4, 5]
    places = []
    for place_id in place_ids:
        eats_restapp_marketing_cache_mock.add_banner(
            ermc_models.PlaceBanner(place_id=place_id, banner_id=place_id),
        )
        places.append(
            catalog.Place(
                id=place_id,
                slug=f'slug_{place_id}',
                business=catalog.Business.Restaurant,
            ),
        )

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        group: list = []

        for place_id in place_ids:
            group.append(create_saas_group(place_id))

        return {
            'Grouping': [
                {
                    'Attr': '',
                    'Group': group,
                    'Mode': 0,
                    'NumDocs': [len(place_ids), 0, 0],
                    'NumGroups': [1, 0, 0],
                },
            ],
        }

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        return {'direct_premium': [], 'stat': []}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
            'delivery_time': delivery_time,
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert yabs.times_called == yabs_calls

    assert response.status == 200


@pytest.mark.now('2022-02-02T18:05:00+03:00')
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@get_eats_fts_colors()
@get_yabs_settings()
@get_advertiser_source(SOURCE_YABS)
@get_place_block_settings([{'index': 0}])
async def test_check_yandexuid_in_request(
        taxi_eats_full_text_search,
        mockserver,
        eats_restapp_marketing_cache_mock,
        eats_catalog,
        load_json,
):
    """
    EDACAT-2355: проверяет, что yandexuid из куки прокидывается в Yabs
    """

    places = [
        catalog.Place(id=1, slug='slug_1', business=catalog.Business.Shop),
        catalog.Place(
            id=2, slug='slug_2', business=catalog.Business.Restaurant,
        ),
        catalog.Place(
            id=3, slug='slug_3', business=catalog.Business.Restaurant,
        ),
    ]

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return load_json('umlaas_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        response = load_json('nomenclature_response.json')
        response['categories'] = [
            {'category_id': str(category_id)}
            for category_id in request.json['categories']
        ]
        return response

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        assert request.query
        assert 'new_yandexuid' in request.query
        assert request.query['new_yandexuid'] == '12345'

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={
            'Cookie': 'yandexuid=12345',
            'x-request-id': 'testsuite',
            **utils.get_headers(),
        },
    )

    assert response.status == 200

    assert yabs.times_called == 1

    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert umlaas_eats.times_called > 0
    assert nomenclature.times_called > 0


@pytest.mark.now('2022-02-02T18:05:00+03:00')
@get_yabs_settings()
@get_advertiser_source(SOURCE_YABS)
@get_place_block_settings([{'index': 0}])
@pytest.mark.parametrize(
    'ignore_context_value',
    [
        pytest.param(
            False,
            marks=(
                pytest.mark.experiments3(
                    match={
                        'predicate': {'init': {}, 'type': 'true'},
                        'enabled': True,
                    },
                    name='eats_ignore_context_yabs',
                    consumers=['eats-full-text-search/advertiser'],
                    clauses=[
                        {
                            'title': 'Always match',
                            'value': {'enabled': True},
                            'predicate': {'type': 'true'},
                        },
                    ],
                    default_value={},
                ),
            ),
            id='enabled',
        ),
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    match={
                        'predicate': {'init': {}, 'type': 'true'},
                        'enabled': True,
                    },
                    name='eats_ignore_context_yabs',
                    consumers=['eats-full-text-search/advertiser'],
                    clauses=[
                        {
                            'title': 'Always match',
                            'value': {'enabled': False},
                            'predicate': {'type': 'true'},
                        },
                    ],
                    default_value={},
                ),
            ),
            id='disabled',
        ),
        pytest.param(True, id='not found'),
    ],
)
async def test_ignore_context_experiment(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        eats_restapp_marketing_cache_mock,
        load_json,
        ignore_context_value,
):
    """
    EDACAT-2378: выключаем экспом ignore_context
    """

    places = [
        catalog.Place(id=1, slug='slug_1', business=catalog.Business.Shop),
    ]

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        response = load_json('nomenclature_response.json')
        response['categories'] = [
            {'category_id': str(category_id)}
            for category_id in request.json['categories']
        ]
        return response

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        assert 'additional-banners' in request.query
        banners = json.loads(request.query['additional-banners'])
        assert banners[0]['ignore_context'] == ignore_context_value

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'Searching',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert response.status == 200
    assert yabs.times_called == 1

    assert saas.times_called > 0
    assert nomenclature.times_called > 0


@experiments.ADVERTS_OFF
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
async def test_search_disable_advertisements(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        eats_restapp_marketing_cache_mock,
        load_json,
):
    """
    Тест проверяет, что эксп, отключающий рекламу, работает
    """

    places = get_catalog_places()
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        return load_json('nomenclature_response.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return load_json('umlaas_response.json')

    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
    )
    eats_restapp_marketing_cache_mock.add_banner(
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    )

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        assert False

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': 'testsuite', **utils.get_headers()},
    )

    assert response.status == 200

    assert eats_catalog.times_called == 1
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert nomenclature.times_called > 0
    assert umlaas_eats.times_called > 0
    assert eats_restapp_marketing_cache_mock.times_called > 0

    assert yabs.times_called == 0
