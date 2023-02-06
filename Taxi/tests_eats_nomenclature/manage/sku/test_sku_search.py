import pytest

HANDLER = '/v1/manage/sku/search'

SEARCH_PART = 'name'
MAX_LIMIT = 100
UUID_PREFIX = 'd112f20d-20e1-4e2e-bb5e-ce0c4f5d47d'


async def test_no_cursor_no_limit(
        taxi_eats_nomenclature, pgsql, base64_encode,
):
    _sql_insert_sku(pgsql)
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'name_part': SEARCH_PART},
    )
    assert response.status_code == 200

    expected_json = generate_expected_json(
        base64_encode,
        start_idx=0,
        end_idx=MAX_LIMIT,
        expected_limit=MAX_LIMIT,
        current_cursor=None,
    )
    assert _sorted_response(response.json()) == _sorted_response(expected_json)


@pytest.mark.parametrize('limit', [1, 2, (MAX_LIMIT - 1), MAX_LIMIT])
async def test_cursor_limit(
        taxi_eats_nomenclature,
        pgsql,
        base64_encode,
        # parametrize
        limit,
):
    _sql_insert_sku(pgsql)
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
            base64_encode,
            start_idx=start_idx,
            end_idx=end_idx,
            expected_limit=limit,
            current_cursor=cursor,
        )
        assert _sorted_response(response_json) == _sorted_response(
            expected_json,
        )

        cursor = response_json['cursor']
        start_idx = end_idx
        end_idx += limit

        if len(expected_json['skus']) < limit:
            break


async def test_empty_response(taxi_eats_nomenclature, pgsql):
    _sql_insert_sku(pgsql)
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'name_part': 'unknown_search_part'},
    )
    assert response.status_code == 200

    assert response.json() == {'skus': [], 'cursor': '', 'limit': MAX_LIMIT}


def generate_expected_json(
        base64_encode, start_idx, end_idx, expected_limit, current_cursor,
):
    all_skus = [
        {'id': f'{UUID_PREFIX}{i}', 'cursor': base64_encode(i + 1)}
        for i in range(10)
    ]

    expected_data = dict()
    expected_data['skus'] = all_skus[start_idx:end_idx]
    if expected_data['skus']:
        expected_data['cursor'] = expected_data['skus'][-1]['cursor']
    else:
        expected_data['cursor'] = current_cursor
    for i in expected_data['skus']:
        i.pop('cursor')
    expected_data['limit'] = expected_limit

    return expected_data


def _sorted_response(data):
    data['skus'].sort(key=lambda k: k['id'])
    return data


def _sql_insert_sku(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    for i in range(10):
        cursor.execute(
            f"""
        insert into eats_nomenclature.sku (
            uuid, alternate_name
        )
        values (
            '{UUID_PREFIX}{i}', 'name_{i}'
        )
        """,
        )
