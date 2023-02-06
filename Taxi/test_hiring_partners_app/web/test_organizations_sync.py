import pytest


QUERY = (
    'SELECT id, name, is_deleted FROM hiring_partners_app.organizations '
    'ORDER BY id;'
)


@pytest.mark.parametrize(
    ('request_name', 'expected_name'),
    [('delete', 'delete'), ('upsert', 'upsert')],
)
async def test_organizations_sync(
        taxi_hiring_partners_app_web,
        pgsql,
        load_json,
        request_name,
        expected_name,
):
    request = load_json('requests.json')[request_name]
    expected_results = load_json('expected_results.json')[expected_name]

    response = await taxi_hiring_partners_app_web.post(
        request['route'], json=request['body'],
    )
    body = await response.json()

    assert body == expected_results['response']

    cursor = pgsql['hiring_partners_app'].cursor()
    cursor.execute(QUERY)
    result = list(list(row) for row in cursor)

    assert result == expected_results['data']
