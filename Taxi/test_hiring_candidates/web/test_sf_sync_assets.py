import pytest


QUERY = (
    'SELECT asset_id, lead_id, sts, plate_number, vin, release_year '
    'FROM hiring_candidates.assets '
    'ORDER BY asset_id;'
)


@pytest.mark.parametrize(
    ('request_name', 'expected_name'),
    [('delete', 'delete'), ('upsert', 'upsert')],
)
async def test_assets_sync(
        taxi_hiring_candidates_web,
        pgsql,
        load_json,
        request_name,
        expected_name,
):
    request = load_json('requests.json')[request_name]
    expected_results = load_json('expected_results.json')[expected_name]

    response = await taxi_hiring_candidates_web.post(
        request['route'], json=request['body'],
    )
    body = await response.json()

    assert body == expected_results['response']

    cursor = pgsql['hiring_candidates'].cursor()
    cursor.execute(QUERY)
    result = list(list(row) for row in cursor)

    assert result == expected_results['data']
