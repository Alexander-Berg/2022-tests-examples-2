import pytest


def slug_by_depot_id(depot_id):
    if depot_id == '90213':
        return 'lavka_baryshixa'
    if depot_id == '87840':
        return 'lavka_malomoskovskaya'
    return 'not found'


def get_response_by_slug(search):
    if search == 'lavka_baryshixa':
        return {
            'last_fail_date': '2020-01-03T11:04:31+00:00',
            'last_success_date': '2020-03-03T11:04:31+00:00',
            'slug': 'lavka_baryshixa',
            'depot_id': '90213',
            'errors_count_in_row': 2,
            'source': 'nomenclatures',
            'url_to_kibana': 'https://kibana-testsuite.ru/app/kibana#/discover?_g=(\'filters\'%3A!()%2C\'time\'%3A(\'from\'%3A\'2020-01-03T10%3A04%3A31Z\'%2C\'to\'%3A\'2020-01-03T11%3A04%3A31Z\'))&_a=(\'columns\'%3A!(\'_source\')%2C\'filters\'%3A!((\'%24state\'%3A(\'store\'%3A\'appState\')%2C\'meta\'%3A(\'alias\'%3A!n%2C\'disabled\'%3A!f%2C\'index\'%3A\'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea\'%2C\'key\'%3A\'module\'%2C\'negate\'%3A!f%2C\'params\'%3A!(\'UpdateStatus\'%2C\'HandleRegionId\'%2C\'HandleDepot\'%2C\'UpdateDepotStocks\')%2C\'type\'%3A\'phrase\'%2C\'value\'%3A\'UpdateStatus%2CHandleRegionId%2CHandleDepot%2CUpdateDepotStocks\')%2C\'query\'%3A(\'bool\'%3A(\'minimum_should_match\'%3A1%2C\'should\'%3A!((\'match_phrase\'%3A(\'module\'%3A\'UpdateStatus\'))%2C(\'match_phrase\'%3A(\'module\'%3A\'HandleRegionId\'))%2C(\'match_phrase\'%3A(\'module\'%3A\'HandleDepot\'))%2C(\'match_phrase\'%3A(\'module\'%3A\'UpdateDepotStocks\'))))))%2C(\'%24state\'%3A(\'store\'%3A\'appState\')%2C\'meta\'%3A(\'alias\'%3A!n%2C\'disabled\'%3A!f%2C\'index\'%3A\'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea\'%2C\'key\'%3A\'level\'%2C\'negate\'%3A!f%2C\'params\'%3A!(\'ERROR\'%2C\'WARNING\')%2C\'type\'%3A\'phrase\'%2C\'value\'%3A\'ERROR%2CWARNING\')%2C\'query\'%3A(\'bool\'%3A(\'minimum_should_match\'%3A1%2C\'should\'%3A!((\'match_phrase\'%3A(\'level\'%3A\'ERROR\'))%2C(\'match_phrase\'%3A(\'level\'%3A\'WARNING\'))))))%2C(\'%24state\'%3A(\'store\'%3A\'appState\')%2C\'meta\'%3A(\'alias\'%3A!n%2C\'disabled\'%3A!f%2C\'index\'%3A\'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea\'%2C\'key\'%3A\'ngroups\'%2C\'negate\'%3A!f%2C\'params\'%3A(\'query\'%3A\'testsuite\')%2C\'type\'%3A\'phrase\'%2C\'value\'%3A\'testsuite\')%2C\'query\'%3A(\'match\'%3A(\'ngroups\'%3A(\'query\'%3A\'testsuite\'%2C\'type\'%3A\'phrase\')))))%2C\'index\'%3A\'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea\'%2C\'interval\'%3A\'auto\'%2C\'query\'%3A(\'language\'%3A\'kuery\'%2C\'query\'%3A\'\')%2C\'sort\'%3A!(\'%40timestamp\'%2C\'desc\'))',  # noqa: E501 pylint: disable=line-too-long
        }
    if search == 'lavka_malomoskovskaya':
        return {
            'last_success_date': '2019-12-03T11:04:31+00:00',
            'slug': 'lavka_malomoskovskaya',
            'depot_id': '87840',
            'errors_count_in_row': 0,
            'source': 'stocks',
            'url_to_kibana': 'https://kibana-testsuite.ru/app/kibana#/discover?_g=(\'filters\'%3A!()%2C\'time\'%3A(\'from\'%3A\'now-15m\'%2C\'to\'%3A\'now\'))&_a=(\'columns\'%3A!(\'_source\')%2C\'filters\'%3A!((\'%24state\'%3A(\'store\'%3A\'appState\')%2C\'meta\'%3A(\'alias\'%3A!n%2C\'disabled\'%3A!f%2C\'index\'%3A\'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea\'%2C\'key\'%3A\'module\'%2C\'negate\'%3A!f%2C\'params\'%3A!(\'UpdateStatus\'%2C\'HandleRegionId\'%2C\'HandleDepot\'%2C\'UpdateDepotStocks\')%2C\'type\'%3A\'phrase\'%2C\'value\'%3A\'UpdateStatus%2CHandleRegionId%2CHandleDepot%2CUpdateDepotStocks\')%2C\'query\'%3A(\'bool\'%3A(\'minimum_should_match\'%3A1%2C\'should\'%3A!((\'match_phrase\'%3A(\'module\'%3A\'UpdateStatus\'))%2C(\'match_phrase\'%3A(\'module\'%3A\'HandleRegionId\'))%2C(\'match_phrase\'%3A(\'module\'%3A\'HandleDepot\'))%2C(\'match_phrase\'%3A(\'module\'%3A\'UpdateDepotStocks\'))))))%2C(\'%24state\'%3A(\'store\'%3A\'appState\')%2C\'meta\'%3A(\'alias\'%3A!n%2C\'disabled\'%3A!f%2C\'index\'%3A\'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea\'%2C\'key\'%3A\'level\'%2C\'negate\'%3A!f%2C\'params\'%3A!(\'ERROR\'%2C\'WARNING\')%2C\'type\'%3A\'phrase\'%2C\'value\'%3A\'ERROR%2CWARNING\')%2C\'query\'%3A(\'bool\'%3A(\'minimum_should_match\'%3A1%2C\'should\'%3A!((\'match_phrase\'%3A(\'level\'%3A\'ERROR\'))%2C(\'match_phrase\'%3A(\'level\'%3A\'WARNING\'))))))%2C(\'%24state\'%3A(\'store\'%3A\'appState\')%2C\'meta\'%3A(\'alias\'%3A!n%2C\'disabled\'%3A!f%2C\'index\'%3A\'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea\'%2C\'key\'%3A\'ngroups\'%2C\'negate\'%3A!f%2C\'params\'%3A(\'query\'%3A\'testsuite\')%2C\'type\'%3A\'phrase\'%2C\'value\'%3A\'testsuite\')%2C\'query\'%3A(\'match\'%3A(\'ngroups\'%3A(\'query\'%3A\'testsuite\'%2C\'type\'%3A\'phrase\')))))%2C\'index\'%3A\'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea\'%2C\'interval\'%3A\'auto\'%2C\'query\'%3A(\'language\'%3A\'kuery\'%2C\'query\'%3A\'\')%2C\'sort\'%3A!(\'%40timestamp\'%2C\'desc\'))',  # noqa: E501 pylint: disable=line-too-long
        }

    return {}


@pytest.mark.parametrize('search', ['90213', '87840'])
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_search_by_depot_id(
        taxi_overlord_catalog, search, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list',
        json={
            'search': search,
            'order_by': 'last_success_date',
            'order_direction': 'desc',
        },
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == 1
    slug = response.json()['payload'][0]['slug']
    assert response.json()['payload'] == [get_response_by_slug(slug)]


@pytest.mark.parametrize(
    'search', ['lavka_baryshixa', 'lavka_malomoskovskaya'],
)
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_search_by_slug(
        taxi_overlord_catalog, search, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list',
        json={
            'search': search,
            'order_by': 'last_success_date',
            'order_direction': 'desc',
        },
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == 1
    slug = response.json()['payload'][0]['slug']
    assert response.json()['payload'] == [get_response_by_slug(slug)]


@pytest.mark.parametrize('search', ['lavka_', 'l', 'a', 'vka', '0'])
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_search_by_substr(
        taxi_overlord_catalog, search, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list',
        json={
            'search': search,
            'order_by': 'last_success_date',
            'order_direction': 'desc',
        },
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == 2
    for depot_response in response.json()['payload']:
        slug = depot_response['slug']
        assert depot_response == get_response_by_slug(slug)


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_search_not_found(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list',
        json={
            'search': 'blabla123123',
            'order_by': 'last_success_date',
            'order_direction': 'desc',
        },
    )

    assert response.status_code == 200
    assert not response.json()['payload']


@pytest.mark.parametrize('search', ['lavka_'])
@pytest.mark.parametrize(
    'order_by', ['last_success_date', 'errors_count_in_row'],
)
@pytest.mark.parametrize(
    'order_direction, expected_order',
    [('desc', ['90213', '87840']), ('asc', ['87840', '90213'])],
)
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_order_by(
        taxi_overlord_catalog,
        search,
        order_by,
        order_direction,
        expected_order,
        mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list',
        json={
            'search': search,
            'order_by': order_by,
            'order_direction': order_direction,
        },
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == 2

    for i, depot_response in enumerate(response.json()['payload']):
        assert depot_response['slug'] == slug_by_depot_id(expected_order[i])
        assert depot_response['depot_id'] == expected_order[i]


@pytest.mark.parametrize('search', ['lavka_'])
@pytest.mark.parametrize(
    'order_by, expected_order',
    [('desc', ['90213', '87840']), ('asc', ['90213', '87840'])],
)
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_order_by_with_null(
        taxi_overlord_catalog,
        search,
        order_by,
        expected_order,
        mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list',
        json={
            'search': search,
            'order_by': 'last_fail_date',
            'order_direction': order_by,
        },
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == len(expected_order)

    for i, depot_response in enumerate(response.json()['payload']):
        expected_slug = slug_by_depot_id(expected_order[i])
        assert depot_response == get_response_by_slug(expected_slug)

    assert 'last_fail_date' in response.json()['payload'][0]
    assert 'last_fail_date' not in response.json()['payload'][1]


@pytest.mark.parametrize('search', ['lavka_'])
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_show_errors(taxi_overlord_catalog, search, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list',
        json={'search': search, 'show_depots_with_errors': True},
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == 1
    assert response.json()['payload'] == [
        get_response_by_slug(slug_by_depot_id('90213')),
    ]


@pytest.mark.parametrize('search', ['lavka_'])
@pytest.mark.parametrize(
    'success_from, success_to, expected_depot_ids',
    [
        ('2020-02-10T00:30:00+03:00', '2020-04-10T00:30:00+03:00', ['90213']),
        ('2019-10-10T00:30:00+03:00', '2020-01-10T00:30:00+03:00', ['87840']),
        ('2019-10-10T00:30:00+03:00', None, ['87840', '90213']),
        ('2020-01-10T00:30:00+03:00', None, ['90213']),
    ],
)
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_dates_interval_select(
        taxi_overlord_catalog,
        search,
        success_from,
        success_to,
        expected_depot_ids,
        mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    json = {
        'search': search,
        'order_by': 'errors_count_in_row',
        'order_direction': 'asc',
    }
    if success_from is not None:
        json['last_success_date_from'] = success_from

    if success_to is not None:
        json['last_success_date_to'] = success_to

    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list', json=json,
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == len(expected_depot_ids)
    for i, depot_response in enumerate(response.json()['payload']):
        expected_slug = slug_by_depot_id(expected_depot_ids[i])
        assert depot_response == get_response_by_slug(expected_slug)


@pytest.mark.parametrize('search', ['lavka_'])
@pytest.mark.parametrize(
    'fail_from, fail_to, expected_depot_ids',
    [
        ('2019-02-10T00:30:00+03:00', '2020-04-10T00:30:00+03:00', ['90213']),
        (None, '2020-04-10T00:30:00+03:00', ['90213']),
        ('2019-02-10T00:30:00+03:00', None, ['90213']),
        (None, None, ['87840', '90213']),
    ],
)
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_dates_optional_date_in_db(
        taxi_overlord_catalog,
        search,
        fail_from,
        fail_to,
        expected_depot_ids,
        mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    json = {
        'search': search,
        'order_by': 'errors_count_in_row',
        'order_direction': 'asc',
    }
    if fail_from is not None:
        json['last_fail_date_from'] = fail_from

    if fail_to is not None:
        json['last_fail_date_to'] = fail_to

    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list', json=json,
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == len(expected_depot_ids)
    for i, depot_response in enumerate(response.json()['payload']):
        expected_slug = slug_by_depot_id(expected_depot_ids[i])
        assert depot_response == get_response_by_slug(expected_slug)


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_empty_search(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list',
        json={'order_by': 'errors_count_in_row', 'order_direction': 'asc'},
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == 2
    assert response.json()['payload'][0] == get_response_by_slug(
        slug_by_depot_id('87840'),
    )
    assert response.json()['payload'][1] == get_response_by_slug(
        slug_by_depot_id('90213'),
    )


@pytest.mark.parametrize(
    'sources, expected_depot_ids',
    [
        (['nomenclatures', 'stocks'], ['87840', '90213']),
        (['nomenclatures'], ['90213']),
        (['stocks'], ['87840']),
        (None, ['87840', '90213']),
        (['eats_id_mappings'], []),
        (['polygons'], []),
    ],
)
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_select_by_sources(
        taxi_overlord_catalog,
        sources,
        expected_depot_ids,
        mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    json = {'order_by': 'errors_count_in_row', 'order_direction': 'asc'}
    if sources is not None:
        json['source_types'] = sources

    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list', json=json,
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == len(expected_depot_ids)
    for i, depot_response in enumerate(response.json()['payload']):
        expected_slug = slug_by_depot_id(expected_depot_ids[i])
        assert depot_response == get_response_by_slug(expected_slug)


@pytest.mark.pgsql(
    'overlord_catalog',
    files=['1c_menu_data.sql', '1c_stocks.sql', 'import_stats.sql'],
)
async def test_wrong_dates_input(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
    )
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/import-stats/list',
        json={
            'order_by': 'errors_count_in_row',
            'order_direction': 'asc',
            'last_success_date_from': '2020-12-10T00:30:00+03:00',
            'last_success_date_to': '2020-04-10T00:30:00+03:00',
        },
    )

    assert response.status_code == 400
