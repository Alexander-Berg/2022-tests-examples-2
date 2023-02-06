import pytest

HANDLER = '/v1/manage/tags/search'

SEARCH_PART = 'мо'
MAX_LIMIT = 100


@pytest.mark.parametrize(
    'name_part, expected_tags',
    [
        ('мо', ['Молоко', 'морковь', 'Мороженое']),
        ('Мо', ['Молоко', 'морковь', 'Мороженое']),
        ('к', ['Молоко', 'морковь', 'кефир', 'Каша']),
        ('', ['Молоко', 'морковь', 'Мороженое', 'кефир', 'Каша']),
        ('я', []),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_no_cursor_no_limit(
        taxi_eats_nomenclature, name_part, expected_tags,
):
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'name_part': name_part},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['tags'] == expected_tags


@pytest.mark.parametrize('limit', [1, 2, (MAX_LIMIT - 1), MAX_LIMIT])
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_cursor_limit(taxi_eats_nomenclature, limit):
    cursor = None
    start_idx = 0
    end_idx = limit

    while True:
        response = await taxi_eats_nomenclature.post(
            HANDLER,
            json={'name_part': SEARCH_PART, 'limit': limit, 'cursor': cursor},
        )
        assert response.status_code == 200

        response_json = response.json()
        expected_json = generate_expected_json(
            start_idx=start_idx,
            end_idx=end_idx,
            expected_limit=limit,
            current_cursor=cursor,
        )
        assert response_json == expected_json

        cursor = response_json['cursor']
        start_idx = end_idx
        end_idx += limit

        if len(expected_json['tags']) < limit:
            break


@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_bad_cursor(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'name_part': SEARCH_PART, 'cursor': 'bad_cursor'},
    )

    assert response.status_code == 400


def generate_expected_json(start_idx, end_idx, expected_limit, current_cursor):
    data_for_response = [
        {'name': 'Молоко', 'cursor': 'MQ=='},
        {'name': 'морковь', 'cursor': 'Mg=='},
        {'name': 'Мороженое', 'cursor': 'Mw=='},
    ]

    expected_data = {
        'tags': [
            item['name'] for item in data_for_response[start_idx:end_idx]
        ],
    }

    if expected_data['tags']:
        expected_data['cursor'] = data_for_response[start_idx:end_idx][-1][
            'cursor'
        ]
    else:
        expected_data['cursor'] = current_cursor

    expected_data['limit'] = expected_limit

    return expected_data
