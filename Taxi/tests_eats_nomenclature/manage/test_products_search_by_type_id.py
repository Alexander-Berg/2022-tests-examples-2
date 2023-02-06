import pytest

HANDLER = '/v1/manage/products/search_by_type_id'

BRAND_ID = 1
PRODUCT_TYPE_VALUE_UUID = '00000000-0000-0000-0000-000000000001'
MAX_LIMIT = 100
MOCK_NOW = '2021-09-30T15:00:00+03:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_no_cursor_no_limit(taxi_eats_nomenclature, load_json):
    response = await taxi_eats_nomenclature.post(
        HANDLER,
        json={
            'brand_id': BRAND_ID,
            'product_type_id': PRODUCT_TYPE_VALUE_UUID,
        },
    )
    assert response.status_code == 200

    expected_json = generate_expected_json(
        load_json,
        start_idx=0,
        end_idx=MAX_LIMIT,
        expected_limit=MAX_LIMIT,
        current_cursor=None,
    )
    assert response.json() == expected_json


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('limit', [1, 2, (MAX_LIMIT - 1), MAX_LIMIT])
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_cursor_limit(taxi_eats_nomenclature, load_json, limit):
    cursor = None
    start_idx = 0
    end_idx = limit

    while True:
        print(f'Current start index: {start_idx}')

        response = await taxi_eats_nomenclature.post(
            HANDLER,
            json={
                'brand_id': BRAND_ID,
                'product_type_id': PRODUCT_TYPE_VALUE_UUID,
                'limit': limit,
                'cursor': cursor,
            },
        )
        assert response.status_code == 200

        response_json = response.json()
        expected_json = generate_expected_json(
            load_json,
            start_idx=start_idx,
            end_idx=end_idx,
            expected_limit=limit,
            current_cursor=cursor,
        )
        assert response_json == expected_json

        cursor = response_json['cursor']
        start_idx = end_idx
        end_idx += limit

        if len(expected_json['products']) < limit:
            break


@pytest.mark.now(MOCK_NOW)
async def test_404(taxi_eats_nomenclature):
    unknown_type_id = 'unknown_type_id'
    response = await taxi_eats_nomenclature.post(
        HANDLER,
        json={'brand_id': BRAND_ID, 'product_type_id': unknown_type_id},
    )
    assert response.status_code == 404


def generate_expected_json(
        load_json, start_idx, end_idx, expected_limit, current_cursor,
):
    expected_data = load_json('full_response.json')

    expected_data['products'] = expected_data['products'][start_idx:end_idx]
    if expected_data['products']:
        expected_data['cursor'] = expected_data['products'][-1]['cursor']
    else:
        expected_data['cursor'] = current_cursor
    for i in expected_data['products']:
        i.pop('cursor')
    expected_data['limit'] = expected_limit

    return expected_data
