import pytest

from grocery_tasks.autoorder.config import get_city_id


@pytest.mark.config(
    GROCERY_REGIONS_CONTROL={
        'regions': [
            {
                'cities': [{'id': 10393, 'name': 'London'}],
                'jns_notifications': False,
                'name': 'england',
            },
            {'cities': [{'id': 10502, 'name': 'Paris'}], 'name': 'france'},
            {'cities': [{'id': 131, 'name': 'Tel Aviv'}], 'name': 'israel'},
            {'cities': [{'id': 63, 'name': 'irkutsk'}], 'name': 'irkutsk'},
            {
                'cities': [
                    {'id': 193, 'name': 'Voronezh'},
                    {'id': 54, 'name': 'Ekaterinburg'},
                    {'id': 43, 'name': 'Kazan'},
                    {'id': 35, 'name': 'Krasnodar'},
                    {'id': 213, 'name': 'Moscow'},
                    {'id': 47, 'name': 'Nizhniy Novgorod'},
                    {'id': 65, 'name': 'Novosibirsk'},
                    {'id': 39, 'name': 'Rostov-on-Don'},
                    {'id': 2, 'name': 'Saint-Petersburg'},
                    {'id': 172, 'name': 'Ufa'},
                ],
                'jns_notifications': True,
                'name': 'russia_center',
            },
        ],
    },
)
@pytest.mark.usefixtures()
async def test_get_city_id_irkutsk(cron_context):
    assert get_city_id(cron_context, 'irkutsk') == 63
