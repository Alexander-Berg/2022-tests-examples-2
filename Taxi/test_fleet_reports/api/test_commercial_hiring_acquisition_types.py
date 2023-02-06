import pytest

TRANSLATIONS = {'app': {'ru': 'Приложение'}, 'partner': {'ru': 'Партнеры'}}


@pytest.mark.translations(fleet_enums=TRANSLATIONS)
@pytest.mark.config(
    FLEET_REPORTS_COMMERCIAL_HIRING_TYPES=[
        {'type_code': 'partner'},
        {'type_code': 'app'},
    ],
)
async def test_simple(web_app_client, headers):
    response = await web_app_client.get(
        '/reports-api/v1/summary/commercial-hiring/acquisition/types',
        headers={
            **headers,
            'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
            'Accept-Language': 'ru',
        },
        json={},
    )
    assert response.status == 200
    assert await response.json() == {
        'items': [
            {'id': 'partner', 'name': 'partner'},
            {'id': 'app', 'name': 'app'},
        ],
    }


async def test_empty_config(web_app_client, headers):
    response = await web_app_client.get(
        '/reports-api/v1/summary/commercial-hiring/acquisition/types',
        headers={
            **headers,
            'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
            'Accept-Language': 'ru',
        },
        json={},
    )
    assert response.status == 200
    assert await response.json() == {'items': []}


@pytest.mark.translations(fleet_enums=TRANSLATIONS)
@pytest.mark.config(
    FLEET_REPORTS_COMMERCIAL_HIRING_TYPES=[
        {'type_code': 'partner', 'tanker_code': 'partner'},
        {'type_code': 'app', 'tanker_code': 'app'},
    ],
)
async def test_exist_tanker_key(web_app_client, headers):
    response = await web_app_client.get(
        '/reports-api/v1/summary/commercial-hiring/acquisition/types',
        headers={
            **headers,
            'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
            'Accept-Language': 'ru',
        },
        json={},
    )
    assert response.status == 200
    assert await response.json() == {
        'items': [
            {'id': 'partner', 'name': 'Партнеры'},
            {'id': 'app', 'name': 'Приложение'},
        ],
    }
