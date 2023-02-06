# pylint: disable=redefined-outer-name
from eats_menu_processor.generated.cron import run_cron


def fetchall(conn, query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def select_all(conn):
    select_all_query = f'select place_group_id, "schema" from dev_filters'
    return fetchall(conn, select_all_query)


async def test_insert_new_filters(
        emp_pgsql_conn, mockserver, mock_eats_place_groups_replica,
):

    epgr_returned_value = [
        {
            'place_group_id': 'place_group_id__1',
            'dev_filter': {
                'filter__1': 'значение на кириллице 1',
                'filter__2': 'значение на кириллице 2',
            },
        },
        {
            'place_group_id': 'place_group_id__2',
            'dev_filter': {
                'filter__1': 'filter__1__value',
                'filter__2': 'filter__value__2',
            },
        },
    ]

    @mock_eats_place_groups_replica('/v1/place_groups')
    def _request(request):
        return {'items': epgr_returned_value}

    assert select_all(emp_pgsql_conn) == []

    await run_cron.main(
        ['eats_menu_processor.crontasks.update_filters', '-t', '0'],
    )

    db_result = select_all(emp_pgsql_conn)

    assert len(db_result) == len(epgr_returned_value)

    for i, item in enumerate(epgr_returned_value):
        assert db_result[i]['place_group_id'] == item['place_group_id']
        assert db_result[i]['schema'] == item['dev_filter']


async def test_update_existing_filters(
        emp_pgsql_conn, emp_filters_factory, mock_eats_place_groups_replica,
):

    emp_filters_factory(
        place_group_id='place_group_id__1',
        schema={
            'filter__1': 'filter__1__value',
            'filter__2': 'filter__value__2',
        },
    )

    epgr_returned_value = [
        {
            'place_group_id': 'place_group_id__1',
            'dev_filter': {'filter__1': 'new_value'},
        },
    ]

    @mock_eats_place_groups_replica('/v1/place_groups')
    def _request(request):
        return {'items': epgr_returned_value}

    await run_cron.main(
        ['eats_menu_processor.crontasks.update_filters', '-t', '0'],
    )

    db_result = select_all(emp_pgsql_conn)

    assert len(db_result) == 1

    for i, item in enumerate(epgr_returned_value):
        assert db_result[i]['place_group_id'] == item['place_group_id']
        assert db_result[i]['schema'] == item['dev_filter']
