import copy
import datetime

import pytest

from crm_admin.generated.service.swagger import models
from test_crm_admin.web.test_targets import utils


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_target_list(web_context, web_app_client):

    perfect_target_body = models.api.TargetCreate(
        audiences=['Driver', 'User', 'Geo'],
        is_available=True,
        is_important=True,
        label='fancy_target_1',
        name='Fancy Wat Target',
        apply_conditions=None,
        control_settings=models.api.ControlSettings(
            is_control_active=True, is_control_enabled=True, track_all=True,
        ),
        description='whatever',
    )

    # creating a perfectly matching target
    target_id = await utils.create_target(
        web_app_client=web_app_client, target_body=perfect_target_body,
    )
    await utils.create_couple_of_periods(
        web_app_client=web_app_client, target_id=target_id,
    )

    perfect_target_body.label = 'fancy_target_2'

    # creating another perfectly matching target
    perfect_target_body.label = 'fancy_target_2'
    target_id = await utils.create_target(
        web_app_client=web_app_client, target_body=perfect_target_body,
    )
    await utils.create_couple_of_periods(
        web_app_client=web_app_client, target_id=target_id,
    )

    perfect_target_body.label = 'fancy_target_3'

    # creating target without matching owner
    perfect_target_body.label = 'fancy_target_3'
    target_id = await utils.create_target(
        web_app_client=web_app_client,
        target_body=perfect_target_body,
        owner='rando',
    )
    await utils.create_couple_of_periods(
        web_app_client=web_app_client, target_id=target_id,
    )

    # creating target without matching audience
    imperfect_target_body = copy.deepcopy(perfect_target_body)
    imperfect_target_body.audiences = ['User', 'Geo']
    imperfect_target_body.label = 'fancy_target_4'

    imperfect_target_body.label = 'fancy_target_4'

    target_id = await utils.create_target(
        web_app_client=web_app_client, target_body=imperfect_target_body,
    )
    await utils.create_couple_of_periods(
        web_app_client=web_app_client, target_id=target_id,
    )

    # creating target without matching name
    imperfect_target_body = copy.deepcopy(perfect_target_body)
    imperfect_target_body.name = 'Fancy Target'
    imperfect_target_body.label = 'fancy_target_5'

    target_id = await utils.create_target(
        web_app_client=web_app_client, target_body=imperfect_target_body,
    )
    await utils.create_couple_of_periods(
        web_app_client=web_app_client, target_id=target_id,
    )

    # creating unavailable target
    imperfect_target_body = copy.deepcopy(perfect_target_body)
    imperfect_target_body.is_available = False
    imperfect_target_body.label = 'fancy_target_6'

    target_id = await utils.create_target(
        web_app_client=web_app_client, target_body=imperfect_target_body,
    )
    await utils.create_couple_of_periods(
        web_app_client=web_app_client, target_id=target_id,
    )

    # creating target without actual control
    target_id = await utils.create_target(
        web_app_client=web_app_client,
        target_body=models.api.TargetCreate(
            audiences=['Driver', 'User', 'Geo'],
            is_available=True,
            is_important=True,
            label='fancy_target_7',
            name='Fancy Wat Target',
            apply_conditions=None,
            control_settings=models.api.ControlSettings(
                is_control_active=False,
                is_control_enabled=True,
                track_all=True,
            ),
            description='whatever',
        ),
    )
    await utils.create_couple_of_periods(
        web_app_client=web_app_client, target_id=target_id,
    )

    # creating target without actual control another variant
    target_id = await utils.create_target(
        web_app_client=web_app_client,
        target_body=models.api.TargetCreate(
            audiences=['Driver', 'User', 'Geo'],
            is_available=True,
            is_important=True,
            label='fancy_target_8',
            name='Fancy Wat Target',
            apply_conditions=None,
            control_settings=models.api.ControlSettings(
                is_control_active=True,
                is_control_enabled=False,
                track_all=True,
            ),
            description='whatever',
        ),
    )
    await utils.create_couple_of_periods(
        web_app_client=web_app_client, target_id=target_id,
    )

    # creating target without actual control yet another variant
    imperfect_target_body = copy.deepcopy(perfect_target_body)
    imperfect_target_body.control_settings = None
    imperfect_target_body.label = 'fancy_target_9'

    await utils.create_target(
        web_app_client=web_app_client, target_body=imperfect_target_body,
    )

    response = await web_app_client.put(
        f'/v1/targets',
        json=models.api.TargetsFilter(
            audience='Driver',
            is_available=True,
            is_controlled=True,
            name='wat',
            owner=utils.OWNER_OF_ALL,
        ).serialize(),
    )

    expected_result = [
        models.api.TargetListItem(
            id=1,
            description='whatever',
            audiences=['Driver', 'User', 'Geo'],
            created_at=datetime.datetime.fromisoformat(
                '2022-02-22T02:22:22+03:00',
            ),
            updated_at=datetime.datetime.fromisoformat(
                '2022-02-22T02:22:22+03:00',
            ),
            name='Fancy Wat Target',
            owner=utils.OWNER_OF_ALL,
            control_settings=models.api.ControlSettings(
                is_control_active=True,
                is_control_enabled=True,
                track_all=True,
            ),
            is_important=True,
            is_available=True,
            periods=[
                models.api.PeriodGet(
                    id=1,
                    owner=utils.OWNER_OF_ALL,
                    control=models.api.Control(
                        control_percentage=5,
                        key='phone_pd_id',
                        salt=utils.EVERY_SALT,
                    ),
                    previous_control_percentage=50,
                    start_at=datetime.datetime.fromisoformat(
                        '2023-03-23T02:22:22+03:00',
                    ),
                    created_at=datetime.datetime.fromisoformat(
                        '2022-02-22T02:22:22+03:00',
                    ),
                    updated_at=datetime.datetime.fromisoformat(
                        '2022-02-22T02:22:22+03:00',
                    ),
                ),
                models.api.PeriodGet(
                    id=2,
                    owner=utils.OWNER_OF_ALL,
                    control=models.api.Control(
                        control_percentage=10,
                        key='phone_pd_id',
                        salt=utils.EVERY_SALT,
                    ),
                    previous_control_percentage=25,
                    start_at=datetime.datetime.fromisoformat(
                        '2024-04-24T02:22:22+03:00',
                    ),
                    created_at=datetime.datetime.fromisoformat(
                        '2022-02-22T02:22:22+03:00',
                    ),
                    updated_at=datetime.datetime.fromisoformat(
                        '2022-02-22T02:22:22+03:00',
                    ),
                ),
            ],
        ).serialize(),
        models.api.TargetListItem(
            id=2,
            description='whatever',
            audiences=['Driver', 'User', 'Geo'],
            created_at=datetime.datetime.fromisoformat(
                '2022-02-22T02:22:22+03:00',
            ),
            updated_at=datetime.datetime.fromisoformat(
                '2022-02-22T02:22:22+03:00',
            ),
            name='Fancy Wat Target',
            owner=utils.OWNER_OF_ALL,
            control_settings=models.api.ControlSettings(
                is_control_active=True,
                is_control_enabled=True,
                track_all=True,
            ),
            is_important=True,
            is_available=True,
            periods=[
                models.api.PeriodGet(
                    id=3,
                    owner=utils.OWNER_OF_ALL,
                    control=models.api.Control(
                        control_percentage=5,
                        key='phone_pd_id',
                        salt=utils.EVERY_SALT,
                    ),
                    previous_control_percentage=50,
                    start_at=datetime.datetime.fromisoformat(
                        '2023-03-23T02:22:22+03:00',
                    ),
                    created_at=datetime.datetime.fromisoformat(
                        '2022-02-22T02:22:22+03:00',
                    ),
                    updated_at=datetime.datetime.fromisoformat(
                        '2022-02-22T02:22:22+03:00',
                    ),
                ),
                models.api.PeriodGet(
                    id=4,
                    owner=utils.OWNER_OF_ALL,
                    control=models.api.Control(
                        control_percentage=10,
                        key='phone_pd_id',
                        salt=utils.EVERY_SALT,
                    ),
                    previous_control_percentage=25,
                    start_at=datetime.datetime.fromisoformat(
                        '2024-04-24T02:22:22+03:00',
                    ),
                    created_at=datetime.datetime.fromisoformat(
                        '2022-02-22T02:22:22+03:00',
                    ),
                    updated_at=datetime.datetime.fromisoformat(
                        '2022-02-22T02:22:22+03:00',
                    ),
                ),
            ],
        ).serialize(),
    ]

    assert response.status == 200
    assert expected_result == await response.json()
