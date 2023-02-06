import pytest

from . import utils

LOGGING_FREQUENCY = 1.0
TIMESTAMP_NOW = '2020-01-01T12:00:00+00:00'


def sort_factors(factors):
    return sorted(factors, key=lambda x: x['type'])


@pytest.mark.parametrize(
    ('params,headers,personal_phone_id,' 'msg_source,fts_status_code'),
    (
        (
            {
                'text': 'My Search Text',
                'latitude': 55.725326,
                'longitude': 37.567051,
            },
            {
                'X-Yandex-Uid': 'user1',
                'x-device-id': 'device1',
                'x-request-id': 'request1',
            },
            'phone1',
            'all_categories',
            200,
        ),
        (
            {
                'text': 'My Search Text',
                'latitude': 55.725326,
                'longitude': 37.567051,
            },
            {
                'X-Yandex-Uid': 'user1',
                'x-device-id': 'device1',
                'x-request-id': 'request2',
            },
            'phone2',
            'all_categories',
            200,
        ),
        (
            {
                'text': 'My Search Text',
                'latitude': 55.725326,
                'longitude': 37.567051,
            },
            {
                'X-Yandex-Uid': 'user1',
                'x-device-id': 'device1',
                'x-request-id': 'request3',
            },
            'phone3',
            'all_categories',
            200,
        ),
    ),
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_LOGGING_SETTINGS={
        'enable': True,
        'ratio': LOGGING_FREQUENCY,
    },
)
@pytest.mark.experiments3(filename='eats_fts_saas_factors_logging.json')
async def test_log_factors(
        taxi_eats_full_text_search,
        mockserver,
        testpoint,
        params,
        headers,
        personal_phone_id,
        msg_source,
        fts_status_code,
):
    """
    Проверяем, что факторы которые возвращает SAAS логируются в YT
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
            {'id': 100, 'parent_id': None, 'title': 'My Search Category'},
        ],
        'factors': 'factors1',
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
            {'id': 100, 'parent_id': None, 'title': 'My Search Category'},
        ],
        'factors': 'factors2',
    }

    factors = sort_factors(
        [
            # смотри мапинг id в default/*.sql
            {'id': '10', 'type': 'item', 'value': item['factors']},
            {
                'id': str(category['category_id']),
                'type': 'category',
                'value': category['factors'],
            },
        ],
    )

    category_url = '/{}/categories/{}'.format(
        category['place_id'], category['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        # Проверяем что эксперимент по phone_id применился
        # Во всех кейсах
        if personal_phone_id == 'phone1':
            assert request.query.get('dbgrlv') == 'da'
            assert request.query.get('fsgta') is None
        elif personal_phone_id == 'phone2':
            assert request.query.get('dbgrlv') is None
            assert request.query.get('fsgta') == '_JsonFactors'
        elif personal_phone_id == 'phone3':
            assert request.query.get('dbgrlv') == 'da'
            assert request.query.get('fsgta') == '_JsonFactors'

        x = utils.get_saas_response(
            [
                utils.gta_to_document(item_url, utils.item_to_gta(item)),
                utils.gta_to_document(
                    category_url, utils.category_to_gta(category),
                ),
            ],
        )
        return x

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {
            'categories': [utils.to_nomenclature_category(category)],
            'products': [utils.to_nomenclature_product(item)],
        }

    @testpoint('yt_log_message')
    def _yt_log_message_testpoint(message):
        assert message['personal_phone_id'] == personal_phone_id
        assert sort_factors(message['factors']) == factors

    headers['X-Eats-User'] = f'personal_phone_id={personal_phone_id}'
    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{slug}'.format(slug=place_slug),
        params=params,
        headers=headers,
    )

    assert _yt_log_message_testpoint.times_called == 1

    assert response.status_code == fts_status_code
