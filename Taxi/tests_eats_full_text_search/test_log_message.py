import copy
import datetime

import pytest

from . import translations
from . import utils


SAAS_SERVICE = 'eats_fts_testsute'
SAAS_PREFIX = 1
SAAS_MISSPELL = 'try_at_first'

MIN_SEARCH_TEXT_LENGTH = 3
LOGGING_FREQUENCY = 1.0
TIMESTAMP_NOW = '2020-01-01T12:00:00+00:00'


@pytest.mark.parametrize(
    (
        'params,headers,personal_phone_id,'
        'msg_source,fts_status_code,fts_response'
    ),
    (
        (
            {
                'text': 'My Search Text',
                'latitude': 55.725326,
                'longitude': 37.567051,
                'deliveryTime': '2018-06-14T01:00:00+00:00',
                'shippingType': 'pickup',
            },
            {
                'X-Yandex-Uid': 'user1',
                'x-device-id': 'device1',
                'x-request-id': 'request1',
            },
            'phone1',
            'all_categories',
            200,
            {
                'meta': {},
                'payload': [
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {
                            'title': 'Категории',
                            'type': 'category',
                        },
                        'items': [
                            {
                                'id': 100,
                                'name': 'My Search Category',
                                'parentId': 200,
                                'schedule': None,
                                'gallery': [{'url': 'URL'}],
                                'available': True,
                                'ancestors': [
                                    {
                                        'id': 200,
                                        'name': 'My Base Category',
                                        'parentId': 300,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                            },
                            {
                                'id': 200,
                                'name': 'My Base Category',
                                'parentId': 300,
                                'schedule': None,
                                'gallery': [],
                                'available': True,
                                'ancestors': [
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {'title': 'Товары', 'type': 'item'},
                        'items': [
                            {
                                'id': 10,
                                'name': 'My Search Item',
                                'description': 'Some item description',
                                'available': True,
                                'inStock': 2,
                                'price': 100,
                                'decimalPrice': '100',
                                'promoPrice': None,
                                'decimalPromoPrice': None,
                                'promoTypes': [],
                                'adult': False,
                                'weight': '100 г',
                                'picture': {
                                    'url': 'URL',
                                    'scale': 'aspect_fit',
                                },
                                'optionGroups': [],
                                'ancestors': [
                                    {
                                        'id': 100,
                                        'name': 'My Search Category',
                                        'parentId': 200,
                                        'available': True,
                                        'schedule': None,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 200,
                                        'name': 'My Base Category',
                                        'parentId': 300,
                                        'available': True,
                                        'schedule': None,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                                'shippingType': 'all',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'text': 'My Search Text',
                'shippingType': 'delivery',
                'category': '100',
            },
            {'x-request-id': 'request1'},
            'phone1',
            'category',
            200,
            {
                'meta': {},
                'payload': [
                    {
                        'scopeType': 'category',
                        'scopeBoundary': '100',
                        'itemsType': {
                            'title': 'My Search Category',
                            'type': 'category',
                        },
                        'items': [],
                    },
                    {
                        'scopeType': 'category',
                        'scopeBoundary': '100',
                        'itemsType': {'title': 'Товары', 'type': 'item'},
                        'items': [
                            {
                                'id': 10,
                                'name': 'My Search Item',
                                'description': 'Some item description',
                                'available': True,
                                'inStock': 2,
                                'price': 100,
                                'decimalPrice': '100',
                                'promoPrice': None,
                                'decimalPromoPrice': None,
                                'promoTypes': [],
                                'adult': False,
                                'weight': '100 г',
                                'picture': {
                                    'url': 'URL',
                                    'scale': 'aspect_fit',
                                },
                                'optionGroups': [],
                                'ancestors': [
                                    {
                                        'id': 100,
                                        'name': 'My Search Category',
                                        'parentId': 200,
                                        'available': True,
                                        'schedule': None,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 200,
                                        'name': 'My Base Category',
                                        'parentId': 300,
                                        'available': True,
                                        'schedule': None,
                                        'gallery': [],
                                    },
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                                'shippingType': 'all',
                            },
                        ],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {
                            'title': 'Другие категории',
                            'type': 'category',
                        },
                        'items': [
                            {
                                'id': 200,
                                'name': 'My Base Category',
                                'parentId': 300,
                                'schedule': None,
                                'gallery': [],
                                'available': True,
                                'ancestors': [
                                    {
                                        'id': 300,
                                        'name': 'Root Category',
                                        'parentId': None,
                                        'schedule': None,
                                        'available': True,
                                        'gallery': [],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {
                            'title': 'Совпадения в других категориях',
                            'type': 'item',
                        },
                        'items': [],
                    },
                ],
            },
        ),
    ),
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'misspell': SAAS_MISSPELL,
    },
)
@translations.DEFAULT
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_LOGGING_SETTINGS={
        'enable': True,
        'ratio': LOGGING_FREQUENCY,
    },
)
@pytest.mark.now(TIMESTAMP_NOW)
async def test_yt_log_message_ok_response(
        taxi_eats_full_text_search,
        mockserver,
        testpoint,
        params,
        headers,
        personal_phone_id,
        msg_source,
        fts_status_code,
        fts_response,
):
    """
    Проверяем корректность заполнения полей в log message и наличие
    request_id в запросе к SaaS и ответе от full text search в случае
    успешного поиска.
    Наличие хедеров в запросе к ручке правильно отражается в log message.
    """
    place_slug = 'my_place_slug'

    item = {
        'place_id': 1,
        'place_slug': place_slug,
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My Search Item',
        'in_stock': 2,
        'price': 100,
        'weight': '100 g',
        'adult': False,
        'shipping_type': 0,
        'gallery': [{'url': 'URL', 'scale': 'aspect_fit'}],
        'description': 'Some item description',
        'parent_categories': [
            {'id': 100, 'parent_id': 200, 'title': 'My Search Category'},
            {'id': 200, 'parent_id': 300, 'title': 'My Base Category'},
            {'id': 300, 'parent_id': None, 'title': 'Root Category'},
        ],
    }

    item_url = '/{}/items/{}'.format(
        item['place_id'], item['nomenclature_item_id'],
    )

    category = {
        'place_id': 1,
        'place_slug': place_slug,
        'category_id': 100,
        'title': 'My Search Category',
        'gallery': [{'url': 'URL'}],
        'parent_categories': [
            {'id': 100, 'parent_id': 200, 'title': 'My Search Category'},
            {'id': 200, 'parent_id': 300, 'title': 'My Base Category'},
            {'id': 300, 'parent_id': None, 'title': 'Root Category'},
        ],
    }

    category_url = '/{}/categories/{}'.format(
        category['place_id'], category['category_id'],
    )

    parent_category = {
        'place_id': 1,
        'place_slug': place_slug,
        'category_id': 200,
        'title': 'My Base Category',
        'parent_categories': [
            {'id': 200, 'parent_id': 300, 'title': 'My Base Category'},
            {'id': 300, 'parent_id': None, 'title': 'Root Category'},
        ],
    }

    parent_category_url = '/{}/categories/{}'.format(
        parent_category['place_id'], parent_category['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        assert request.query['reqid'] == headers['x-request-id']
        x = utils.get_saas_response(
            [
                utils.gta_to_document(item_url, utils.item_to_gta(item)),
                utils.gta_to_document(
                    category_url, utils.category_to_gta(category),
                ),
                utils.gta_to_document(
                    parent_category_url,
                    utils.category_to_gta(parent_category),
                ),
            ],
        )
        return x

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {
            'categories': [
                utils.to_nomenclature_category(category),
                utils.to_nomenclature_category(parent_category),
            ],
            'products': [utils.to_nomenclature_product(item)],
        }

    @testpoint('yt_log_message')
    def _yt_log_message_testpoint(message):
        local_time = datetime.datetime.fromisoformat(message['timestamp'])
        request_time = datetime.datetime.fromisoformat(TIMESTAMP_NOW)
        assert local_time.astimezone(datetime.timezone.utc) == request_time

        assert message['personal_phone_id'] == personal_phone_id
        assert message['slug'] == place_slug
        assert message['text'] == params['text']
        assert message['source'] == msg_source
        assert message['data'] == fts_response
        assert message['error'] is None

        for header_key, msg_key in zip(
                ['x-device-id', 'x-request-id', 'X-Yandex-Uid'],
                ['device_id', 'request_id', 'yandex_uid'],
        ):
            if header_key in headers:
                assert headers[header_key] == message[msg_key]
            else:
                assert message[msg_key] == ''

        msg_params = copy.deepcopy(message['query'])
        del params['text']
        assert msg_params == params

    headers['X-Eats-User'] = f'personal_phone_id={personal_phone_id}'

    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{slug}'.format(slug=place_slug),
        params=params,
        headers=headers,
    )

    assert _yt_log_message_testpoint.times_called == 1

    assert response.headers['x-request-id'] == headers['x-request-id']
    assert response.status_code == fts_status_code
    assert response.json() == fts_response


@pytest.mark.parametrize(
    (
        'params,headers,personal_phone_id,'
        'msg_source,fts_status_code,fts_response'
    ),
    (
        (
            {'text': 'No', 'category': '100'},
            {'x-request-id': 'request1'},
            'phone1',
            'category',
            400,
            {
                'code': 'TEXT_TOO_SHORT',
                'message': 'Search text must be bigger than 3 symbols',
            },
        ),
        (
            {'text': 'Ян'},
            {},
            'phone1',
            'all_categories',
            400,
            {
                'code': 'TEXT_TOO_SHORT',
                'message': 'Search text must be bigger than 3 symbols',
            },
        ),
    ),
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_TEXT_SEARCH_SETTINGS={
        'min_search_text_length': MIN_SEARCH_TEXT_LENGTH,
    },
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_LOGGING_SETTINGS={
        'enable': True,
        'ratio': LOGGING_FREQUENCY,
    },
)
@pytest.mark.now(TIMESTAMP_NOW)
async def test_yt_log_message_error(
        taxi_eats_full_text_search,
        testpoint,
        params,
        headers,
        personal_phone_id,
        msg_source,
        fts_status_code,
        fts_response,
):
    """
    Проверяем наличие error в log message в случае если
    запрос к SaaS завершился ошибкой.
    """

    @testpoint('yt_log_message')
    def _yt_log_message_testpoint(message):
        local_time = datetime.datetime.fromisoformat(message['timestamp'])
        request_time = datetime.datetime.fromisoformat(TIMESTAMP_NOW)
        assert local_time.astimezone(datetime.timezone.utc) == request_time

        assert message['personal_phone_id'] == personal_phone_id
        assert message['slug'] == place_slug
        assert message['text'] == params['text']
        assert message['source'] == msg_source
        assert message['data'] is None
        assert message['error'] == fts_response

        params['shippingType'] = 'delivery'
        del params['text']
        assert message['query'] == params

    place_slug = 'my_place_slug'

    headers['X-Eats-User'] = f'personal_phone_id={personal_phone_id}'

    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{slug}'.format(slug=place_slug),
        params=params,
        headers=headers,
    )

    assert _yt_log_message_testpoint.times_called == 1

    assert 'x-request-id' not in response.headers
    assert response.status_code == fts_status_code
    assert response.json() == fts_response


@pytest.mark.parametrize(
    'params,fts_status_code',
    (({'text': 'Correct text'}, 200), ({'text': 'No'}, 400)),
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_LOGGING_SETTINGS={
        'enable': False,
        'ratio': LOGGING_FREQUENCY,
    },
)
async def test_no_log_message_sent(
        taxi_eats_full_text_search,
        mockserver,
        testpoint,
        params,
        fts_status_code,
):
    """
    Проверяем, что сообщение с логом не оптравляется в YT если
    параметр конфига enable равен false.
    """

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return {}

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {}

    @testpoint('yt_log_message')
    def _yt_log_message_testpoint(message):
        pass

    place_slug = 'my_place_slug'

    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{slug}'.format(slug=place_slug),
        params=params,
    )

    assert _yt_log_message_testpoint.times_called == 0
    assert response.status_code == fts_status_code
