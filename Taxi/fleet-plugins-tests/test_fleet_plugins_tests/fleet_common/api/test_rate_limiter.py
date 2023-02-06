import pytest

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'tarasalk',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
    'X-Real-IP': '127.0.0.1',
}


@pytest.mark.config(
    OPTEUM_RATE_LIMITER_PYTHON_EXTENDED={
        'enable': True,
        'services': [
            {'enable': True, 'name': 'fleet_plugins_tests', 'rpm': 2},
        ],
        'users': {'enable': False},
        'parks': {'enable': False},
    },
)
async def test_services(web_app_client):

    for i in range(4):
        response = await web_app_client.post(
            '/fleet_rate_limiter/one', headers=HEADERS,
        )

        if i < 2:
            assert response.status == 200
        else:
            assert response.status == 429


@pytest.mark.config(
    OPTEUM_RATE_LIMITER_PYTHON_EXTENDED={
        'enable': True,
        'services': [
            {
                'enable': True,
                'name': 'fleet_plugins_tests',
                'urls': [
                    {'url': '/fleet_rate_limiter/one_POST', 'rpm': 2},
                    {'url': '/fleet_rate_limiter/two_POST', 'rpm': 2},
                ],
            },
        ],
        'users': {'enable': False},
        'parks': {'enable': False},
    },
)
async def test_urls(web_app_client):

    for i in range(4):
        response = await web_app_client.post(
            '/fleet_rate_limiter/one', headers=HEADERS,
        )

        if i < 2:
            assert response.status == 200
        else:
            assert response.status == 429

    response = await web_app_client.post(
        '/fleet_rate_limiter/two', headers=HEADERS,
    )

    assert response.status == 200


@pytest.mark.config(
    OPTEUM_RATE_LIMITER_PYTHON_EXTENDED={
        'enable': True,
        'services': [],
        'users': {
            'enable': True,
            'rpm': 2,
            'logins': [{'login': 'test_login', 'rpm': 1}],
        },
        'parks': {'enable': False},
    },
)
async def test_users(web_app_client):
    for i in range(3):
        response = await web_app_client.post(
            '/fleet_rate_limiter/one', headers=HEADERS,
        )

        if i < 2:
            assert response.status == 200
        else:
            assert response.status == 429


@pytest.mark.config(
    OPTEUM_RATE_LIMITER_PYTHON_EXTENDED={
        'enable': True,
        'services': [],
        'users': {
            'enable': True,
            'rpm': 4,
            'logins': [{'login': 'test_login', 'rpm': 2}],
        },
        'parks': {'enable': False},
    },
)
async def test_user_login(web_app_client):
    HEADERS['X-Yandex-Login'] = 'test_login'

    for i in range(3):
        response = await web_app_client.post(
            '/fleet_rate_limiter/one', headers=HEADERS,
        )

        if i < 2:
            assert response.status == 200
        else:
            assert response.status == 429

    # Для других работает
    HEADERS['X-Yandex-UID'] = '234'
    HEADERS['X-Yandex-Login'] = 'tarasalk'

    response = await web_app_client.post(
        '/fleet_rate_limiter/one', headers=HEADERS,
    )

    assert response.status == 200


@pytest.mark.config(
    OPTEUM_RATE_LIMITER_PYTHON_EXTENDED={
        'enable': True,
        'services': [],
        'users': {'enable': False},
        'parks': {
            'enable': True,
            'rpm': 2,
            'park_ids': [{'id': '1111', 'rpm': 1}],
        },
    },
)
async def test_parks(web_app_client):
    for i in range(3):
        response = await web_app_client.post(
            '/fleet_rate_limiter/one', headers=HEADERS,
        )

        if i < 2:
            assert response.status == 200
        else:
            assert response.status == 429


@pytest.mark.config(
    OPTEUM_RATE_LIMITER_PYTHON_EXTENDED={
        'enable': True,
        'services': [],
        'users': {'enable': False},
        'parks': {
            'enable': True,
            'rpm': 4,
            'park_ids': [{'id': '1111', 'rpm': 2}],
        },
    },
)
async def test_park_id(web_app_client):
    HEADERS['X-Park-Id'] = '1111'

    for i in range(3):
        response = await web_app_client.post(
            '/fleet_rate_limiter/one', headers=HEADERS,
        )

        if i < 2:
            assert response.status == 200
        else:
            assert response.status == 429

    # Для других работает
    HEADERS['X-Park-Id'] = '2222'

    response = await web_app_client.post(
        '/fleet_rate_limiter/one', headers=HEADERS,
    )

    assert response.status == 200
