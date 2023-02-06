import json

import pytest


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_get_menu_bunker(
        web_app_client, table_uuid, load_json, mockserver,
):
    @mockserver.handler('/cat')
    def cat(request):
        if (
                request.query['node']
                == '/eats-web/mercury/restaurants/place_id__1'
        ):
            return mockserver.make_response(
                json.dumps(load_json('bunker_response.json')), 200,
            )
        if (
                request.query['node']
                == '/eats-web/mercury/restaurants/place_id__1/logo'
        ):
            return mockserver.make_response(
                load_json('bunker_logo_response.json')['xml'], 200,
            )
        raise NotImplementedError()

    response = await web_app_client.get(f'/v1/menu?uuid={table_uuid}')
    assert response.status == 200
    data = await response.json()
    assert data == load_json('menu_bunker.json')

    assert cat.times_called == 2


@pytest.mark.client_experiments3(
    consumer='eats-integration-offline-orders/menu_sources',
    experiment_name='eats_integration_offline_orders-menu_sources',
    args=[{'name': 'place_id', 'type': 'string', 'value': 'place_id__1'}],
    value={'sources': ['database']},
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['tables.sql', 'restaurants.sql', 'db_menu.sql'],
)
async def test_get_menu_db(web_app_client, table_uuid, load_json):
    response = await web_app_client.get(f'/v1/menu?uuid={table_uuid}')
    assert response.status == 200
    data = await response.json()
    assert data == load_json('menu_db.json')
