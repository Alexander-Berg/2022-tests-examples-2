import pytest


@pytest.mark.pgsql('operation_calculations', files=['pg_doxgety.sql'])
@pytest.mark.parametrize(
    'query, expected_ids, expected_total',
    (
        pytest.param({}, ['b', 'a', 'c'], 3),
        pytest.param({'tariff_zones': ['omsk']}, ['b', 'a'], 2),
        pytest.param({'created_by': 'robot'}, ['b', 'c'], 2),
        pytest.param({'limit': 1, 'offset': 2}, ['c'], 3),
        pytest.param({'tariff_zones': ['adler']}, [], 0),
        pytest.param({'statuses': ['SUCCESS']}, ['b'], 1),
    ),
)
async def test_v1_doxgety_filter_post(
        web_app_client, query, expected_ids, expected_total,
):
    response = await web_app_client.post(f'/v1/doxgety/filter/', json=query)
    res = await response.json()
    ids = [item['task_id'] for item in res['items']]
    assert ids == expected_ids
    assert res['total'] == expected_total
    assert response.status == 200
