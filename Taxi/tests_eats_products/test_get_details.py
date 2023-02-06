import pytest

from tests_eats_products import utils


PRODUCTS_HEADERS = {
    'X-AppMetrica-DeviceId': 'device_id',
    'x-platform': 'android_app',
    'x-app-version': '12.11.12',
    'X-Eats-User': 'user_id=456',
}
PLACE_SLUG = 'slug'
DISCOUNT_PROMO = {
    'id': 25,
    'name': 'Скидка для магазинов.',
    'picture_uri': (
        'https://avatars.mds.yandex.net/get-eda/1370147/5b73e9ea19587/80x80'
    ),
    'detailed_picture_url': (
        'https://avatars.mds.yandex.net/get-eda/1370148/5b73e9ea19588/80x80'
    ),
}


@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'fill_additional_data.sql'],
)
async def test_get_details(
        taxi_eats_products, taxi_config, mockserver, load_json,
):
    settings = {'discount_promo': {'enabled': True, **DISCOUNT_PROMO}}
    taxi_config.set(EATS_PRODUCTS_SETTINGS=settings)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature(request):
        assert {p for p in request.json['products']} == {
            'public_101',
            'public_102',
            'public_103',
        }
        assert request.query['slug'] == PLACE_SLUG
        assert request.query['include_unavailable'] == 'true'
        assert (
            request.headers['X-AppMetrica-DeviceId']
            == PRODUCTS_HEADERS['X-AppMetrica-DeviceId']
        )
        assert request.headers['x-platform'] == PRODUCTS_HEADERS['x-platform']
        assert (
            request.headers['x-app-version']
            == PRODUCTS_HEADERS['x-app-version']
        )
        return load_json('nomenclature_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.ASSORTMENT,
        json={
            'place_id': '1',
            'origin_ids': ['origin_id_101', 'origin_id_102', 'origin_id_103'],
        },
        headers=PRODUCTS_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('products_response.json')


@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'fill_additional_data.sql'],
)
async def test_items_not_found_in_mapping(taxi_eats_products):
    response = await taxi_eats_products.post(
        utils.Handlers.ASSORTMENT,
        json={
            'place_id': '8',
            'origin_ids': ['origin_id_101', 'origin_id_102', 'origin_id_999'],
        },
    )
    assert response.status_code == 404
    assert response.json()['error'] == 'not_found_place'


@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'fill_additional_data.sql'],
)
async def test_404_in_nomenclature(taxi_eats_products, mockserver):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature(request):
        return mockserver.make_response(status=404)

    response = await taxi_eats_products.post(
        utils.Handlers.ASSORTMENT,
        json={
            'place_id': '3',
            'origin_ids': ['origin_id_101', 'origin_id_102', 'origin_id_103'],
        },
    )
    assert response.status_code == 404
    assert response.json()['error'] == 'not_found_place'


@pytest.mark.parametrize(
    'max_batch_size, expected_call_times',
    [(1, 3), (2, 2), (3, 1), (10, 1), (100, 1), (1000, 1)],
)
@pytest.mark.pgsql(
    'eats_products',
    files=['pg_eats_products.sql', 'fill_additional_data.sql'],
)
async def test_get_details_with_batch_request(
        taxi_eats_products,
        taxi_config,
        mockserver,
        max_batch_size,
        expected_call_times,
        load_json,
):

    settings = {'max_batch_size': max_batch_size}
    taxi_config.set(EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=settings)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature(request):
        nom_response = load_json('nomenclature_response.json')
        ids = request.json['products']
        nom_response['products'] = [
            i for i in nom_response['products'] if i['product_id'] in ids
        ]

        return nom_response

    response = await taxi_eats_products.post(
        utils.Handlers.ASSORTMENT,
        json={
            'place_id': '1',
            'origin_ids': ['origin_id_101', 'origin_id_102', 'origin_id_103'],
        },
        headers=PRODUCTS_HEADERS,
    )

    # in cpp code we use unordered_map
    # different OS calculate the hash differently, so we need to sort
    data = response.json()
    data['products'].sort(key=lambda i: i['name'])
    load_data = load_json('products_response.json')
    load_data['products'].sort(key=lambda i: i['name'])

    assert _mock_eats_nomenclature.times_called == expected_call_times
    assert response.status_code == 200
    assert data == load_data


async def test_get_details_invalid_request(taxi_eats_products):
    """
    Тест проверяет ответ на запрос без place_id
    """
    response = await taxi_eats_products.post(
        utils.Handlers.ASSORTMENT,
        json={
            'origin_ids': ['origin_id_101', 'origin_id_102', 'origin_id_999'],
        },
    )
    assert response.status_code == 400
