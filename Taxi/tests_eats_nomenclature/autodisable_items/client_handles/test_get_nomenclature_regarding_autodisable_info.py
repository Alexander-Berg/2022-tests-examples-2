import pytest


PLACE_SLUG = 'slug'
HEADERS = {'x-device-id': 'device_id'}
CATEGORY_ID = 'category_1_origin'
ORIGIN_ID_1 = 'item_origin_1_available'
ORIGIN_ID_2 = 'item_origin_2_force_unavailable'


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

    response = await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug={PLACE_SLUG}&category_id={CATEGORY_ID}',
        headers=HEADERS,
    )

    assert response.status == 200

    expected_availabilities = {ORIGIN_ID_1: True, ORIGIN_ID_2: False}
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

    response = await taxi_eats_nomenclature.get(
        f'/v1/nomenclature?slug={PLACE_SLUG}&category_id={CATEGORY_ID}',
        headers=HEADERS,
    )

    assert response.status == 200

    # since we don't get autodisable info, both products are available
    expected_availabilities = {ORIGIN_ID_1: True, ORIGIN_ID_2: True}
    assert get_items_availabilities(response.json()) == expected_availabilities


def get_items_availabilities(response):
    items = response['categories'][0]['items']
    return {
        items[0]['id']: items[0]['is_available'],
        items[1]['id']: items[1]['is_available'],
    }
