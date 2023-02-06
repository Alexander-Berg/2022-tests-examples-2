import pytest


HANDLER = '/v1/place/products/info'
PLACE_ID = '1'
ORIGIN_ID_1 = 'item_origin_1_available'
ORIGIN_ID_2 = 'item_origin_2_force_unavailable'
REQUESTED_PRODUCTS = [
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
]
AUTH_HEADERS = {'x-device-id': 'device_id'}


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data_for_autodisable_info_test.sql',
    ],
)
async def test_get_force_unavailable_info(
        enable_get_disable_info_via_service,
        mockserver,
        taxi_eats_nomenclature,
):
    enable_get_disable_info_via_service()

    # both products are available due to db
    # but autodisable info says product 2 is unavailable
    # so we check it in handle response
    @mockserver.json_handler(
        '/eats-retail-products-autodisable/v1/autodisable_info',
    )
    def _mock(request):
        assert len(request.json['origin_ids']) == 2
        response_body = {
            'autodisable_info': [
                {'origin_id': ORIGIN_ID_1, 'is_available': True},
                {'origin_id': ORIGIN_ID_2, 'is_available': False},
            ],
        }
        return mockserver.make_response(status=200, json=response_body)

    request = {'product_ids': REQUESTED_PRODUCTS}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID}', json=request, headers=AUTH_HEADERS,
    )

    assert response.status == 200

    expected_availabilities = {
        REQUESTED_PRODUCTS[0]: True,
        REQUESTED_PRODUCTS[1]: False,
    }
    assert get_items_availabilities(response.json()) == expected_availabilities


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data_for_autodisable_info_test.sql',
    ],
)
@pytest.mark.parametrize('status', [404, 429, 500, 'timeout'])
async def test_force_unavailable_info_bad_response(
        enable_get_disable_info_via_service,
        mockserver,
        taxi_eats_nomenclature,
        # parametrize
        status,
):
    enable_get_disable_info_via_service()

    # check that bad autodisable info response doesn't
    # lead to 500 in nomenclature
    @mockserver.json_handler(
        '/eats-retail-products-autodisable/v1/autodisable_info',
    )
    def _mock(request):
        assert len(request.json['origin_ids']) == 2
        if status == 'timeout':
            raise mockserver.TimeoutError()
        return mockserver.make_response(status=status)

    request = {'product_ids': REQUESTED_PRODUCTS}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID}', json=request, headers=AUTH_HEADERS,
    )

    assert response.status == 200
    # since we don't get autodisable info, both products are available
    expected_availabilities = {
        REQUESTED_PRODUCTS[0]: True,
        REQUESTED_PRODUCTS[1]: True,
    }
    assert get_items_availabilities(response.json()) == expected_availabilities


def get_items_availabilities(response):
    return {item['id']: item['is_available'] for item in response['products']}
