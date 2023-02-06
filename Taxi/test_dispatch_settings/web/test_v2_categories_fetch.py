import pytest


@pytest.mark.config(
    ALL_CATEGORIES=[
        'test_tariff_1',
        'test_tariff_2',
        'test_tariff_3',
        'test_tariff_4',
    ],
    DISPATCH_SETTINGS_DETAILED_FETCH_LOG={
        'enabled': True,
        'tariffs': ['test_tariff_1'],
        'types': [],
        'zones': ['zone1'],
    },
)
async def test_service_categories_fetch(taxi_dispatch_settings_web):
    response = await taxi_dispatch_settings_web.get('/v2/categories/fetch')

    assert response.status == 200
    content = await response.json()

    # Response normalization to prevent flaps
    categories = content['categories']
    categories.sort(key=lambda cat_obj: cat_obj['zone_name'])
    for cat in categories:
        cat['tariff_names'].sort()
    groups = content['groups']
    groups.sort(key=lambda group: group['group_name'])
    for group in groups:
        group['tariff_names'].sort()
    assert content == {
        'categories': [
            {
                'zone_name': '__default__',
                'tariff_names': ['__default__group1__', 'test_tariff_1'],
            },
            {'zone_name': 'zone1', 'tariff_names': ['__default__group1__']},
        ],
        'groups': [
            {
                'group_name': 'group1',
                'tariff_names': [
                    '__default__group1__',
                    'test_tariff_1',
                    'test_tariff_2',
                ],
            },
            {'group_name': 'group2', 'tariff_names': ['__default__group2__']},
        ],
    }
