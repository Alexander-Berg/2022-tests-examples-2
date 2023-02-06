import pytest

HANDLER = '/v1/manage/product_types/search'

SEARCH_PART = 'мо'
MAX_LIMIT = 100


@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_no_cursor_no_limit(taxi_eats_nomenclature, load_json):
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'name_part': SEARCH_PART},
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
            json={'name_part': SEARCH_PART, 'limit': limit, 'cursor': cursor},
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

        if len(expected_json['product_types']) < limit:
            break


def generate_expected_json(
        load_json, start_idx, end_idx, expected_limit, current_cursor,
):
    expected_data = load_json('full_response.json')

    expected_data['product_types'] = expected_data['product_types'][
        start_idx:end_idx
    ]
    if expected_data['product_types']:
        expected_data['cursor'] = expected_data['product_types'][-1]['cursor']
    else:
        expected_data['cursor'] = current_cursor
    for i in expected_data['product_types']:
        i.pop('cursor')
    expected_data['limit'] = expected_limit

    return expected_data
