import pytest


DEFAULT_HEADERS = {'X-YaTaxi-Draft-Id': 'test_draft_id'}

PARAMETRIZE_OK: list = [
    pytest.param('br_moscow_middle_region', id='br_moscow_middle_region'),
]


PARAMETRIZE_WITH_ERROR: list = [
    pytest.param(
        'br_root',
        {
            'code': 'FORBID_DELETING_GEO_NODE_WITH_CHILDREN',
            'message': (
                'GeoNode has children: [\'br_russia\', \'br_kazakhstan\']'
            ),
        },
        id='with_children',
    ),
    pytest.param(
        'br_moscow_adm',
        {
            'code': 'FORBID_DELETING_GEO_NODE_WITH_TARIFF_ZONES',
            'message': (
                'GeoNode has tariff_zones: [\'boryasvo\', \'moscow\', \'vko\']'
            ),
        },
        id='with_tariff_zones',
    ),
]


@pytest.mark.parametrize('name, expected_content', PARAMETRIZE_WITH_ERROR)
@pytest.mark.parametrize(
    'url', ['v1/admin/geo-node/delete/', 'v1/admin/geo-node/delete/check/'],
)
@pytest.mark.filldb()
async def test_v1_admin_geo_node_delete_with_error(
        web_app_client, name, expected_content, url,
):
    response = await web_app_client.post(
        url, json={'name': name}, headers=DEFAULT_HEADERS,
    )
    assert response.status == 400
    assert await response.json() == expected_content


@pytest.mark.parametrize('name', PARAMETRIZE_OK)
@pytest.mark.filldb()
async def test_v1_admin_geo_node_delete_ok(web_app_client, name):
    body = {'name': name}
    response = await web_app_client.get('v1/admin/geo-node/', params=body)

    assert response.status == 200
    parent_names = (await response.json()).get('parents', [])

    response = await web_app_client.post(
        'v1/admin/geo-node/delete/check/', json=body,
    )
    assert response.status == 200, await response.json()
    expected_check = {
        'change_doc_id': name,
        'data': {'name': name, 'hierarchy_type': name[:2].upper()},
    }
    assert await response.json() == expected_check

    response = await web_app_client.post(
        'v1/admin/geo-node/delete/', json=body, headers=DEFAULT_HEADERS,
    )
    assert response.status == 200, await response.json()
    response = await web_app_client.get('v1/admin/geo-node/', params=body)
    assert response.status == 404
    assert await response.json() == {
        'code': 'NOT_FOUND',
        'message': f'GeoNode with name="{name}" not found',
    }

    for parent_name in parent_names:
        response = await web_app_client.get(
            'v1/admin/geo-node/', params={'name': parent_name},
        )
        assert response.status == 200
        children = (await response.json()).get('children', [])
        assert name not in children
