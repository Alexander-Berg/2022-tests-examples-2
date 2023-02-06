# pylint: disable=unused-argument,too-many-arguments,unused-variable
import datetime

import pytest

from crm_admin import entity
from crm_admin import storage
from crm_admin.generated.service.swagger import models
from crm_admin.utils import audience_settings


EVERY_SALT = '4457b9de118347c696eaa54c97b272f4'
OWNER_OF_ALL = 'test_owner'


@pytest.mark.now('2022-02-22T02:22:22+03:00')
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_target_list(web_context, web_app_client):
    campaign_id = 2
    db_target = storage.DbTarget(context=web_context)
    db_period = storage.DbPeriod(context=web_context)
    db_conn = storage.DbTargetLink(context=web_context)
    whatever_datetime = datetime.datetime(2022, 1, 10, 2, 22, 22)

    # create target applied for tested campaign
    target = entity.Target(
        target_id=1,
        owner=OWNER_OF_ALL,
        name='Fancy Name',
        label='global_control_drivers',
        is_available=True,
        is_important=True,
        const_salt=EVERY_SALT,
        audiences=[audience_settings.AudienceType.DRIVERS],
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
        description='whatever',
        control_settings=entity.ControlSettings(
            is_control_enabled=True, is_control_active=True, track_all=False,
        ),
    )

    target = await db_target.create(target)
    await db_conn.create(campaign_id=campaign_id, target_id=target.target_id)

    # create pre-pre-previous period, shouldn't be relevant, too old
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.MURMUR,
            salt=EVERY_SALT,
            control_percentage=5,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2022, 2, 1, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # create pre-previous period, relevant
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.MURMUR,
            salt='prepresalt',
            control_percentage=5,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2022, 2, 2, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # create previous period, relevant
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.EXP3,
            salt='presalt',
            control_percentage=10,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2022, 2, 3, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # create current period, relevant
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.EXP3,
            salt='salt',
            control_percentage=10,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2022, 2, 4, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # create future period, should not be relevant
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.EXP3,
            salt='postsalt',
            control_percentage=10,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2024, 2, 1, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # --------------------------------------------------------------

    # create target applied for tested campaign, with only two periods
    target = entity.Target(
        target_id=2,
        owner=OWNER_OF_ALL,
        name='Fancy Name',
        label='fancy_control',
        is_available=True,
        is_important=True,
        const_salt=EVERY_SALT,
        audiences=[audience_settings.AudienceType.DRIVERS],
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
        description='whatever',
        control_settings=entity.ControlSettings(
            is_control_enabled=True, is_control_active=True, track_all=False,
        ),
    )

    target = await db_target.create(target)
    await db_conn.create(campaign_id=campaign_id, target_id=target.target_id)

    # create previous period, relevant
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.EXP3,
            salt='presalt',
            control_percentage=10,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2022, 2, 3, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # create current period, relevant
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.EXP3,
            salt='salt',
            control_percentage=10,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2022, 2, 4, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # --------------------------------------------------------------

    # create target applied for tested campaign, with only one period
    target = entity.Target(
        target_id=3,
        owner=OWNER_OF_ALL,
        name='Fancy Name',
        label='ultra_fancy_control',
        is_available=True,
        is_important=True,
        const_salt=EVERY_SALT,
        audiences=[audience_settings.AudienceType.DRIVERS],
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
        description='whatever',
        control_settings=entity.ControlSettings(
            is_control_enabled=True, is_control_active=True, track_all=False,
        ),
    )

    target = await db_target.create(target)
    await db_conn.create(campaign_id=campaign_id, target_id=target.target_id)

    # create current period, relevant
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.EXP3,
            salt='salt',
            control_percentage=10,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2022, 2, 4, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # --------------------------------------------------------------

    # create target applied for tested campaign, but not active
    target = entity.Target(
        target_id=4,
        owner=OWNER_OF_ALL,
        name='Fancy Name',
        label='super_ultra_fancy_control',
        is_available=True,
        is_important=True,
        const_salt=EVERY_SALT,
        audiences=[audience_settings.AudienceType.DRIVERS],
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
        description='whatever',
        control_settings=entity.ControlSettings(
            is_control_enabled=True, is_control_active=False, track_all=True,
        ),
    )

    target = await db_target.create(target)
    await db_conn.create(campaign_id=campaign_id, target_id=target.target_id)

    # create current period, relevant
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.EXP3,
            salt='salt',
            control_percentage=10,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2022, 2, 4, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # --------------------------------------------------------------

    # create target not applied for tested campaign, but with track all set
    target = entity.Target(
        target_id=5,
        owner=OWNER_OF_ALL,
        name='Fancy Name',
        label='mega_ultra_fancy_control_1',
        is_available=True,
        is_important=True,
        const_salt=EVERY_SALT,
        audiences=[audience_settings.AudienceType.DRIVERS],
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
        description='whatever',
        control_settings=entity.ControlSettings(
            is_control_enabled=True, is_control_active=True, track_all=True,
        ),
    )

    target = await db_target.create(target)

    # create current period, relevant
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.EXP3,
            salt='salt',
            control_percentage=10,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2022, 2, 4, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # --------------------------------------------------------------

    # create for different audience, but with track all set, not relevant
    target = entity.Target(
        target_id=6,
        owner=OWNER_OF_ALL,
        name='Fancy Name',
        label='mega_ultra_fancy_control_2',
        is_available=True,
        is_important=True,
        const_salt=EVERY_SALT,
        audiences=[audience_settings.AudienceType.USERS],
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
        description='whatever',
        control_settings=entity.ControlSettings(
            is_control_enabled=True, is_control_active=True, track_all=True,
        ),
    )

    target = await db_target.create(target)
    await db_conn.create(campaign_id=1, target_id=target.target_id)

    # create current period, relevant
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.EXP3,
            salt='salt',
            control_percentage=10,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2022, 2, 4, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # --------------------------------------------------------------

    # create target for different audience, should be irrelevant
    target = entity.Target(
        target_id=7,
        owner=OWNER_OF_ALL,
        name='Fancy Name',
        label='irrelevant_1',
        is_available=True,
        is_important=True,
        const_salt=EVERY_SALT,
        audiences=[audience_settings.AudienceType.USERS],
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
        description='whatever',
        control_settings=entity.ControlSettings(
            is_control_enabled=True, is_control_active=True, track_all=False,
        ),
    )

    target = await db_target.create(target)
    await db_conn.create(campaign_id=1, target_id=target.target_id)

    # create current period
    period = entity.Period(
        period_id=0,
        owner=OWNER_OF_ALL,
        target_id=target.target_id,
        control=entity.Control(
            mechanism=entity.ControlMechanismType.EXP3,
            salt='salt',
            control_percentage=10,
            key='phone_pd_id',
        ),
        previous_control_percentage=50,
        start_at=datetime.datetime(2022, 2, 4, 2, 22, 22),
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
    )
    await db_period.create(period)

    # --------------------------------------------------------------

    # create target with disabled control, should be irrelevant
    target = entity.Target(
        target_id=8,
        owner=OWNER_OF_ALL,
        name='Fancy Name',
        label='irrelevant_2',
        is_available=True,
        is_important=True,
        const_salt=EVERY_SALT,
        audiences=[audience_settings.AudienceType.DRIVERS],
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
        description='whatever',
        control_settings=entity.ControlSettings(
            is_control_enabled=False, is_control_active=True, track_all=False,
        ),
    )

    await db_target.create(target)
    await db_conn.create(campaign_id=campaign_id, target_id=target.target_id)

    # --------------------------------------------------------------

    # create target without any periods, should be irrelevant
    target = entity.Target(
        target_id=9,
        owner=OWNER_OF_ALL,
        name='Fancy Name',
        label='irrelevant_3',
        is_available=True,
        is_important=True,
        const_salt=EVERY_SALT,
        audiences=[audience_settings.AudienceType.DRIVERS],
        created_at=whatever_datetime,
        updated_at=whatever_datetime,
        description='whatever',
        control_settings=entity.ControlSettings(
            is_control_enabled=True, is_control_active=True, track_all=False,
        ),
    )

    await db_target.create(target)
    await db_conn.create(campaign_id=campaign_id, target_id=target.target_id)

    response = await web_app_client.get(
        '/v1/internal/targets/config', params={'campaign_id': 2},
    )

    expected_result = models.api.TargetConfig(
        targets_labels=[],
        control_targets=[
            models.api.TargetControlConfig(
                id=1,
                const_salt=EVERY_SALT,
                is_active=True,
                label='global_control_drivers',
                current_period=models.api.PeriodControlConfig(
                    current_control=models.api.SupercontrolConfig(
                        control_percentage=10,
                        key='phone_pd_id',
                        mechanism='exp3',
                        salt='salt',
                    ),
                    previous_control=models.api.SupercontrolConfig(
                        control_percentage=10,
                        key='phone_pd_id',
                        mechanism='exp3',
                        salt='presalt',
                    ),
                    previous_control_saved_percentage=50,
                    inverted_period_selection=True,
                ),
                previous_period=models.api.PeriodControlConfig(
                    current_control=models.api.SupercontrolConfig(
                        control_percentage=10,
                        key='phone_pd_id',
                        mechanism='exp3',
                        salt='presalt',
                    ),
                    previous_control=models.api.SupercontrolConfig(
                        control_percentage=5,
                        key='phone_pd_id',
                        mechanism='murmur',
                        salt='prepresalt',
                    ),
                    previous_control_saved_percentage=50,
                    inverted_period_selection=False,
                ),
            ),
            models.api.TargetControlConfig(
                id=2,
                const_salt=EVERY_SALT,
                is_active=True,
                label='fancy_control',
                current_period=models.api.PeriodControlConfig(
                    current_control=models.api.SupercontrolConfig(
                        control_percentage=10,
                        key='phone_pd_id',
                        mechanism='exp3',
                        salt='salt',
                    ),
                    previous_control=models.api.SupercontrolConfig(
                        control_percentage=10,
                        key='phone_pd_id',
                        mechanism='exp3',
                        salt='presalt',
                    ),
                    previous_control_saved_percentage=50,
                    inverted_period_selection=True,
                ),
                previous_period=models.api.PeriodControlConfig(
                    current_control=models.api.SupercontrolConfig(
                        control_percentage=10,
                        key='phone_pd_id',
                        mechanism='exp3',
                        salt='presalt',
                    ),
                    previous_control_saved_percentage=50,
                    inverted_period_selection=False,
                ),
            ),
            models.api.TargetControlConfig(
                id=3,
                const_salt=EVERY_SALT,
                is_active=True,
                label='ultra_fancy_control',
                current_period=models.api.PeriodControlConfig(
                    current_control=models.api.SupercontrolConfig(
                        control_percentage=10,
                        key='phone_pd_id',
                        mechanism='exp3',
                        salt='salt',
                    ),
                    previous_control_saved_percentage=50,
                    inverted_period_selection=False,
                ),
            ),
            models.api.TargetControlConfig(
                id=4,
                const_salt=EVERY_SALT,
                is_active=False,
                label='super_ultra_fancy_control',
                current_period=models.api.PeriodControlConfig(
                    current_control=models.api.SupercontrolConfig(
                        control_percentage=10,
                        key='phone_pd_id',
                        mechanism='exp3',
                        salt='salt',
                    ),
                    previous_control_saved_percentage=50,
                    inverted_period_selection=False,
                ),
            ),
            models.api.TargetControlConfig(
                id=5,
                const_salt=EVERY_SALT,
                is_active=False,
                label='mega_ultra_fancy_control_1',
                current_period=models.api.PeriodControlConfig(
                    current_control=models.api.SupercontrolConfig(
                        control_percentage=10,
                        key='phone_pd_id',
                        mechanism='exp3',
                        salt='salt',
                    ),
                    previous_control_saved_percentage=50,
                    inverted_period_selection=False,
                ),
            ),
        ],
    ).serialize()

    response_json = await response.json()
    response_json['control_targets'].sort(key=lambda v: v['id'])
    response_json['targets_labels'].sort()
    expected_result['control_targets'].sort(key=lambda v: v['id'])
    expected_result['targets_labels'].sort()

    assert response.status == 200
    assert expected_result == response_json


@pytest.mark.now('2022-02-22T02:22:22+03:00')
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_empty_campaign(web_context, web_app_client):

    response = await web_app_client.get(
        '/v1/internal/targets/config', params={'campaign_id': 2},
    )

    expected_result = models.api.TargetConfig(
        targets_labels=[], control_targets=[],
    )

    assert response.status == 200
    assert expected_result.serialize() == await response.json()
