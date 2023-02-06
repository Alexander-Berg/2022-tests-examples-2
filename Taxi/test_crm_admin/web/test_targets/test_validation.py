# pylint: disable=redefined-outer-name,unused-variable,too-many-lines
import datetime

import pytest

from crm_admin import storage
from crm_admin.generated.service.swagger import models
from test_crm_admin.web.test_targets import utils


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_period_start_at(web_context, web_app_client):
    start_at = datetime.datetime.fromisoformat('2022-02-22T01:22:22+03:00')
    target_id = await utils.create_target_for_periods(web_app_client)
    period_body = models.api.PeriodUpdate(
        control_percentage=5,
        key='phone_pd_id',
        previous_control_percentage=50,
        start_at=start_at,
    )

    response = await web_app_client.post(
        f'/v1/targets/{target_id}/periods',
        json=period_body.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )

    assert response.status == 400
    assert (await response.json()) == {
        'errors': [
            {
                'code': 'period_start_at_error',
                'details': {
                    'reason': 'Can not set the "start_at" earlier than now',
                    'field': 'start_at',
                    'value': '2022-02-21 22:22:22',
                },
            },
        ],
    }


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_period_control(web_context, web_app_client):
    start_at = datetime.datetime.fromisoformat('2022-02-22T03:22:22+03:00')
    target_id = await utils.create_target_for_periods(web_app_client)
    period_body = models.api.PeriodUpdate(
        control_percentage=5,
        key='phone_pd_id',
        previous_control_percentage=50,
        start_at=start_at,
    )

    response = await web_app_client.post(
        f'/v1/targets/{target_id}/periods',
        json=period_body.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )

    assert response.status == 200

    period_body.key = 'user_id'

    response = await web_app_client.post(
        f'/v1/targets/{target_id}/periods',
        json=period_body.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )

    assert response.status == 400
    assert (await response.json()) == {
        'errors': [
            {
                'code': 'period_key_error',
                'details': {
                    'reason': (
                        'The key must be the same as'
                        ' the previous periods have'
                    ),
                    'value': 'phone_pd_id',
                },
            },
        ],
    }


async def test_target_label(web_context, web_app_client):
    target = models.api.TargetCreate(
        audiences=['User'],
        is_available=True,
        is_important=False,
        label='target_1',
        name='name',
    )

    response = await web_app_client.post(
        '/v1/targets',
        json=target.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/targets',
        json=target.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )
    assert response.status == 400

    assert (await response.json()) == {
        'errors': [
            {
                'code': 'target_label_error',
                'details': {
                    'reason': 'Target with this label exists',
                    'field': 'label',
                    'value': 'target_1',
                    'target_id': 1,
                },
            },
        ],
    }


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_target_control(web_context, web_app_client):
    target = models.api.TargetCreate(
        audiences=['User'],
        is_available=True,
        is_important=False,
        label='target_1',
        name='name',
        control_settings=models.api.ControlSettings(
            is_control_active=True, is_control_enabled=True, track_all=False,
        ),
    )

    response = await web_app_client.post(
        '/v1/targets',
        json=target.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )
    assert response.status == 200

    target_id = (await response.json())['id']
    target.control_settings.is_control_enabled = False

    response = await web_app_client.put(
        f'/v1/targets/{target_id}',
        json=target.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )
    assert response.status == 400

    assert (await response.json()) == {
        'errors': [
            {
                'code': 'target_control_enabled_error',
                'details': {'reason': 'Can not disable enabled control'},
            },
        ],
    }


@pytest.mark.pgsql('crm_admin', files=['campaign.sql'])
@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_target_audiences(web_context, web_app_client):
    campaign_id = 1
    target = models.api.TargetCreate(
        audiences=['User', 'Driver'],
        is_available=True,
        is_important=False,
        label='target_1',
        name='name',
        control_settings=models.api.ControlSettings(
            is_control_active=True, is_control_enabled=True, track_all=False,
        ),
    )

    response = await web_app_client.post(
        '/v1/targets',
        json=target.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )
    assert response.status == 200

    target_id = (await response.json())['id']

    db_target_link = storage.DbTargetLink(web_context)
    await db_target_link.create(campaign_id, target_id)

    target.audiences = ['User']

    response = await web_app_client.put(
        f'/v1/targets/{target_id}',
        json=target.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )
    assert response.status == 400

    assert (await response.json()) == {
        'errors': [
            {
                'code': 'target_in_active_campaign',
                'details': {
                    'reason': (
                        'Can not delete audiences, there are '
                        'a linked campaign with this audiences'
                    ),
                    'audiences': ['Driver'],
                    'value': '1',
                },
            },
        ],
    }


@pytest.mark.pgsql('crm_admin', files=['campaign.sql', 'target.sql'])
@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_keys(web_context, web_app_client, patch):
    @patch(
        'crm_admin.utils.validation.groupings.campaign_pre_start_validation',
    )
    async def validate(*args, **kwargs):
        return []

    @patch('crm_admin.utils.common.get_yt_columns')
    async def get_yt_columns(*args, **kwargs):
        return ['unique_driver_id']

    campaign_id = 1
    target_id = 1

    db_target_link = storage.DbTargetLink(web_context)
    await db_target_link.create(campaign_id, target_id)

    response = await web_app_client.post(
        f'/v1/campaigns/apply_draft',
        params={'campaign_id': campaign_id},
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )
    assert response.status == 400

    assert (await response.json()) == {
        'errors': [
            {
                'code': 'segment_non_existent_keys',
                'details': {
                    'reason': (
                        'Targets have keys that are not exists '
                        'in the segment'
                    ),
                    'value': '1',
                },
            },
        ],
    }
