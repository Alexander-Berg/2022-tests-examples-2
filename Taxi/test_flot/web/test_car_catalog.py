import pytest


@pytest.mark.parametrize('login,status', [('123', 200)])
async def test_get_car_catalog_types(
        web_context, web_app_client, login, status,
):
    response = await web_app_client.get(
        '/car_catalog/types', headers={'X-Yandex-UID': login},
    )
    assert response.status == status


@pytest.mark.parametrize('login,status', [('123', 200)])
async def test_get_car_catalog_colors(
        web_context, web_app_client, login, status,
):
    response = await web_app_client.get(
        '/car_catalog/colors', headers={'X-Yandex-UID': login},
    )
    assert response.status == status


@pytest.mark.parametrize(
    'login,status,params', [('123', 200, {'type': 'CAR'})],
)
async def test_get_car_catalog_bodies(
        web_context, web_app_client, login, status, params,
):
    response = await web_app_client.get(
        '/car_catalog/bodies', headers={'X-Yandex-UID': login}, params=params,
    )
    assert response.status == status


@pytest.mark.parametrize(
    'login,status,params', [('123', 200, {'type': 'CAR'})],
)
async def test_get_car_catalog_options(
        web_context, web_app_client, login, status, params,
):
    response = await web_app_client.get(
        '/car_catalog/options', headers={'X-Yandex-UID': login}, params=params,
    )
    assert response.status == status


@pytest.mark.parametrize('login,status,params', [('123', 200, {'year': 2022})])
async def test_get_car_catalog_brands(
        web_context, web_app_client, login, status, params,
):
    response = await web_app_client.get(
        '/car_catalog/brands', headers={'X-Yandex-UID': login}, params=params,
    )
    assert response.status == status


@pytest.mark.parametrize(
    'login,status,params', [('123', 200, {'brand': 'HAVAL', 'year': 2019})],
)
async def test_get_car_catalog_models(
        web_context, web_app_client, login, status, params,
):
    response = await web_app_client.get(
        '/car_catalog/models', headers={'X-Yandex-UID': login}, params=params,
    )
    assert response.status == status


@pytest.mark.parametrize(
    'login,status,params',
    [('123', 200, {'brand': 'HAVAL', 'model': 'F7X', 'year': 2022})],
)
async def test_get_car_catalog_generations(
        web_context, web_app_client, login, status, params,
):
    response = await web_app_client.get(
        '/car_catalog/generations',
        headers={'X-Yandex-UID': login},
        params=params,
    )
    assert response.status == status


@pytest.mark.parametrize(
    'login,status,params',
    [
        (
            '123',
            200,
            {
                'brand': 'HAVAL',
                'model': 'F7X',
                'generation': '21709866',
                'year': 2022,
            },
        ),
    ],
)
async def test_get_car_catalog_configurations(
        web_context, web_app_client, login, status, params,
):
    response = await web_app_client.get(
        '/car_catalog/configurations',
        headers={'X-Yandex-UID': login},
        params=params,
    )
    assert response.status == status


@pytest.mark.parametrize(
    'login,status,params',
    [
        (
            '123',
            200,
            {
                'brand': 'HAVAL',
                'model': 'F7X',
                'generation': '21709866',
                'configuration': '21709901',
                'year': 2022,
            },
        ),
    ],
)
async def test_get_car_catalog_techparams(
        web_context, web_app_client, login, status, params,
):
    response = await web_app_client.get(
        '/car_catalog/techparams',
        headers={'X-Yandex-UID': login},
        params=params,
    )
    assert response.status == status
