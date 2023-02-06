import pytest

from tests_ride_discounts import common


@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'parent_name': 'br_moskovskaja_obl',
        },
        {
            'name': 'br_moscow_adm',
            'name_en': 'Moscow (adm)',
            'name_ru': 'Москва (адм)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
            'tariff_zones': ['moscow'],
            'region_id': '213',
        },
        {
            'name': 'br_moscow_middle_region',
            'name_en': 'Moscow (Middle Region)',
            'name_ru': 'Москва (среднее)',
            'node_type': 'node',
            'parent_name': 'br_moscow',
        },
        {
            'name': 'br_moskovskaja_obl',
            'node_type': 'node',
            'name_en': 'Moscow Region',
            'name_ru': 'Московская область',
            'parent_name': 'br_tsentralnyj_fo',
            'region_id': '1',
        },
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'country',
            'parent_name': 'br_root',
            'region_id': '225',
        },
        {
            'name': 'br_tsentralnyj_fo',
            'name_en': 'Central Federal District',
            'name_ru': 'Центральный ФО',
            'node_type': 'node',
            'parent_name': 'br_russia',
            'region_id': '3',
        },
    ],
)
@pytest.mark.parametrize(
    'request_body, expected_status_code, expected_body',
    (
        pytest.param(
            {
                'zones': [
                    {
                        'name': 'moscow',
                        'type': 'tariff_zone',
                        'is_prioritized': False,
                    },
                ],
            },
            200,
            {
                'zones_by_timezone': [
                    {
                        'timezone': 'Europe/Moscow',
                        'zones': [
                            {
                                'is_prioritized': False,
                                'name': 'moscow',
                                'type': 'tariff_zone',
                            },
                        ],
                    },
                ],
            },
            id='tariff_zone',
        ),
        pytest.param(
            {
                'zones': [
                    {
                        'name': 'br_moscow',
                        'type': 'geonode',
                        'is_prioritized': False,
                    },
                ],
            },
            200,
            {
                'zones_by_timezone': [
                    {
                        'timezone': 'Europe/Moscow',
                        'zones': [
                            {
                                'is_prioritized': False,
                                'name': 'br_moscow',
                                'type': 'geonode',
                            },
                        ],
                    },
                ],
            },
            id='geonode_with_tariff_zones',
        ),
        pytest.param(
            {
                'zones': [
                    {
                        'name': 'br_tsentralnyj_fo',
                        'type': 'geonode',
                        'is_prioritized': False,
                    },
                ],
            },
            200,
            {
                'zones_by_timezone': [
                    {
                        'timezone': 'Europe/Moscow',
                        'zones': [
                            {
                                'name': 'br_tsentralnyj_fo',
                                'type': 'geonode',
                                'is_prioritized': False,
                            },
                        ],
                    },
                ],
            },
            id='geonode_without_tariff_zones',
        ),
        pytest.param({'zones': []}, 400, None, id='empty_request'),
        pytest.param(
            {
                'zones': [
                    {
                        'name': 'mosccow',
                        'type': 'tariff_zone',
                        'is_prioritized': False,
                    },
                ],
            },
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Tariff zone mosccow has no tariff settings. Use utc time'
                ),
            },
            id='wrong_tariff_zone',
        ),
        pytest.param(
            {
                'zones': [
                    {
                        'name': 'mosccow',
                        'type': 'geonode',
                        'is_prioritized': False,
                    },
                ],
            },
            400,
            {
                'code': 'Validation error',
                'message': 'Geonode mosccow not found',
            },
            id='wrong_geonode',
        ),
    ),
)
async def test_v1_load_timezones(
        client, request_body, expected_status_code, expected_body,
):
    response = await client.post(
        '/v1/admin/load-timezones', request_body, headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code
    if expected_body is not None:
        assert response.json() == expected_body
