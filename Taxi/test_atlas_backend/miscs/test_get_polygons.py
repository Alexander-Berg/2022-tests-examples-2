import pytest


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
@pytest.mark.parametrize(
    'key,value',
    [
        pytest.param('city', 'Москва'),
        pytest.param(
            'geonodes', [{'name': 'br_moscow', 'type': 'agglomeration'}],
        ),
    ],
)
async def test_get_polygons(web_app_client, key, value):
    request_json = {'user': 'moscow_user', key: value}
    response = await web_app_client.post('/api/polygons', json=request_json)
    assert response.status == 200

    content = sorted(await response.json(), key=lambda x: x['name'])
    assert len(content) == 3

    assert content[2] == {
        '_id': '5e9efcfae280e46e8ae00a09',
        'city': ['Москва', 'Казань', 'Владивосток'],
        'name': 'many_cities',
        'polygons': [
            [
                [55.75072421501753, 37.51739013671875],
                [55.780532192800166, 37.61214721679688],
                [55.71469185069788, 37.62038696289061],
                [55.75072421501753, 37.51739013671875],
            ],
        ],
        'quadkeys': [
            '120310101033213210',
            '120310101033213212',
            '120310101033213211',
            '120310101033213213',
            '120310101033213231',
            '120310101033213122',
            '120310101033213300',
            '120310101033213302',
            '120310101033213320',
            '120310101033213121',
            '120310101033213123',
            '120310101033213301',
            '120310101033213303',
            '120310101033213321',
            '120310101033213323',
            '120310101033213130',
            '120310101033213132',
            '120310101033213310',
            '120310101033213312',
            '120310101033213330',
            '120310101033213332',
            '120310101033213331',
            '120310101033213333',
        ],
        'user': '__default__',
        'tariff_zones': ['moscow', 'kazan', 'vladivostok'],
    }


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
@pytest.mark.parametrize(
    'key,value',
    [
        pytest.param('city', 'Москва'),
        pytest.param(
            'geonodes', [{'name': 'br_moscow', 'type': 'agglomeration'}],
        ),
    ],
)
async def test_get_polygons_other_user(web_app_client, key, value):
    request_json = {'user': 'asdf_user', key: value}
    response = await web_app_client.post('/api/polygons', json=request_json)
    assert response.status == 200

    content = await response.json()

    assert len(content) == 2
    assert content[0]['user'] == content[1]['user'] == '__default__'


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
@pytest.mark.parametrize(
    'key,value',
    [
        pytest.param('city', 'Арск'),
        pytest.param(
            'geonodes', [{'name': 'br_arsk', 'type': 'agglomeration'}],
        ),
    ],
)
async def test_get_polygons_empty_city(web_app_client, key, value):
    request_json = {'user': 'moscow_user', key: value}
    response = await web_app_client.post('/api/polygons', json=request_json)
    assert response.status == 200

    content = await response.json()

    assert content == []


@pytest.mark.parametrize(
    'user,expected_len,expected_result',
    [
        pytest.param(
            'moscow_user',
            3,
            {
                '_id': '5e9efcfae280e46e8ae00a09',
                'city': ['Москва', 'Казань', 'Владивосток'],
                'name': 'many_cities',
                'polygons': [
                    [
                        [55.75072421501753, 37.51739013671875],
                        [55.780532192800166, 37.61214721679688],
                        [55.71469185069788, 37.62038696289061],
                        [55.75072421501753, 37.51739013671875],
                    ],
                ],
                'quadkeys': [
                    '120310101033213210',
                    '120310101033213212',
                    '120310101033213211',
                    '120310101033213213',
                    '120310101033213231',
                    '120310101033213122',
                    '120310101033213300',
                    '120310101033213302',
                    '120310101033213320',
                    '120310101033213121',
                    '120310101033213123',
                    '120310101033213301',
                    '120310101033213303',
                    '120310101033213321',
                    '120310101033213323',
                    '120310101033213130',
                    '120310101033213132',
                    '120310101033213310',
                    '120310101033213312',
                    '120310101033213330',
                    '120310101033213332',
                    '120310101033213331',
                    '120310101033213333',
                ],
                'tariff_zones': ['moscow', 'kazan', 'vladivostok'],
                'user': '__default__',
            },
        ),
        pytest.param(
            'kazan_user',
            3,
            {
                '_id': '5e9efcfae280e46e8ae00a09',
                'city': ['Москва', 'Казань', 'Владивосток'],
                'name': 'many_cities',
                'polygons': [
                    [
                        [55.75072421501753, 37.51739013671875],
                        [55.780532192800166, 37.61214721679688],
                        [55.71469185069788, 37.62038696289061],
                        [55.75072421501753, 37.51739013671875],
                    ],
                ],
                'quadkeys': [
                    '120310101033213210',
                    '120310101033213212',
                    '120310101033213211',
                    '120310101033213213',
                    '120310101033213231',
                    '120310101033213122',
                    '120310101033213300',
                    '120310101033213302',
                    '120310101033213320',
                    '120310101033213121',
                    '120310101033213123',
                    '120310101033213301',
                    '120310101033213303',
                    '120310101033213321',
                    '120310101033213323',
                    '120310101033213130',
                    '120310101033213132',
                    '120310101033213310',
                    '120310101033213312',
                    '120310101033213330',
                    '120310101033213332',
                    '120310101033213331',
                    '120310101033213333',
                ],
                'tariff_zones': ['moscow', 'kazan', 'vladivostok'],
                'user': '__default__',
            },
        ),
    ],
)
async def test_get_polygons_all_cities(
        web_app_client, user, expected_len, expected_result,
):
    request_json = {'user': user, 'city': []}
    response = await web_app_client.post('/api/polygons', json=request_json)
    assert response.status == 200

    content = await response.json()

    assert len(content) == expected_len
    assert content[-1] == expected_result
