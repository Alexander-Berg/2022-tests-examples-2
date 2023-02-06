# pylint: disable=import-only-modules,unused-variable
from aiohttp import web
from freezegun.api import FakeDatetime
import pytest

from crm_admin import settings
from crm_admin.storage import campaign_adapters
from crm_admin.storage import group_adapters


@pytest.fixture(autouse=True)
def skip_parametrization_validation(patch):
    @patch(
        'crm_admin.utils.validation'
        '.extra_data_validators.validate_personalization_params',
    )
    async def validation(*agrs, **kwargs):  # pylint: disable=unused-variable
        return []


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_campaign_not_found(
        web_app_client,
):  # , stq, campaign_id, status):
    campaign_id = -1
    body = {'group_ids': [1, 3, 5], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 424
    body = await response.json()
    assert body == {'message': 'Campaign -1 was not found'}


# ****************************************************************************


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_campaign_without_segment(web_app_client):
    campaign_id = 1
    body = {'group_ids': [1], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 424


# ****************************************************************************


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_group_without_content_and_feed_id(web_app_client):
    campaign_id = 2
    body = {'group_ids': [2], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 424
    body = await response.json()
    assert body == {
        'message': 'Campaign has a group with empty content/feed_id',
    }


# ****************************************************************************


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_group_without_feed_id(
        web_app_client, mock_promotions,
):  # have content
    campaign_id = 3

    @mock_promotions('/admin/promotions/')
    async def _promo(request):
        return web.json_response(
            {
                'id': 'good_content',
                'name': 'name',
                'promotion_type': 'promotion_type',
                'status': 'status',
            },
            status=200,
        )

    body = {'group_ids': [3], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 424
    body = await response.json()
    assert body == {'message': 'Group 3 has invalid state \'None\'.'}


# ****************************************************************************


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_group_fs_without_days_count(web_app_client):
    campaign_id = 5
    body = {'group_ids': [5], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 424
    body = await response.json()
    assert body == {'message': 'Channel has no days_count/time_until'}


# ****************************************************************************


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_group_fs_without_time_until(web_app_client):
    campaign_id = 6
    body = {'group_ids': [6], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 424
    body = await response.json()
    assert body == {'message': 'Channel has no days_count/time_until'}


# ****************************************************************************


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_bad_group_state(web_app_client):
    campaign_id = 7
    body = {'group_ids': [7], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 424
    body = await response.json()
    assert body['message'] == 'Group 7 has invalid state \'HOLD\'.'


# ****************************************************************************


@pytest.mark.now('2021-04-12 17:01:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_campaign_late(web_app_client, web_context):
    campaign_id = 10
    body = {'group_ids': [14], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 400
    body = await response.json()
    assert body == {
        'errors': [{'code': 'campaign_efficiency_stop_time_expired'}],
    }


# ****************************************************************************


@pytest.mark.now('2021-04-08 17:01:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_group_late(web_app_client, web_context):
    campaign_id = 10
    body = {'group_ids': [14], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 424
    body = await response.json()
    assert body['message'] == 'Group 14 too late to start.'


# ****************************************************************************


@pytest.mark.now('2021-04-05 15:00:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_efficiency_item_success(web_app_client, web_context, stq):
    campaign_id = 10
    body = {'group_ids': [14], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 200
    # check stq called
    assert stq.crm_admin_batch_sending.times_called == 1


# ****************************************************************************


@pytest.mark.config(
    CRM_ADMIN_FEATURE_FLAGS_V2=[
        {'feature_name': 'group_actions', 'is_fully_enabled': True},
    ],
    CRM_ADMIN_GROUPS_V2={'all_on': True},
)
@pytest.mark.now('2022-04-05 15:00:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_efficiency_without_actions(web_app_client, web_context, stq):
    campaign_id = 35
    body = {'group_ids': [30], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 400

    data = await response.json()
    errors = data['errors']
    assert len(errors) == 2
    assert errors[0]['code'] == 'invalid_parameter_value'
    assert errors[1]['code'] == 'invalid_parameter_value'
    assert stq.crm_admin_batch_sending.times_called == 0


# ****************************************************************************


@pytest.mark.config(
    CRM_ADMIN_FEATURE_FLAGS_V2=[
        {'feature_name': 'group_actions', 'is_fully_enabled': False},
    ],
    CRM_ADMIN_GROUPS_V2={'all_on': True},
)
@pytest.mark.now('2022-04-05 15:00:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_efficiency_with_off_feature(web_app_client, web_context, stq):
    campaign_id = 35
    body = {'group_ids': [30], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 200


# ****************************************************************************


@pytest.mark.config(
    CRM_ADMIN_FEATURE_FLAGS_V2=[
        {'feature_name': 'group_actions', 'is_fully_enabled': True},
    ],
    CRM_ADMIN_GROUPS_V2={'all_on': True},
)
@pytest.mark.now('2022-04-05 15:00:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_efficiency_correct_group(web_app_client, web_context, stq):
    campaign_id = 35
    body = {'group_ids': [31], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 200


# ****************************************************************************


@pytest.mark.config(
    CRM_ADMIN_FEATURE_FLAGS_V2=[
        {'feature_name': 'group_actions', 'is_fully_enabled': True},
    ],
    CRM_ADMIN_GROUPS_V2={'all_on': True},
)
@pytest.mark.now('2022-04-05 15:00:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_efficiency_with_actions(web_app_client, web_context, stq):
    campaign_id = 35
    body = {'group_ids': [32], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 400
    data = await response.json()
    errors = data['errors']
    assert len(errors) == 2
    assert errors[0]['code'] == 'missing_mandatory_parameter'
    assert errors[1]['code'] == 'missing_mandatory_parameter'


# ****************************************************************************


@pytest.mark.config(
    CRM_ADMIN_FEATURE_FLAGS_V2=[
        {'feature_name': 'group_actions', 'is_fully_enabled': False},
    ],
    CRM_ADMIN_GROUPS_V2={'all_on': True},
)
@pytest.mark.now('2022-04-05 15:00:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_efficiency_with_actions_off(web_app_client, web_context, stq):
    campaign_id = 35
    body = {'group_ids': [32], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 400
    data = await response.json()
    errors = data['errors']
    assert len(errors) == 2
    assert errors[0]['code'] == 'missing_mandatory_parameter'
    assert errors[1]['code'] == 'missing_mandatory_parameter'


# ****************************************************************************


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_success_final_false(web_app_client, web_context, stq):
    campaign_id = 9
    body = {'group_ids': [9, 11, 16], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 200

    # check stq called
    assert stq.crm_admin_batch_sending.times_called == 2

    # check groups states (NEW - present)
    group_storage = group_adapters.DbGroup(web_context)
    rows = await group_storage.fetch_by_segment(9)
    states = {}
    excepted = {
        9: 'SCHEDULED',
        10: 'NEW',
        11: 'SCHEDULED',
        12: 'SENDING',
        13: 'SENT',
        16: 'HOLD',
    }
    for row in rows:
        states[row.group_id] = row.params.state

    assert states == excepted


# ****************************************************************************


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_success_final_true(web_app_client, web_context, stq):
    campaign_id = 9
    body = {'group_ids': [9, 11, 16], 'final': True}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 200

    # check stq called
    assert stq.crm_admin_batch_sending.times_called == 2

    # check groups states (NEW - present)
    group_storage = group_adapters.DbGroup(web_context)
    rows = await group_storage.fetch_by_segment(9)
    states = {}
    excepted = {
        9: 'SCHEDULED',
        10: 'HOLD',
        11: 'SCHEDULED',
        12: 'SENDING',
        13: 'SENT',
        16: 'HOLD',
    }
    for row in rows:
        states[row.group_id] = row.params.state

    assert states == excepted


# ****************************************************************************


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_group_from_other_campaign(web_app_client, web_context):
    campaign_id = 4
    body = {'group_ids': [8], 'final': True}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 424
    body = await response.json()
    assert body['message'] == 'Group 8 has invalid segment_id. 8 != 4.'


# ****************************************************************************


@pytest.mark.now('2021-04-05 16:00:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_eff_group_status_after_processing(
        web_app_client, web_context, patch,
):
    campaign_id = 11
    group_id = 17
    body = {'group_ids': [group_id], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    group_storage = group_adapters.DbGroup(web_context)
    group = await group_storage.fetch(
        group_id=group_id, campaign_id=campaign_id,
    )

    assert response.status == 200
    assert group.params.state == settings.GROUP_STATE_EFFICIENCY_PLANNED


# ****************************************************************************


@pytest.mark.now('2021-04-05 16:00:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_group_status_after_processing(web_app_client, web_context):
    campaign_id = 10
    group_id = 14
    body = {'group_ids': [group_id], 'final': False}

    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )
    group_storage = group_adapters.DbGroup(web_context)
    group = await group_storage.fetch(
        group_id=group_id, campaign_id=campaign_id,
    )

    assert response.status == 200
    assert group.params.state == settings.GROUP_STATE_PLANNED


# ****************************************************************************


@pytest.mark.now('2021-05-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_user_login(web_app_client, web_context, stq, patch):
    # pylint: disable=unused-variable,
    @patch('crm_admin.utils.validation.serializers.process_campaign_errors')
    async def process_campaign_errors(
            context, campaign_id, user_login, *args, **kwargs,
    ):
        assert user_login == 'test'

    campaign_id = 4
    body = {'group_ids': [8], 'final': True}
    await web_app_client.post(
        '/v1/process/send',
        params={'id': campaign_id},
        json=body,
        headers={'X-Yandex-Login': 'test'},
    )


# ****************************************************************************


@pytest.mark.now('2021-04-07 13:00:00')
@pytest.mark.parametrize('campaign_id, group_id', [[12, 18], [13, 19]])
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_holding_group(
        web_app_client, web_context, campaign_id, group_id,
):
    body = {'group_ids': [group_id], 'final': False}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    async with web_context.pg.master_pool.acquire() as conn:
        group_storage = group_adapters.DbGroup(web_context, conn)
        group = await group_storage.fetch(
            group_id=group_id, campaign_id=campaign_id,
        )

        campaign_storage = campaign_adapters.DbCampaign(web_context, conn)
        campaign = await campaign_storage.fetch(campaign_id)

    assert response.status == 200
    assert group.params.state == settings.GROUP_STATE_HOLD
    assert campaign.state == settings.SENDING_RESULT_STATE


# ****************************************************************************


@pytest.mark.now('2022-02-09 20:00:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_eff_group_status_after_processing_recalculate(
        web_app_client, web_context, patch,
):
    @patch('crm_admin.utils.stq_tasks.start_calculations_processing')
    async def start_calculations_processing(*args, **kwargs):
        pass

    campaign_id = 123
    group_id = 20
    body = {'group_ids': [group_id], 'final': False, 'recalculate': True}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 200
    assert start_calculations_processing.calls


# ****************************************************************************


@pytest.mark.now('2022-02-09 20:00:00')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_send_with_recalculate_error_exist_sending(
        web_app_client, web_context, patch,
):
    @patch('crm_admin.utils.stq_tasks.start_calculations_processing')
    async def start_calculations_processing(*args, **kwargs):
        pass

    campaign_id = 1234
    group_id = 21
    body = {'group_ids': [group_id], 'final': False, 'recalculate': True}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 424
    assert not start_calculations_processing.calls
    body = await response.json()
    assert (
        body['message']
        == 'Cannot to recalculate because there is already a sending.'
    )


# ****************************************************************************


@pytest.mark.now('2022-02-22 16:00:00')
@pytest.mark.config(CRM_ADMIN_RECALCULATION_INTERVAL=120)
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
@pytest.mark.parametrize(
    ['campaign_id', 'group_ids', 'eta'],
    [
        pytest.param(
            33, [22], None, id='not delay send, without efficiency datetime',
        ),
        pytest.param(
            33,
            [23],
            FakeDatetime(2022, 3, 24, 18, 0),
            id='delay send, without efficiency datetime',
        ),
        pytest.param(
            33,
            [24],
            None,
            id=(
                'delay send with date less than RC, '
                'without efficiency datetime'
            ),
        ),
        pytest.param(
            33,
            [22, 23],
            None,
            id=(
                'one group delay, one not delay, '
                'without efficiency datetime'
            ),
        ),
        pytest.param(
            34,
            [25],
            FakeDatetime(2022, 3, 24, 17, 0),
            id='not delay send, with efficiency datetime',
        ),
        pytest.param(
            34,
            [26],
            FakeDatetime(2022, 3, 24, 17, 0),
            id='delay send, with efficiency datetime',
        ),
        pytest.param(
            34,
            [27],
            FakeDatetime(2022, 3, 24, 17, 0),
            id=(
                'delay send with date less than RC '
                '(value from config), with efficiency datetime'
            ),
        ),
        pytest.param(
            34,
            [25, 26],
            FakeDatetime(2022, 3, 24, 17, 0),
            id='one group delay, one not delay, with efficiency datetime',
        ),
        pytest.param(
            34,
            [28],
            None,
            id='efficiency datetime less than RC (value from config)',
        ),
    ],
)
async def test_recalculate_before_send(
        web_app_client, web_context, patch, campaign_id, group_ids, eta,
):
    @patch('crm_admin.utils.stq_tasks.start_calculations_processing')
    async def start_calculations_processing(*args, **kwargs):
        assert kwargs['eta'] == eta

    body = {'group_ids': group_ids, 'final': False, 'recalculate': True}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 200
    assert start_calculations_processing.calls


@pytest.mark.now('2022-04-12 16:00:00')
@pytest.mark.config(CRM_ADMIN_RECALCULATION_INTERVAL=120)
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_send_with_recalculate_error_expired_campaign(
        web_app_client, web_context, patch,
):
    """
        Campaign 1234 active in
        ['2022-02-04 13:00:00', '2022-04-12 17:00:00']
        if try to send with recalculation in 2022-04-12 16:00:00,
        send validation should return error
    """

    @patch('crm_admin.utils.stq_tasks.start_calculations_processing')
    async def start_calculations_processing(*args, **kwargs):
        pass

    campaign_id = 1234
    group_id = 21
    body = {'group_ids': [group_id], 'final': False, 'recalculate': True}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 400
    assert not start_calculations_processing.calls
    body = await response.json()
    assert body == {
        'errors': [
            {'code': 'campaign_efficiency_stop_time_expired'},
            {
                'code': 'group_efficiency_expired',
                'details': {
                    'entity_id': '21',
                    'entity_name': 'UserGroup',
                    'entity_type': 'group',
                },
            },
        ],
    }


@pytest.mark.config(CRM_ADMIN_GROUPS_V2={'all_on': True})
@pytest.mark.now('2022-03-05 05:05:05')
@pytest.mark.pgsql('crm_admin', files=['prepare_campaign.sql'])
async def test_promocode_success_final_true(
        web_app_client, web_context, stq, patch,
):
    @patch(
        'crm_admin.utils.validation.group_validators.'
        'promocode_series_validation',
    )
    async def group_update_validation(*args, **kwargs):
        return []

    campaign_id = 36
    body = {'group_ids': [1, 2], 'final': True}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': campaign_id}, json=body,
    )

    assert response.status == 200

    # check stq called
    assert stq.crm_admin_batch_sending.times_called == 2

    # check groups states (NEW - present)
    group_storage = group_adapters.DbGroup(web_context)
    rows = await group_storage.fetch_by_segment(campaign_id)
    states = {}
    excepted = {1: 'SCHEDULED', 2: 'SCHEDULED'}
    for row in rows:
        states[row.group_id] = row.params.state

    assert states == excepted
