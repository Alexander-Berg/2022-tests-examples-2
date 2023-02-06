import pytest

from generated.clients import salesforce


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.usefixtures(
    'mock_salesforce_auth',
    'mock_salesforce_make_query',
    'mock_salesforce_get_territory',
)
async def test_initial_fetch_territories(
        run_sf_fetch_territories, pgsql, load_json,
):
    queries = load_json('queries.json')
    cursor = pgsql['hiring_misc'].cursor()

    cursor.execute(queries['next_rev'])
    revision = cursor.fetchone()[0]
    assert revision == 1

    await run_sf_fetch_territories()

    # test dates were updated
    cursor.execute(queries['last_update'])
    (last_update,) = cursor.fetchone()
    assert str(last_update) == '2019-01-01 12:00:00+03:00'

    # test territories saved
    cursor.execute(queries['get_all'])
    records = cursor.fetchall()
    expected_records = load_json('expected_records.json')
    records = list(map(list, records))
    assert records == expected_records

    # test revision updated
    cursor.execute(queries['next_rev'])
    assert cursor.fetchone()[0] == revision + 2


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.usefixtures(
    'mock_salesforce_auth',
    'mock_salesforce_make_query',
    'mock_salesforce_get_territory',
)
async def test_refresh_territories(run_sf_fetch_territories, pgsql, load_json):
    queries = load_json('queries.json')
    cursor = pgsql['hiring_misc'].cursor()

    cursor.execute(queries['next_rev'])
    revision = cursor.fetchone()[0]
    assert revision == 124

    await run_sf_fetch_territories()

    # test dates were updated
    cursor.execute(queries['last_update'])
    (last_update,) = cursor.fetchone()
    assert str(last_update) == '2020-01-01 12:00:00+03:00'

    # test territories saved
    cursor.execute(queries['get_all'])
    records = cursor.fetchall()
    expected_records = load_json('expected_records.json')
    records = list(map(list, records))
    assert records == expected_records

    # test revision updated
    cursor.execute(queries['next_rev'])
    assert cursor.fetchone()[0] == revision + 2


@pytest.mark.usefixtures(
    'mock_salesforce_auth', 'mock_salesforce_get_territory',
)
@pytest.mark.parametrize(
    ('territory_name', 'expect_error'),
    [
        ('bad_territory', True),
        ('bad_territory_2', True),
        ('bad_territory_3', True),
        ('good_territory', False),
        ('good_territory_2', False),
    ],
)
async def test_country_code_pattern(
        run_sf_fetch_territories,
        mock_salesforce_make_query_name,
        territory_name,
        expect_error,
):
    mock_salesforce_make_query_name(territory_name)
    if expect_error:
        with pytest.raises(salesforce.GetTerritoryInvalidResponse):
            await run_sf_fetch_territories()
    else:
        await run_sf_fetch_territories()


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.usefixtures(
    'mock_salesforce_auth',
    'mock_salesforce_make_query',
    'mock_salesforce_query_next',
    'mock_salesforce_get_territory',
)
async def test_next_query(run_sf_fetch_territories, pgsql, load_json):
    queries = load_json('queries.json')
    cursor = pgsql['hiring_misc'].cursor()

    await run_sf_fetch_territories()

    # test territories saved
    cursor.execute(queries['get_all'])
    records = cursor.fetchall()
    expected_records = load_json('expected_records.json')
    records = list(map(list, records))
    assert records == expected_records
