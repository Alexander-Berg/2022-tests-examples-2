import pytest


def get_saved_offers(pgsql):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute('SELECT * FROM ONLY cache.user_offers ')
        db_result = cursor.fetchall()
        fields = [column.name for column in cursor.description]
        return [
            {field: value for field, value in zip(fields, db_res)}
            for db_res in db_result
        ]


def get_loads(pgsql):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(f'SELECT * FROM ONLY cache.offers_loads ')
        db_result = cursor.fetchall()
        fields = [column.name for column in cursor.description]
        return [
            {field: value for field, value in zip(fields, db_res)}
            for db_res in db_result
        ]


def get_details(pgsql):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(f'SELECT * FROM ONLY cache.offers_details ')
        db_result = cursor.fetchall()
        fields = [column.name for column in cursor.description]
        return [
            {field: value for field, value in zip(fields, db_res)}
            for db_res in db_result
        ]


@pytest.mark.pgsql('pricing_data_preparer', files=['yql_loads.sql'])
@pytest.mark.now('2020-08-10T09:00:00.000000+0000')
async def test_offer_load_check(
        taxi_pricing_admin, pgsql, mockserver, load_json,
):
    @mockserver.json_handler('/yql/api/v2/operations/link2/results')
    def _mock_link2_yql_get(request):
        return load_json('yql_offer_error.json')

    @mockserver.json_handler('/yql/api/v2/operations/link3/results')
    def _mock_link3_yql_get(request):
        return load_json('yql_offer_success_truncated.json')

    @mockserver.json_handler('/yql/api/v2/operations/pricing_link3/results')
    def _mock_link4_yql_get(request):
        return load_json('yql_pricing_data.json')

    @mockserver.json_handler('/yql/api/v2/table_data')
    def _mock_table_data_yql_get(request):
        data = request.query
        assert data['cluster'] == 'hahn'
        assert 'tmp/yql/some_table_link' in data['path']
        table = data['path'].replace('tmp/yql/some_table_link_', '')
        name = 'yql_offer_data_{}_0{}.json'.format(table, data['offset'])
        return load_json(name)

    response = await taxi_pricing_admin.post(
        'service/cron', json={'task_name': 'offers-load-check'},
    )
    assert response.status_code == 200

    loads = get_loads(pgsql)
    for load in loads:
        if 'yql_error' in load and load['yql_error']:
            load['yql_error'] = load['yql_error'][:-32]
    assert loads == load_json('loads_after.json')

    offers = get_saved_offers(pgsql)
    for offer in offers:
        offer.pop('last_access_time')
    assert offers == load_json('offers_after.json')

    details = get_details(pgsql)
    for detail in details:
        detail.pop('last_access_time')
    assert details == load_json('details_after.json')
