import pytest


@pytest.mark.config(
    DEV_TEAMS={
        'antifraud': {
            'description': 'Группа разработки антифрода Яндекс.Такси',
            'staff_groups': [
                'yandex_distproducts_browserdev_mobile_taxi_9720_3001',
            ],
        },
        'billing_infra': {
            'description': (
                'Группа разработки биллинговой инфраструктуры Яндекс.Такси'
            ),
            'staff_groups': [
                'yandex_distproducts_browserdev_mobile_taxi_9720_4183',
            ],
        },
    },
)
async def test_dev_teams_list_get(web_app_client):
    response = await web_app_client.get('/v1/dev-teams/list/')
    assert await response.json() == {
        'dev_teams': ['antifraud', 'billing_infra'],
    }
