import datetime

from crm_admin.generated.service.swagger import models


EVERY_SALT = '4457b9de118347c696eaa54c97b272f4'
OWNER_OF_ALL = 'test_owner'


async def create_target(
        web_app_client,
        target_body: models.api.TargetCreate,
        owner: str = OWNER_OF_ALL,
) -> int:
    response = await web_app_client.post(
        '/v1/targets',
        json=target_body.serialize(),
        headers={'X-Yandex-Login': owner},
    )
    assert response.status == 200
    target_id = await response.json()
    target_id = target_id['id']
    return target_id


async def create_target_for_periods(web_app_client) -> int:
    target_body = models.api.TargetCreate(
        audiences=['Driver', 'User', 'Geo'],
        is_available=True,
        is_important=True,
        label='fancy_target',
        name='Fancy Target',
        apply_conditions=None,
        control_settings=models.api.ControlSettings(
            is_control_active=True, is_control_enabled=True, track_all=True,
        ),
        description='whatever',
    )
    response = await web_app_client.post(
        '/v1/targets',
        json=target_body.serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200
    target_id = await response.json()
    target_id = target_id['id']
    return target_id


async def create_couple_of_periods(web_app_client, target_id: int):
    response = await web_app_client.post(
        f'/v1/targets/{target_id}/periods',
        json=models.api.PeriodUpdate(
            control_percentage=5,
            key='phone_pd_id',
            previous_control_percentage=50,
            start_at=datetime.datetime.fromisoformat(
                '2023-03-23T02:22:22+03:00',
            ),
        ).serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200

    response = await web_app_client.post(
        f'/v1/targets/{target_id}/periods',
        json=models.api.PeriodUpdate(
            control_percentage=10,
            key='phone_pd_id',
            previous_control_percentage=25,
            start_at=datetime.datetime.fromisoformat(
                '2024-04-24T02:22:22+03:00',
            ),
        ).serialize(),
        headers={'X-Yandex-Login': OWNER_OF_ALL},
    )
    assert response.status == 200
