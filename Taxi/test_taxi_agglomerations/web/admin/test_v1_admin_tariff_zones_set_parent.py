import pytest
import pytz

PARAMETRIZE_OK: list = [
    pytest.param(
        {
            'tariff_zone': 'tomsk',
            'currency': 'RUB',
            'parent': {'geo_node_name': 'br_moscow_adm'},
        },
        {},
        {
            'hierarchy_type': 'BR',
            'name': 'br_moscow_adm',
            'tanker_key': 'name.br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'oebs_mvp_id': 'MSKc',
            'parents': ['br_moscow'],
            'tariff_zones': ['boryasvo', 'moscow', 'vko', 'tomsk'],
            'region_id': '213',
        },
        id='new',
    ),
    pytest.param(
        {
            'tariff_zone': 'moscow',
            'currency': 'RUB',
            'parent': {'geo_node_name': 'br_moscow_middle_region'},
        },
        {
            'hierarchy_type': 'BR',
            'name': 'br_moscow_adm',
            'tanker_key': 'name.br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'oebs_mvp_id': 'MSKc',
            'parents': ['br_moscow'],
            'tariff_zones': ['boryasvo', 'moscow', 'vko'],
            'region_id': '213',
        },
        {
            'hierarchy_type': 'BR',
            'name': 'br_moscow_middle_region',
            'tanker_key': 'name.br_moscow_middle_region',
            'name_en': 'Moscow (Middle Region)',
            'name_ru': 'Москва (среднее)',
            'node_type': 'node',
            'oebs_mvp_id': 'br_moscow_oebs_mvp_id',
            'parents': ['br_moscow'],
            'tariff_zones': ['moscow'],
        },
        id='existing',
    ),
]


PARAMETRIZE_WITH_ERROR: list = [
    pytest.param(
        {
            'tariff_zone': 'almaty',
            'currency': 'KZT',
            'parent': {'geo_node_name': 'br_moscow_adm'},
        },
        {
            'code': 'INVALID_CURRENCY',
            'message': 'Tariff zones must have the same currency with country',
        },
        id='invalid_currency',
    ),
    pytest.param(
        {
            'tariff_zone': 'tomsk',
            'currency': 'RUB',
            'parent': {'geo_node_name': 'invalid'},
        },
        {
            'code': 'GEO_NODE_NOT_FOUND',
            'message': 'GeoNode with name=invalid not found',
        },
        id='invalid_geo_node_name',
    ),
]


@pytest.mark.parametrize('body, expected_content', PARAMETRIZE_WITH_ERROR)
@pytest.mark.parametrize(
    'url',
    [
        '/v1/admin/tariff_zones/set_parent/',
        '/v1/admin/tariff_zones/set_parent/check/',
    ],
)
@pytest.mark.filldb()
async def test_v1_admin_tariff_zones_set_parent_with_error(
        web_app_client, body, expected_content, url,
):
    response = await web_app_client.post(url, json=body)
    assert response.status == 400, await response.json()
    assert await response.json() == expected_content


@pytest.mark.parametrize(
    'body, current_geo_node, updated_geo_node', PARAMETRIZE_OK,
)
@pytest.mark.filldb()
async def test_v1_admin_tariff_zones_set_parent_ok(
        web_app_client, body, current_geo_node, updated_geo_node, mocked_time,
):
    tariff_zone = body['tariff_zone']

    response = await web_app_client.post(
        '/v1/admin/tariff_zones/set_parent/check/', json=body,
    )
    assert response.status == 200, await response.json()

    response = await web_app_client.get(
        'v1/admin/geo-nodes/list/', params={'tariff_zones': tariff_zone},
    )
    current_geo_nodes = []
    if current_geo_node:
        current_geo_nodes.append(current_geo_node)
    assert (await response.json())['items'] == current_geo_nodes

    response = await web_app_client.post(
        '/v1/admin/tariff_zones/set_parent/', json=body,
    )
    assert response.status == 200

    response = await web_app_client.get(
        'v1/admin/geo-nodes/list/', params={'tariff_zones': tariff_zone},
    )

    assert (await response.json())['items'] == [updated_geo_node]
    oebs_mvp_id = updated_geo_node['oebs_mvp_id']

    await web_app_client.app['context'].oebs_mvp_cache.refresh_cache()

    mocked_time.sleep(1)

    response = await web_app_client.get(
        'v1/geo_nodes/get_mvp_oebs_id', params={'tariff_zone': tariff_zone},
    )
    assert response.status == 200
    assert await response.json() == {'oebs_mvp_id': oebs_mvp_id}
    now = mocked_time.now().replace(tzinfo=pytz.utc).isoformat()
    response = await web_app_client.get(
        'v1/geo_nodes/get_mvp_oebs_id',
        params={'tariff_zone': tariff_zone, 'dt': now},
    )
    assert response.status == 200
    assert await response.json() == {'oebs_mvp_id': oebs_mvp_id}
