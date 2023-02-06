import pytest


YT_SCHEMA = 'yt_schema.yaml'

YT_PLACES_DATA = 'yt_places_data.yaml'
YT_BRANDS_DATA = 'yt_brands_data.yaml'
YT_CATEGORIES_DATA = 'yt_categories_data.yaml'
YT_ITEMS_DATA = 'yt_items_data.yaml'
YT_TMP_DATA = 'yt_tmp_data.yaml'
YT_TMP_DATA_EMPTY = 'yt_tmp_data_empty.yaml'


PERIODIC_CONFIG = {
    'enable': True,
    'interval': 3600,
    'enable_check_interval': 60,
    'yql_operation_check_period': 1,
    'yql_operation_check_max_attempts': 3,
    'start_date': '2015-01-01T00:00:00+03:00',
    'yt_cluster': 'hahn',
    'yt_places_path': '//yt/places',
    'yt_brands_path': '//yt/brands',
    'yt_categories_path': '//yt/categories',
    'yt_menu_items_path': '//yt/menu-items',
    'yt_tmp_path': '//yt/tmp',
    'yt_batch_size': 1000,
}

PERIODIC_NAME = 'restaurant-menu-periodic'

MENU_PERIODIC_FINISHED = (
    'eats_full_text_search_indexer::restaurant-menu-periodic-finished'
)
MENU_LOG_ITEM = 'fts-indexer-log-menu-item'
MENU_DELETE_ITEM = 'fts-indexer-delete-menu-item'

EXPECTED_YQL_REQUEST = 'expected_yql_request.json'
EXPECTED_ITEMS = 'expected_items.json'


def get_last_updated_at(pgsql):
    cursor = pgsql['eats_full_text_search_indexer'].dict_cursor()
    cursor.execute(
        """
        SELECT
            updated_at
        FROM
            fts_indexer.restaurant_menu_state
        WHERE id = 1;
    """,
    )
    rows = [dict(row) for row in cursor]
    if rows:
        return rows[0]['updated_at']
    return None


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_INDEXER_RESTAURANT_MENU_PERIODIC=PERIODIC_CONFIG,
)
@pytest.mark.parametrize(
    'yql_status,expected_status_requests',
    (
        pytest.param('COMPLETED', 1, id='completed'),
        pytest.param('PENDING', 3, id='pending with max retries'),
        pytest.param('ERROR', 1, id='error'),
        pytest.param('UNKNOWN', 1, id='unknown'),
    ),
)
@pytest.mark.yt(schemas=[YT_SCHEMA], static_table_data=[YT_TMP_DATA_EMPTY])
async def test_periodic_yql_max_attempts(
        taxi_eats_full_text_search_indexer,
        taxi_config,
        mockserver,
        yt_apply,
        testpoint,
        mock_yql,
        yql_status,
        expected_status_requests,
):
    """
    Тест проверяет что сервис обращается делает запрос к yql
    для индексации блюд маркетом и делает ровно заданное в конфигурации
    количество попыток, либо прекращает при ошибке
    """

    operation_id = '1234'

    @mockserver.json_handler('/yql/api/v2/operations/' + operation_id)
    def mock_yql_status(req):
        return mockserver.make_response(
            status=200,
            json={
                'id': operation_id,
                'createdAt': '2021-02-02T00:00:00.060326Z',
                'updatedAt': '2021-02-02T00:00:00.132560Z',
                'username': 'testsuite',
                'status': yql_status,
            },
        )

    @testpoint(MENU_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_full_text_search_indexer.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    assert mock_yql.times_called == 1
    assert mock_yql_status.times_called == expected_status_requests


@pytest.mark.parametrize(
    'expected_updated_at', [pytest.param('None', id='none')],
)
@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_INDEXER_RESTAURANT_MENU_PERIODIC=PERIODIC_CONFIG,
)
@pytest.mark.yt(schemas=[YT_SCHEMA], static_table_data=[YT_TMP_DATA_EMPTY])
async def test_periodic_updated_at(
        taxi_eats_full_text_search_indexer,
        mockserver,
        yt_apply,
        testpoint,
        pgsql,
        mock_yql,
        expected_updated_at,
):
    """
    Тест проверяет что restaurant-menu-periodic правильно записывает
    updated_at в базу и не записывает, если не было успешно
    обработанных записей
    """

    operation_id = '1234'

    @mockserver.json_handler('/yql/api/v2/operations/' + operation_id)
    def mock_yql_status(req):
        return mockserver.make_response(
            status=200,
            json={
                'id': operation_id,
                'createdAt': '2021-02-02T00:00:00.060326Z',
                'updatedAt': '2021-02-02T00:00:00.132560Z',
                'username': 'testsuite',
                'status': 'COMPLETED',
            },
        )

    @testpoint(MENU_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_full_text_search_indexer.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    assert mock_yql.times_called == 1
    assert mock_yql_status.times_called == 1

    updated_at = get_last_updated_at(pgsql)
    assert str(updated_at) == expected_updated_at


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.yt(schemas=[YT_SCHEMA], static_table_data=[YT_TMP_DATA_EMPTY])
async def test_periodic_date_time_and_lag(
        taxi_eats_full_text_search_indexer,
        mockserver,
        yt_apply,
        testpoint,
        taxi_config,
):
    """
    Тест проверяет что restaurant-menu-periodic передает в YQL дату и время
    в правильном формате, а так же, использует lag из конфига
    """

    config = PERIODIC_CONFIG
    config['lag'] = 3600
    taxi_config.set(
        EATS_FULL_TEXT_SEARCH_INDEXER_RESTAURANT_MENU_PERIODIC=config,
    )

    operation_id = '1234'

    @mockserver.json_handler('/yql/api/v2/operations')
    def mock_yql_operations(req):
        assert req.json['action'] == 'RUN'
        assert 'content' in req.json

        # проверяем что в запрос попала дата в нужном формате (UTC)
        # со сдвигом на lag
        assert (
            'i.utc_updated_dttm >= \'2014-12-31 20:00:00\''
            in req.json['content']
        )
        assert (
            'i.utc_updated_dttm < \'2021-01-01 08:00:00\''
            in req.json['content']
        )
        return mockserver.make_response(
            status=200,
            json={
                'createdAt': '2021-02-02T00:00:00.060326Z',
                'execMode': 'RUN',
                'externalQueryIds': [],
                'id': operation_id,
                'projectId': '5f97ce6768a6f5c079a61aa3',
                'queryData': {
                    'attributes': {'user_agent': ''},
                    'clusterType': 'UNKNOWN',
                    'content': '',
                    'files': [],
                    'parameters': {},
                    'type': 'SQLv1',
                },
                'queryType': 'SQLv1',
                'status': 'PENDING',
                'title': '',
                'updatedAt': '2021-02-02T00:00:00.132560Z',
                'username': 'testsuite',
                'version': 0,
                'workerId': '6974305d-f18339ad-174b72f9-376d5dea',
            },
        )

    @mockserver.json_handler('/yql/api/v2/operations/' + operation_id)
    def mock_yql_status(req):
        return mockserver.make_response(
            status=200,
            json={
                'id': operation_id,
                'createdAt': '2021-02-02T00:00:00.060326Z',
                'updatedAt': '2021-02-02T00:00:00.132560Z',
                'username': 'testsuite',
                'status': 'COMPLETED',
            },
        )

    @testpoint(MENU_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_full_text_search_indexer.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    assert mock_yql_operations.times_called == 1
    assert mock_yql_status.times_called == 1


SERVICE = 'eats_fts'
PREFIX = 3
MENU_SAAS_PUSH_ITEM = 'fts-indexer-saas-push-menu-item'
MENU_SAAS_DELETE_ITEM = 'fts-indexer-saas-delete-menu-item'


@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['fill_place_states.sql'],
)
@pytest.mark.yt(schemas=[YT_SCHEMA], static_table_data=[YT_TMP_DATA])
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_INDEXER_RESTAURANT_MENU_PERIODIC=PERIODIC_CONFIG,
    EATS_FULL_TEXT_SEARCH_INDEXER_RESTAURANT_MENU_UPDATE={
        'saas_settings': {
            'service_alias': SERVICE,
            'prefix': PREFIX,
            'place_document_batch_size': 1,
        },
        'enable': True,
    },
)
async def test_periodic_log_items_saas(
        taxi_eats_full_text_search_indexer,
        mockserver,
        yt_apply,
        testpoint,
        load_json,
        mock_yql,
):
    """
    Тест проверяет что сервис делает YQL запрос в YT и выполняет
    индексацию в SaaS
    """

    operation_id = '1234'

    @mockserver.json_handler('/yql/api/v2/operations/' + operation_id)
    def mock_yql_status(req):
        return mockserver.make_response(
            status=200,
            json={
                'id': operation_id,
                'createdAt': '2021-02-02T00:00:00.060326Z',
                'updatedAt': '2021-02-02T00:00:00.132560Z',
                'username': 'testsuite',
                'status': 'COMPLETED',
            },
        )

    @testpoint(MENU_PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    @testpoint(MENU_SAAS_PUSH_ITEM)
    def menu_saas_push_item(arg):
        pass

    @testpoint(MENU_SAAS_DELETE_ITEM)
    def menu_saas_delete_item(arg):
        pass

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SERVICE),
    )
    def saas_push(request):
        data = request.json
        assert data['prefix'] == 3
        doc = data['docs'][0]
        if data['action'] == 'delete':
            assert doc['url'] == '/my_place_slug/items/4'
        else:
            assert doc['i_type']['value'] == 3
            assert doc['i_core_item_id']['value'] in (1, 2, 3)
        return {
            'written': True,
            'attempts': [
                {
                    'comment': 'ok',
                    'written': True,
                    'attempt': 0,
                    'shard': '0-65535',
                },
            ],
            'comment': 'ok',
        }

    # run menu items indexer
    await taxi_eats_full_text_search_indexer.run_distlock_task(PERIODIC_NAME)

    # wait for every item logging
    expected_items_data = load_json(EXPECTED_ITEMS)

    expected_items = expected_items_data['items']
    for item in expected_items:
        result = await menu_saas_push_item.wait_call()
        url = '/my_place_slug/items/' + str(item['data']['id'])
        assert result['arg']['url'] == url
        assert result['arg']['is_delete'] is False

    expected_deleted_items = expected_items_data['deleted_items']
    for item in expected_deleted_items:
        result = await menu_saas_delete_item.wait_call()
        url = '/my_place_slug/items/' + str(item['data']['id'])
        assert result['arg']['url'] == url
        assert result['arg']['is_delete'] is True

    # wait for periodic finished
    periodic_finished.next_call()

    assert mock_yql.times_called == 1
    assert mock_yql_status.times_called == 1
    assert saas_push.times_called == 4
