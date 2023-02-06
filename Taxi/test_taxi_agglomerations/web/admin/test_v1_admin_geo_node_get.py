import pytest

PARAMETRIZE: list = [
    pytest.param(
        {'name': 'br_root'},
        200,
        {
            'children': ['br_russia', 'br_kazakhstan'],
            'hierarchy_type': 'BR',
            'name': 'br_root',
            'tanker_key': 'name.br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        id='ok_br_root',
    ),
    pytest.param(
        {'name': 'fi_root'},
        200,
        {
            'hierarchy_type': 'FI',
            'children': ['br_moscow', 'fi_emea'],
            'name': 'fi_root',
            'tanker_key': 'name.fi_root',
            'name_en': 'Financial Regions',
            'name_ru': 'Финансовые регионы',
            'node_type': 'root',
        },
        id='ok_fi_root',
    ),
    pytest.param(
        {'name': 'op_root'},
        200,
        {
            'hierarchy_type': 'OP',
            'children': ['br_moscow'],
            'name': 'op_root',
            'tanker_key': 'name.op_root',
            'name_en': 'Operational hierarchy',
            'name_ru': 'Операционная иерархия',
            'node_type': 'root',
        },
        id='ok_op_root',
    ),
    pytest.param(
        {'name': 'br_kazakhstan'},
        200,
        {
            'currency': 'KZT',
            'hierarchy_type': 'BR',
            'name': 'br_kazakhstan',
            'tanker_key': 'name.br_kazakhstan',
            'name_en': 'Kazakhstan',
            'name_ru': 'Казахстан',
            'region_id': '159',
            'node_type': 'country',
            'parents': ['br_root'],
        },
        id='ok_br_kazakhstan',
    ),
    pytest.param(
        {'name': 'br_moscow'},
        200,
        {
            'children': ['br_moscow_adm', 'br_moscow_middle_region'],
            'hierarchy_type': 'BR',
            'name': 'br_moscow',
            'tanker_key': 'name.br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'oebs_mvp_id': 'MSKc',
            'parents': ['br_moskovskaja_obl', 'fi_root', 'op_root'],
            'operational_managers': ['susloparov'],
            'macro_managers': ['mikhailra'],
            'meta_tags': ['agglomeration_with_only_br_parent'],
        },
        id='ok_br_moscow',
    ),
    pytest.param(
        {'name': 'invalid'},
        404,
        {
            'code': 'NOT_FOUND',
            'message': 'GeoNode with name="invalid" not found',
        },
        id='not_found',
    ),
]


@pytest.mark.parametrize(
    'query, expected_status, expected_content', PARAMETRIZE,
)
@pytest.mark.filldb()
async def test_v1_admin_geo_node_get(
        client, query, expected_status, expected_content,
):
    response = await client.get('v1/admin/geo-node/', params=query)
    assert response.status == expected_status, await response.json()
    assert await response.json() == expected_content
