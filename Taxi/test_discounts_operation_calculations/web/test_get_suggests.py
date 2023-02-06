import pytest


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_suggests.sql'],
)
async def test_get_suggests(web_app_client):
    params = {'cities': 'Москва,Нижний Тагил', 'status': 'NEED_APPROVAL'}

    response = await web_app_client.get('/v1/suggests', params=params)

    assert response.status == 200
    content = await response.json()

    assert content['total'] == 1
    assert len(content['rows']) == 1
    assert content['rows'][0] == {
        'id': 1,
        'city': 'Москва',
        'status': 'NEED_APPROVAL',
        'created_at': '2020-08-11T02:43:21+03:00',
        'updated_at': '2020-08-11T02:53:21+03:00',
        'algorithms': ['kt1'],
        'author': 'eugenest',
        'multidraft': 'https://ya.ru/123',
        'budget': 100500,
    }


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_suggests.sql'],
)
async def test_get_suggests_all(web_app_client):
    params = {}
    response = await web_app_client.get('/v1/suggests', params=params)

    assert response.status == 200
    content = await response.json()

    assert content['total'] == 5
    assert len(content['rows']) == 5

    # NOT_PUBLISHED status is ignored
    statuses = [suggest['status'] for suggest in content['rows']]
    assert 'NOT_PUBLISHED' not in statuses


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_suggests.sql'],
)
async def test_get_suggests_limit_offset(web_app_client):
    params = {'limit': 2, 'offset': 1}
    response = await web_app_client.get('/v1/suggests', params=params)

    assert response.status == 200
    content = await response.json()

    assert content['total'] == 5
    assert len(content['rows']) == 2

    assert sorted(content['rows'], key=lambda x: x['id'])[1] == {
        'algorithms': ['kt1', 'kt2'],
        'author': 'shedx',
        'city': 'Санкт-Петербург',
        'created_at': '2020-08-09T21:21:04+03:00',
        'id': 2,
        'multidraft': 'https://ya.ru/15',
        'status': 'REJECTED',
        'updated_at': '2020-08-10T13:14:04+03:00',
        'budget': 1000,
    }


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_pushes_texts.sql'],
)
async def test_get_suggests_date_range(web_app_client):
    params = {'date_from': 1644756811, 'date_to': 1645014000}
    response = await web_app_client.get('/v1/suggests', params=params)

    assert response.status == 200
    content = await response.json()

    assert len(content['rows']) == 1

    assert content['rows'][0] == {
        'algorithms': ['test_algo_3'],
        'author': 'eugenest',
        'city': 'Абиджан',
        'created_at': '2022-01-28T15:23:05+03:00',
        'id': 1,
        'multidraft': 'https://ya.ru/1',
        'status': 'NEED_APPROVAL',
        'updated_at': '2022-01-28T15:24:36+03:00',
        'budget': 345675.0,
        'date_from': '2022-01-28T15:53:31+03:00',
        'date_to': '2022-02-16T15:23:16+03:00',
    }


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_pushes_texts.sql'],
)
async def test_get_suggests_author(web_app_client):
    params = {'authors': 'raifox,shedx'}
    response = await web_app_client.get('/v1/suggests', params=params)

    assert response.status == 200
    content = await response.json()

    assert len(content['rows']) == 1

    assert content['rows'][0] == {
        'algorithms': ['test_algo_1'],
        'author': 'raifox',
        'city': 'Саратов',
        'created_at': '2022-01-28T14:42:36+03:00',
        'id': 4,
        'multidraft': 'https://ya.ru/4',
        'status': 'NEED_APPROVAL',
        'updated_at': '2022-01-28T15:23:30+03:00',
        'budget': 1234124.0,
        'date_from': '2022-01-28T15:12:58+03:00',
        'date_to': '2022-02-11T14:42:48+03:00',
    }


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_pushes_texts.sql'],
)
async def test_get_suggests_tariff_zones(web_app_client):
    params = {'tariff_zones': 'saratov,penza'}
    response = await web_app_client.get('/v1/suggests', params=params)

    assert response.status == 200
    content = await response.json()

    assert len(content['rows']) == 1

    assert content['rows'][0] == {
        'algorithms': ['test_algo_1'],
        'author': 'raifox',
        'city': 'Саратов',
        'created_at': '2022-01-28T14:42:36+03:00',
        'id': 4,
        'multidraft': 'https://ya.ru/4',
        'status': 'NEED_APPROVAL',
        'updated_at': '2022-01-28T15:23:30+03:00',
        'budget': 1234124.0,
        'date_from': '2022-01-28T15:12:58+03:00',
        'date_to': '2022-02-11T14:42:48+03:00',
    }


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests_to_pushes_texts.sql'],
)
async def test_get_suggests_cities(web_app_client):
    params = {'cities': 'Саратов,Тестовый город'}
    response = await web_app_client.get('/v1/suggests', params=params)

    assert response.status == 200
    content = await response.json()

    assert len(content['rows']) == 2

    assert sorted(content['rows'], key=lambda x: x['id']) == [
        {
            'algorithms': ['test_algo_2', 'test_algo_3'],
            'author': 'eugenest',
            'city': 'Тестовый город',
            'created_at': '2022-01-28T14:42:36+03:00',
            'id': 3,
            'multidraft': 'https://ya.ru/2',
            'status': 'NEED_APPROVAL',
            'updated_at': '2022-01-28T15:23:30+03:00',
            'budget': 1234124.0,
            'date_from': '2022-01-28T15:12:58+03:00',
            'date_to': '2022-02-11T14:42:48+03:00',
        },
        {
            'algorithms': ['test_algo_1'],
            'author': 'raifox',
            'city': 'Саратов',
            'created_at': '2022-01-28T14:42:36+03:00',
            'id': 4,
            'multidraft': 'https://ya.ru/4',
            'status': 'NEED_APPROVAL',
            'updated_at': '2022-01-28T15:23:30+03:00',
            'budget': 1234124.0,
            'date_from': '2022-01-28T15:12:58+03:00',
            'date_to': '2022-02-11T14:42:48+03:00',
        },
    ]
