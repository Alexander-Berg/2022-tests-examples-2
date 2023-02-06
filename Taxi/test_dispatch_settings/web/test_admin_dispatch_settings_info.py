import pytest


@pytest.mark.config(
    ALL_CATEGORIES=[
        'test_tariff_1',
        'test_tariff_2',
        'test_tariff_3',
        'test_tariff_4',
    ],
)
async def test_admin_dispatch_settings_info(
        taxi_dispatch_settings_web, tariffs,
):
    tariffs.set_zones(['zone1'])

    resp = await taxi_dispatch_settings_web.get(
        '/v1/admin/dispatch_settings_info',
    )
    assert resp.status == 200
    r_json = await resp.json()
    categories = r_json['categories']
    categories.sort(key=lambda category: category['zone_name'])
    for category in categories:
        category['tariff_names'].sort()
    groups = r_json['groups']
    groups['info'].sort(key=lambda group: group['group_name'])
    for info in groups['info']:
        info['tariff_names'].sort()
    groups['group_less_tariff_names'].sort()
    r_json['invalid_zones'].sort()

    assert r_json == {
        'categories': [
            {
                'zone_name': '__default__',
                'tariff_names': ['__default__group1__', 'test_tariff_1'],
            },
            {'zone_name': 'zone1', 'tariff_names': ['__default__group1__']},
        ],
        'groups': {
            'info': [
                {
                    'group_name': 'group1',
                    'tariff_names': [
                        '__default__group1__',
                        'test_tariff_1',
                        'test_tariff_2',
                    ],
                    'description': 'description',
                },
                {
                    'group_name': 'group2',
                    'tariff_names': ['__default__group2__'],
                    'description': 'description',
                },
            ],
            'group_less_tariff_names': ['test_tariff_3', 'test_tariff_4'],
        },
        'invalid_zones': ['zone2'],
    }
