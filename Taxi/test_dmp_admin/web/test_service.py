import pytest


@pytest.fixture
def taxi_dmp_admin_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_dmp_admin_mocks')
async def test_ping(taxi_dmp_admin_web):
    response = await taxi_dmp_admin_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''


async def test_get_v1_services(web_app_client):
    response = await web_app_client.get('/v1/services')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'services': [
            {
                'description': 'Сервис taxi_etl',
                'name': 'taxi_etl',
                'responsible': ['@itsme', '@vverstov', '@amleletko'],
            },
            {
                'description': 'Сервис eda_etl',
                'name': 'eda_etl',
                'responsible': ['@itsme', '@vverstov', '@amleletko'],
            },
            {
                'description': 'Сервис demand_etl',
                'name': 'demand_etl',
                'responsible': ['@igsaf', '@avkoroleva'],
            },
        ],
    }


async def test_get_v1_entity_types(web_app_client):
    response = await web_app_client.get('/v1/entity_types')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'types': [
            {'description': 'YT', 'name': 'YT'},
            {'description': 'Greenplum', 'name': 'GP'},
        ],
    }


async def test_get_v1_entities(web_app_client):
    response = await web_app_client.get('/v1/entities')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'entities': [
            {
                'ctl': [
                    {
                        'name': 'CTL_LAST_SYNC_DATE',
                        'value': '2022-06-01T12:20:25Z',
                    },
                    {
                        'name': 'CTL_LAST_LOAD_DATE',
                        'value': '2022-06-01T12:12:48Z',
                    },
                ],
                'description': (
                    'Таблица, содержащая заказы пользователей. '
                    'Источник MySql Bigfood.'
                ),
                'doc_link': (
                    'https://doc.yandex-team.ru/taxi/dmp/objects/Eda_new'
                    '/yt/ods/bigfood/order.html'
                ),
                'id': '3d4338c8-870e-4906-9df0-f3f2638275b7',
                'name': 'bigfood.order',
                'service_name': 'eda_etl',
                'type': 'YT',
                'view_link': (
                    'https://yt.yandex-team.ru/hahn/navigation?path='
                    '//home/taxi-dwh-dev/itsme/unexpected_arg_changes'
                ),
            },
        ],
    }


async def test_get_v1_entity(web_app_client):
    response = await web_app_client.get(
        '/v1/entities/3d4338c8-870e-4906-9df0-f3f2638275b7',
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'ctl': [
            {'name': 'CTL_LAST_SYNC_DATE', 'value': '2022-06-01T12:20:25Z'},
            {'name': 'CTL_LAST_LOAD_DATE', 'value': '2022-06-01T12:12:48Z'},
        ],
        'description': (
            'Таблица, содержащая заказы пользователей. '
            'Источник MySql Bigfood.'
        ),
        'doc_link': (
            'https://doc.yandex-team.ru/taxi/dmp/objects/Eda_new'
            '/yt/ods/bigfood/order.html'
        ),
        'id': '3d4338c8-870e-4906-9df0-f3f2638275b7',
        'name': 'bigfood.order',
        'service_name': 'eda_etl',
        'type': 'YT',
        'view_link': (
            'https://yt.yandex-team.ru/hahn/navigation?path='
            '//home/taxi-dwh-dev/itsme/unexpected_arg_changes'
        ),
    }


async def test_get_v1_tasks(web_app_client):
    response = await web_app_client.get('/v1/tasks')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'tasks': [
            {
                'arguments': ['--as-backfill', '--no-lock'],
                'description': 'Стриминговый таск загрузки данных (1)',
                'id': '7f22b2b4-140a-4783-b54e-182084de763b',
                'name': 'ods_eda_bigfood_order_replication_streaming',
                'path': 'eda_etl/layer/yt/ods/bigfood/order/loader.py',
                'scheduler': {'schedule': '* * * * *', 'type': 'cron'},
                'service_name': 'eda_etl',
                'sources': [],
                'targets': ['3d4338c8-870e-4906-9df0-f3f2638275b7'],
            },
        ],
    }


async def test_get_v1_task(web_app_client):
    response = await web_app_client.get(
        '/v1/tasks/7f22b2b4-140a-4783-b54e-182084de763b',
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'arguments': ['--as-backfill', '--no-lock'],
        'description': 'Стриминговый таск загрузки данных',
        'id': '7f22b2b4-140a-4783-b54e-182084de763b',
        'name': 'ods_eda_bigfood_order_replication_streaming',
        'path': 'eda_etl/layer/yt/ods/bigfood/order/loader.py',
        'scheduler': {'schedule': '* * * * *', 'type': 'cron'},
        'service_name': 'eda_etl',
        'sources': [],
        'targets': ['3d4338c8-870e-4906-9df0-f3f2638275b7'],
    }


async def test_post_v1_get_last_runs(web_app_client):
    response = await web_app_client.post(
        '/v1/tasks/get_last_runs',
        params={'limit': 5},
        json={'task_ids': ['7f22b2b4-140a-4783-b54e-182084de763b']},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'last_runs': [
            {
                'task_id': '7f22b2b4-140a-4783-b54e-182084de763b',
                'task_runs': [
                    {
                        'arguments': (
                            '{"start_date": "2022-06-01 '
                            '00:00:00", "end_date": '
                            '"2022-06-02 23:59:59"}'
                        ),
                        'end_dttm': '2022-06-03T03:25:12Z',
                        'id': '73057005-e874-41fb-8799-7f6728a90f6e',
                        'logs_link': (
                            'https://kibana.taxi.yandex-team.ru/goto'
                            '/a9b93afaa4021b530e0547a98b5b89c0'
                        ),
                        'start_dttm': '2022-06-03T03:05:02Z',
                        'status': 'success',
                    },
                ],
            },
            {
                'task_id': '7f22b2b4-140a-4783-b54e-182084de763b',
                'task_runs': [
                    {
                        'arguments': (
                            '{"start_date": "2022-06-02 '
                            '00:00:00", "end_date": '
                            '"2022-06-03 23:59:59"}'
                        ),
                        'end_dttm': '2022-06-04T03:05:12Z',
                        'id': 'd1ecec9f-8e8b-4d92-abb4-bf4af7891caf',
                        'logs_link': (
                            'https://kibana.taxi.yandex-team.ru/goto'
                            '/a9b93afaa4021b530e0547a98b5b89c0'
                        ),
                        'start_dttm': '2022-06-04T03:05:07Z',
                        'status': 'error',
                    },
                ],
            },
            {
                'task_id': '7f22b2b4-140a-4783-b54e-182084de763b',
                'task_runs': [
                    {
                        'arguments': (
                            '{"start_date": "2022-06-02 '
                            '00:00:00", "end_date": '
                            '"2022-06-03 23:59:59"}'
                        ),
                        'id': '8a5157d7-04bb-40df-925c-050fa220929b',
                        'logs_link': (
                            'https://kibana.taxi.yandex-team.ru/goto'
                            '/a9b93afaa4021b530e0547a98b5b89c0'
                        ),
                        'start_dttm': '2022-06-03T03:05:15Z',
                        'status': 'running',
                    },
                ],
            },
        ],
        'not_found_tasks': [],
    }
