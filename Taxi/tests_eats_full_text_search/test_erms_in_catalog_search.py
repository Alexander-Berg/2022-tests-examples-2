import pytest

from . import catalog
from . import configs
from . import experiments
from . import rest_menu_storage
from . import utils


SAAS_PREFIX = 2
REST_MENU_PREFIX = 10

SET_SAAS_SETTINGS = pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS={
        'service': 'eats_fts',
        'prefix': SAAS_PREFIX,
        'misspell': 'try_at_first',
        'prefix_erms_menu': REST_MENU_PREFIX,
    },
)


@experiments.USE_ERMS_IN_CATALOG_SEARCH
@SET_SAAS_SETTINGS
async def test_erms_in_catalog_search(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        rest_menu_storage_items_preview,
):
    """
    Проверяет, что при поиске с каталога и включенном флаге
    1) Есть запрос в erms с айтемами из saas
    2) Нет запроса в elastic search
    3) Модель айтема из erms попадает в ответ поиска
    """

    place_slug = 'slug_1'
    rest = catalog.Place(
        brand=catalog.Brand(id=1),
        business=catalog.Business.Restaurant,
        id=1,
        name='Рест',
        slug=place_slug,
    )
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=[rest]))

    item_id = 'my_item_id'
    disabled_item_id = 'disabled_item_id'
    not_found_item_id = 'not_found_item_id'

    item = rest_menu_storage.ItemPreview(
        id=item_id,
        legacy_id=10,
        adult=False,
        available=True,
        name='Какой-то айтем',
        price='123.45',
        weight_value='999.999',
        weight_unit='l',
        pictures=[rest_menu_storage.ItemPicture(url='http://my_items_image')],
    )

    disabled_item = rest_menu_storage.ItemPreview(
        id=disabled_item_id, legacy_id=20, adult=False, available=False,
    )

    # этот айтем не добавляем в ответ erms
    not_found_item = rest_menu_storage.ItemPreview(
        id=not_found_item_id, legacy_id=20, adult=False, available=False,
    )

    rest_menu_storage_items_preview.places = [
        rest_menu_storage.Place(place_id='1', items=[item, disabled_item]),
    ]

    def rest_menu_storage_callback(request):
        assert len(request.json['places']) == 1
        assert frozenset(request.json['shipping_types']) == frozenset(
            ['delivery', 'pickup'],
        )
        place = request.json['places'][0]
        assert place['place_id'] == '1'
        assert frozenset(place['items']) == frozenset(
            [item_id, disabled_item_id, not_found_item_id],
        )

    rest_menu_storage_items_preview.assert_callback = (
        rest_menu_storage_callback
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        args = request.query
        assert tuple(map(int, args['kps'].split(','))) == (
            SAAS_PREFIX,
            REST_MENU_PREFIX,
        )
        return utils.get_saas_response(
            [
                utils.item_preview_to_saas_doc(
                    place_id='1', place_slug=place_slug, item_preview=item,
                ),
                utils.item_preview_to_saas_doc(
                    place_id='1',
                    place_slug=place_slug,
                    item_preview=disabled_item,
                ),
                utils.item_preview_to_saas_doc(
                    place_id='1',
                    place_slug=place_slug,
                    item_preview=not_found_item,
                ),
            ],
        )

    @mockserver.json_handler(
        '/eats-fts-elastic-search/menu_item_production/_search',
    )
    def eats_fts_elastic_search(_):
        return mockserver.make_response('Internal Server Error', status=500)

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.752338, 'longitude': 37.541323},
        },
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert rest_menu_storage_items_preview.times_called > 0
    assert eats_fts_elastic_search.times_called == 0

    assert response.status == 200

    response_items = response.json()['blocks'][0]['payload'][0]['items']
    assert len(response_items) == 1

    response_item = response_items[0]
    assert response_item['id'] == str(item.legacy_id)
    assert response_item['title'] == str(item.name)
    assert response_item['decimal_price'] == str(item.price)
    assert response_item['weight'] == '999.999 л'
    assert response_item['gallery'][0]['url'] == 'http://my_items_image'


@experiments.USE_ERMS_IN_CATALOG_SEARCH
@SET_SAAS_SETTINGS
async def test_erms_in_catalog_search_error(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        rest_menu_storage_items_preview,
):
    """
    Проверяет, что при 500 erms, сам поиск не 500-тит
    """

    place_slug = 'slug_1'
    rest = catalog.Place(
        brand=catalog.Brand(id=1),
        business=catalog.Business.Restaurant,
        id=1,
        name='Рест',
        slug=place_slug,
    )
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=[rest]))

    rest_menu_storage_items_preview.status_code = 500

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(_):
        return utils.get_saas_response(
            [
                utils.item_preview_to_saas_doc(
                    place_id='1',
                    place_slug=place_slug,
                    item_preview=rest_menu_storage.ItemPreview(),
                ),
            ],
        )

    @mockserver.json_handler(
        '/eats-fts-elastic-search/menu_item_production/_search',
    )
    def eats_fts_elastic_search(_):
        return mockserver.make_response('Internal Server Error', status=500)

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.752338, 'longitude': 37.541323},
        },
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert rest_menu_storage_items_preview.times_called > 0
    assert eats_fts_elastic_search.times_called == 0

    assert response.status == 200

    assert not response.json()['blocks'][0]['payload']


@experiments.USE_ERMS_IN_CATALOG_SEARCH
@SET_SAAS_SETTINGS
async def test_erms_in_catalog_search_pickup(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        rest_menu_storage_items_preview,
):
    """
    Проверяет, что pickup из запроса к поиску
    пробрасывается в erms
    """

    delivery_time = '2022-05-31T12:00:00+00:00'

    place_slug = 'slug_1'
    rest = catalog.Place(
        brand=catalog.Brand(id=1),
        business=catalog.Business.Restaurant,
        id=1,
        name='Рест',
        slug=place_slug,
    )
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=[rest]))

    def rest_menu_storage_callback(request):
        assert len(request.json['places']) == 1
        assert frozenset(request.json['shipping_types']) == frozenset(
            ['pickup'],
        )
        assert request.json['delivery_time'] == delivery_time

    rest_menu_storage_items_preview.assert_callback = (
        rest_menu_storage_callback
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(_):
        return utils.get_saas_response(
            [
                utils.item_preview_to_saas_doc(
                    place_id='1',
                    place_slug=place_slug,
                    item_preview=rest_menu_storage.ItemPreview(),
                ),
            ],
        )

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.752338, 'longitude': 37.541323},
            'shipping_type': 'pickup',
            'delivery_time': {'time': delivery_time, 'zone': 0},
        },
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert rest_menu_storage_items_preview.times_called > 0

    assert response.status == 200


@experiments.USE_ERMS_IN_CATALOG_SEARCH
@configs.rest_availability_settings(erms_batch_size=1)
@SET_SAAS_SETTINGS
async def test_erms_batch(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        rest_menu_storage_items_preview,
):
    """
    Проверяем что производится несколько запросов
    в erms, согласно настройкам
    """

    items_count = 10

    place_slug = 'slug_1'
    rest = catalog.Place(
        brand=catalog.Brand(id=1),
        business=catalog.Business.Restaurant,
        id=1,
        name='Рест',
        slug=place_slug,
    )
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=[rest]))

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(_):
        docs = []
        for idx in range(items_count):
            docs.append(
                utils.item_preview_to_saas_doc(
                    place_id='1',
                    place_slug=place_slug,
                    item_preview=rest_menu_storage.ItemPreview(
                        id=str(idx), name=f'item_{idx}',
                    ),
                ),
            )

        return utils.get_saas_response(docs)

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.752338, 'longitude': 37.541323},
            'shipping_type': 'pickup',
        },
        headers=utils.get_headers(),
    )

    assert (
        rest_menu_storage_items_preview.times_called == items_count
    )  # потому что в конфиге 1
    assert response.status == 200


@experiments.USE_ERMS_IN_CATALOG_SEARCH
@SET_SAAS_SETTINGS
@pytest.mark.parametrize(
    'choosable',
    (pytest.param(False, id='false'), pytest.param(True, id='true')),
)
async def test_choosable(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        rest_menu_storage_items_preview,
        choosable,
):
    """
    Проверяем что choosable=false айтемы не показываются в выдаче
    """

    place_slug = 'slug_1'
    rest = catalog.Place(
        brand=catalog.Brand(id=1),
        business=catalog.Business.Restaurant,
        id=1,
        name='Рест',
        slug=place_slug,
    )
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=[rest]))

    item_id = 'my_item_id'

    item = rest_menu_storage.ItemPreview(
        id=item_id, legacy_id=10, adult=False, choosable=choosable,
    )

    rest_menu_storage_items_preview.places = [
        rest_menu_storage.Place(place_id='1', items=[item]),
    ]

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(_):
        return utils.get_saas_response(
            [
                utils.item_preview_to_saas_doc(
                    place_id='1', place_slug=place_slug, item_preview=item,
                ),
            ],
        )

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.752338, 'longitude': 37.541323},
        },
        headers=utils.get_headers(),
    )

    assert rest_menu_storage_items_preview.times_called > 0
    assert response.status == 200
    block = response.json()['blocks'][0]

    if choosable:
        response_item = block['payload'][0]['items'][0]
        assert response_item['id'] == '10'
    else:
        assert not block['payload']
