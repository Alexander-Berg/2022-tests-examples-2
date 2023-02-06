import pytest


@pytest.mark.geo_nodes(filename='geonodes.json')
@pytest.mark.tariffs_cache(filename='tariffs.json')
@pytest.mark.config(
    SUBVENTION_RULE_UTILS_FILTER_TZ_NAME_EQ_ACTIVATION_ZONE_NAME=True,
    SUBVENTION_RULE_UTILS_ACTIVATION_ZONES_OF_INACTIVE_TARIFF_ZONES=[
        '0zone_activation',
    ],
)
@pytest.mark.parametrize(
    'geo_hierarchy_nodes, expected_tz_by_geonode, active_tz_from_request, inactive_tz_from_request',  # noqa: E501
    [
        ([], {}, [], []),
        (['moscow'], {}, ['moscow'], []),
        (
            ['br_moscow_adm'],
            {'br_moscow_adm': {'active': ['moscow'], 'inactive': ['vko']}},
            [],
            [],
        ),
        (
            ['moscow', 'br_almaty', 'vko'],
            {'br_almaty': {'active': [], 'inactive': ['almaty_hub']}},
            ['moscow'],
            ['vko'],
        ),
        (
            ['moscow', 'almaty_hub', 'vko'],
            {},
            ['moscow'],
            ['vko', 'almaty_hub'],
        ),
        (
            ['br_almaty', 'br_moscow_adm'],
            {
                'br_moscow_adm': {'active': ['moscow'], 'inactive': ['vko']},
                'br_almaty': {'active': [], 'inactive': ['almaty_hub']},
            },
            [],
            [],
        ),
    ],
)
async def test_get_and_split_tariff_zone_handler(
        taxi_subvention_admin,
        geo_hierarchy_nodes,
        expected_tz_by_geonode,
        active_tz_from_request,
        inactive_tz_from_request,
):
    response = await taxi_subvention_admin.post(
        '/internal/subvention-admin/v1/enrich-tariff-zones',
        json={'geo_hierarchy_nodes': geo_hierarchy_nodes},
    )

    assert response.status_code == 200
    response = response.json()

    assert sorted(
        [info['name'] for info in response['tariff_zones_by_geonode'][:]],
    ) == sorted(expected_tz_by_geonode.keys())
    for node_info in response['tariff_zones_by_geonode']:
        geonode_name = node_info['name']
        assert geonode_name in expected_tz_by_geonode

        active = []
        inactive = []
        for tz_info in node_info['tariff_zones']:
            if tz_info['is_active']:
                active.append(tz_info['name'])
            else:
                inactive.append(tz_info['name'])
        assert sorted(active) == sorted(
            expected_tz_by_geonode[geonode_name]['active'],
        )
        assert sorted(inactive) == sorted(
            expected_tz_by_geonode[geonode_name]['inactive'],
        )

    active = []
    inactive = []
    for tz_info in response['tariff_zones_from_request']:
        if tz_info['is_active']:
            active.append(tz_info['name'])
        else:
            inactive.append(tz_info['name'])
    assert sorted(active) == sorted(active_tz_from_request)
    assert sorted(inactive) == sorted(inactive_tz_from_request)
