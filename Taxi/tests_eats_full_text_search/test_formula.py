import pytest

from . import utils


@pytest.mark.parametrize(
    ('params,headers,personal_phone_id,relev,' 'fts_status_code'),
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
            'formula=formula1',
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
                'x-request-id': 'request1',
            },
            'phone2',
            'formula=formula2',
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
                'x-request-id': 'request1',
            },
            'phone3',
            'all_factors',
            200,
        ),
    ),
)
@pytest.mark.experiments3(filename='eats_fts_saas_formula.json')
async def test_log_factors(
        taxi_eats_full_text_search,
        mockserver,
        testpoint,
        params,
        headers,
        personal_phone_id,
        relev,
        fts_status_code,
):
    """
    Проверяем, что параметр relev управляется черезе эксперимент
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

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        assert request.query['relev'] == relev
        x = utils.get_saas_response(
            [utils.gta_to_document(item_url, utils.item_to_gta(item))],
        )
        return x

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {
            'categories': [
                {'category_id': str(category_id)}
                for category_id in request.json['categories']
            ],
            'products': [utils.to_nomenclature_product(item)],
        }

    headers['X-Eats-User'] = f'personal_phone_id={personal_phone_id}'
    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{slug}'.format(slug=place_slug),
        params=params,
        headers=headers,
    )

    assert _saas_search_proxy.times_called > 0
    assert response.status_code == fts_status_code
