import pytest


@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
@pytest.mark.config(
    STRONGBOX_TVM_ACCESS={'services': {}, 'enable_in_suggest': True},
)
@pytest.mark.parametrize(
    'text, expected_json',
    [
        ('searchable', 'test_secrets_suggest_expected.json'),
        ('tvm_access', 'test_secrets_suggest_with_tvm_access_expected.json'),
    ],
)
async def test_secrets_suggest(web_app_client, load_json, text, expected_json):
    response = await web_app_client.get(
        '/v1/secrets/suggest/', params={'text': text},
    )
    data = await response.json()
    assert response.status == 200, data
    expected = load_json(expected_json)
    assert expected == data


@pytest.mark.parametrize(
    'params,expected,login',
    [
        (
            {'show_authorized_secrets': 'True', 'project_name': 'taxi'},
            [
                {
                    'environments': ['testing', 'unstable'],
                    'key': 'SEARCHABLE_SECRET',
                },
            ],
            'some-mate',
        ),
        (
            {'secret_key': 'SEARCHABLE_SECRET', 'env': 'testing'},
            [{'environments': ['testing'], 'key': 'SEARCHABLE_SECRET'}],
            'some-mate',
        ),
        (
            {'show_authorized_secrets': 'False', 'project_name': 'axi'},
            [],
            'unexpected',
        ),
        (
            {'show_authorized_secrets': 'true'},
            [
                {'key': 'MONGODB_TAXI_STRONGBOX', 'environments': ['testing']},
                {
                    'environments': ['testing', 'unstable'],
                    'key': 'SEARCHABLE_SECRET',
                },
                {'environments': ['testing'], 'key': 'SEARCH_ABLE_SECRET_2'},
                {
                    'environments': ['testing'],
                    'key': 'POSTGRES_TAXI_STRONGBOX',
                },
            ],
            'some-mate-2',
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_secrets_suggest_service_filtration(
        web_app_client, params, expected, login,
):
    response = await web_app_client.get(
        '/v1/secrets/suggest/',
        params=params,
        headers={'X-Yandex-Login': login},
    )
    data = await response.json()
    assert response.status == 200, data
    data = [
        {'key': item['key'], 'environments': item['environments']}
        for item in data
    ]
    assert data == expected


@pytest.mark.parametrize(
    'params,expected_count',
    [
        ({}, 7),
        ({'limit': 0}, 7),
        ({'limit': 2}, 2),
        ({'offset': 2}, 5),
        ({'limit': 2, 'offset': 2}, 2),
        ({'offset': 10}, 0),
        ({'limit': 100, 'offset': 1}, 6),
        ({'text': 'TEST', 'limit': 1}, 1),
        ({'text': 'TEST', 'offset': 1}, 1),
        ({'text': 'TEST'}, 2),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_secrets_suggest_pagination(
        web_app_client, params, expected_count,
):
    response = await web_app_client.get('/v1/secrets/suggest/', params=params)
    assert response.status == 200
    data = await response.json()
    assert len(data) == expected_count


@pytest.mark.parametrize(
    'params,expected_count',
    [
        ({}, 7),
        ({'types': 'mongodb'}, 3),
        ({'types': 'redis'}, 1),
        ({'types': 'redis,postgresql'}, 3),
        ({'types': 'postgresql,redis'}, 3),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_secrets_suggest_by_types(
        web_app_client, params, expected_count,
):
    response = await web_app_client.get('/v1/secrets/suggest/', params=params)
    data = await response.json()
    assert response.status == 200, data
    assert len(data) == expected_count


async def test_secrets_types(web_app_client, load_json):
    response = await web_app_client.get('/v1/secrets/types/')
    assert response.status == 200
    data = await response.json()
    expected_response = load_json('expected_response.json')
    assert data == expected_response
