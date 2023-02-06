import pytest


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.usefixtures(
    'mock_salesforce_auth',
    'mock_salesforce_updated',
    'mock_salesforce_deleted',
    'mock_pd_personal',
    'mock_pd_territories',
)
async def test_hiring_conditions_update(
        run_sf_update_hiring_conditions,
        pgsql,
        load_json,
        mock_salesforce_get_hc,
):
    mock_salesforce_get_hc('must_add')
    mock_salesforce_get_hc('must_update')
    queries = load_json('queries.json')
    cursor = pgsql['hiring_misc'].cursor()

    cursor.execute(queries['next_rev'])
    revision = cursor.fetchone()[0]
    assert revision == 124

    await run_sf_update_hiring_conditions()

    # test dates were updated
    cursor.execute(queries['last_update'])
    _, last_update, last_delete = cursor.fetchone()
    assert str(last_update) == '2020-01-01 00:00:00+03:00'
    assert str(last_delete) == '2020-01-02 00:00:00+03:00'

    # test deleting
    cursor.execute(queries['get_deleted'])
    assert cursor.fetchone() == (True, revision + 1)

    # test updating
    cursor.execute(queries['get_updated'])
    assert cursor.fetchone() == ('AfterUpdate', revision + 1)

    # test not updating
    cursor.execute(queries['get_not_updated'])
    assert cursor.fetchone() == ('MustNotUpdate', 1)

    # test new
    cursor.execute(queries['get_new'])
    assert cursor.fetchone() == ('AddedPark', revision + 1)

    # test territories
    cursor.execute(queries['get_territories'])
    assert cursor.fetchone() == (['0MI3X000000kfxMWAQ', '0MI3X000000kfo3WAA'],)

    # test fleet_type
    cursor.execute(queries['get_fleet_types'])
    assert cursor.fetchone() == ('uberdriver',)

    # test personal data
    cursor.execute(queries['get_extra'])
    extra = cursor.fetchone()[0]
    assert 'DispatchPhone_pd_id' in extra
    assert extra['DispatchPhone_pd_id'] == 'eb79288c2399407c8f1319ed6ba5f873'

    # test new revision
    cursor.execute(queries['next_rev'])
    assert cursor.fetchone()[0] == revision + 2
