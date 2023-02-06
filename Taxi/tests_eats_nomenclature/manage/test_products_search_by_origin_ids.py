import pytest

HANDLER = '/v1/manage/products/search_by_origin_ids'

BRAND_ID = 1
MOCK_NOW = '2021-09-30T15:00:00+03:00'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_by_origin_ids(taxi_eats_nomenclature, load_json):
    response = await taxi_eats_nomenclature.post(
        HANDLER,
        json={
            'brand_id': BRAND_ID,
            'origin_ids': [
                'origin_1',
                'origin_2',
                'origin_3',
                'origin_4',
                'origin_8',
                'origin_9',
                'origin_10',
                'origin_11',
                'origin_12',
            ],
        },
    )
    assert response.status_code == 200
    expected_json = load_json('response.json')
    assert _sorted_response(response.json()) == _sorted_response(expected_json)


@pytest.mark.now(MOCK_NOW)
async def test_400_too_many_ids(taxi_eats_nomenclature):
    origin_ids = [str(i) for i in range(0, 1001)]
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'brand_id': BRAND_ID, 'origin_ids': origin_ids},
    )
    assert response.status_code == 400


def _sorted_response(data):
    data['products'].sort(key=lambda k: k['id'])
    return data
