# pylint: disable=W0212

import datetime

import pandas as pd
import pytest

from crm_admin import entity
from crm_admin import error_codes
from crm_admin import settings
from crm_admin import storage
from crm_admin.audience.utils import verify_utils
from crm_admin.stq import batch_verify
from crm_admin.utils import kibana
from crm_admin.utils import verify


NOW = datetime.datetime(2000, 1, 1, 1, 1, 1)


class TaskInfo:
    id = 'task_id'  # pylint: disable=invalid-name
    exec_tries = 0


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize(
    'campaign_id, group_id, group_params, expected_result',
    [
        (1, 1, {'channel': 'PUSH', 'content': 'content'}, True),
        (
            1,
            1,
            {
                'channel': 'promo.fs',
                'content': 'content',
                'days_count': 10,
                'time_until': '10:10',
            },
            True,
        ),
        (
            1,
            1,
            {
                'channel': 'promo.notification',
                'content': 'content',
                'days_count': 11,
                'time_until': '11:11',
            },
            True,
        ),
        (
            1,
            1,
            {
                'channel': 'promo.card',
                'content': 'content',
                'days_count': 12,
                'time_until': '12:12',
            },
            True,
        ),
        (1, 1, {'channel': 'PUSH'}, False),
        (1, 1, {'channel': 'promo.fs'}, False),
        (1, 1, {'channel': 'promo.notification'}, False),
        (1, 1, {'channel': 'promo.card'}, False),
        (2, 1, {'channel': 'PUSH', 'content': 'content'}, True),
        (2, 1, {'channel': 'SMS', 'content': 'content'}, True),
        (
            2,
            1,
            {
                'channel': 'LEGACYWALL',
                'feed_id': 'feed_id',
                'days_count': 20,
                'time_until': '20:20',
            },
            True,
        ),
        (2, 1, {'channel': 'PUSH'}, False),
        (2, 1, {'channel': 'SMS'}, False),
        (2, 1, {'channel': 'LEGACYWALL'}, False),
    ],
)
async def test_pre_check_groups(
        stq3_context, campaign_id, group_id, group_params, expected_result,
):
    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)

    db_group = storage.DbGroup(stq3_context)
    group = await db_group.fetch(group_id)
    for key, val in group_params.items():
        setattr(group.params, key, val)
    await db_group.update(group)

    result, _ = await verify.pre_check(stq3_context, campaign, [group_id])
    assert result == expected_result


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize('campaign_id', [3, 4, 5])
async def test_stop_verify_campaign_finished(stq3_context, patch, campaign_id):
    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)

    @patch('crm_admin.utils.log_util.LoggerAdapter.warning')
    def logger_warning(*args, **kwargs):
        pass

    campaign = await db_campaign.fetch(campaign_id)
    await verify.create_verification_sending([], stq3_context, campaign)

    logger_warning_args = logger_warning.calls[0]['args']

    assert logger_warning_args[0] == 'Stop verify: campaign state = %s'
    assert logger_warning_args[1] == campaign.state


@pytest.mark.parametrize(
    'cmp_id, row_type, excepted_data',
    [
        (
            1,
            'int64',
            {
                'data': {0: 16, 1: 16, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
                'group_id': {
                    0: 'default',
                    1: 'default',
                    2: '1_test',
                    3: '1_test',
                    4: '2_test',
                    5: '2_test',
                    6: '3_test',
                    7: '3_test',
                },
                'group_name': {
                    0: 'Default',
                    1: 'Default',
                    2: 'group_1',
                    3: 'group_1',
                    4: 'group_2',
                    5: 'group_2',
                    6: 'group_3',
                    7: 'group_3',
                },
            },
        ),
        (
            2,
            'int64',
            {
                'data': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
                'group_id': {
                    0: 'default',
                    1: 'default',
                    2: '1_test',
                    3: '1_test',
                    4: '2_test',
                    5: '2_test',
                    6: '3_test',
                    7: '3_test',
                },
                'group_name': {
                    0: 'Default',
                    1: 'Default',
                    2: 'group_1',
                    3: 'group_1',
                    4: 'group_2',
                    5: 'group_2',
                    6: 'group_3',
                    7: 'group_3',
                },
            },
        ),
    ],
)
@pytest.mark.yt(
    static_table_data=[
        'yt_cmp_1_verification_clean.yaml',
        'yt_cmp_2_verification_clean.yaml',
    ],
)
async def test_nulls_in_integer_columns(
        yt_apply, stq3_context, cmp_id, row_type, excepted_data,
):
    # pylint: disable=protected-access
    hahn = stq3_context.yt_wrapper.get_client('hahn')

    out_path = f'//home/taxi-crm/robot-crm-admin/cmp_{cmp_id}_verification'
    in_path = out_path + '_clean'

    table = await verify._read_table(hahn, in_path)
    users = filter(None, {'db_id': 'db_id', 'driver_uuid': 'driver_uuid'})
    users = pd.DataFrame(users)  # type: ignore

    await verify._create_verification_table(
        hahn, in_path, out_path, table, users,
    )

    table = pd.DataFrame(await hahn.read_table(out_path))
    assert str(table.dtypes['data']) == row_type

    assert table.to_dict() == excepted_data


# =============================================================================


@pytest.mark.config(CRM_ADMIN_GROUPS_V2={'all_on': True})
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize(
    'campaign_id, groups_id_list', [(6, [3, 4, 5]), (7, [3, 4]), (8, [5])],
)
async def test_error_verification_gen_table(
        stq3_context, patch, campaign_id, groups_id_list,
):
    user_ids = ['1', '2', '3']
    reason = verify_utils.UserErrorReason.USERS_NOT_FOUND
    db_campaign = storage.DbCampaign(context=stq3_context)

    @patch('crm_admin.utils.verify._gen_verification_table')
    async def _gen_verification_table(*args, **kwargs):
        raise verify_utils.UserRetrievalError(reason=reason, user_ids=user_ids)

    db_group = storage.DbGroup(context=stq3_context)
    groups = await db_group.fetch_by_campaign_id(campaign_id)

    for group in groups:
        group.params.state = settings.GROUP_STATE_TESTING
        await db_group.update(group)

    campaign = await db_campaign.fetch(campaign_id)
    await verify.create_verification_sending(
        context=stq3_context, groups_id_list=groups_id_list, campaign=campaign,
    )

    assert _gen_verification_table.calls

    groups = await db_group.fetch_by_campaign_id(campaign_id)
    for group in groups:
        if group.group_id in groups_id_list:
            assert group.params.state == settings.GROUP_STATE_NEW
        else:
            assert group.params.state == settings.GROUP_STATE_TESTING

    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.VERIFY_ERROR
    assert campaign.error_code == error_codes.VERIFY_USER_NOT_FOUND
    assert campaign.error_description == {
        'kibana': kibana.make_url(
            f'ngroups:taxi_crm-admin*'
            f' and stq_task_id:campaign_{campaign.campaign_id}_verify*',
        ),
        'reason': reason.value,
        'values': ' '.join(user_ids),
        'error_msg': verify_utils.UserRetrievalError._error_msg,
    }


# =============================================================================


@pytest.mark.config(CRM_ADMIN_GROUPS_V2={'all_on': True})
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize(
    'campaign_id, groups_id_list', [(6, [3, 4, 5]), (7, [3, 4]), (8, [5])],
)
async def test_error_create_verification_sending(
        stq3_context, patch, campaign_id, groups_id_list,
):
    reason = 'test error'
    db_campaign = storage.DbCampaign(context=stq3_context)

    @patch('crm_admin.utils.verify.create_verification_sending')
    async def _create_verification_sending(*args, **kwargs):
        raise entity.InvalidCampaign(reason)

    db_group = storage.DbGroup(context=stq3_context)
    groups = await db_group.fetch_by_campaign_id(campaign_id)

    for group in groups:
        group.params.state = settings.GROUP_STATE_TESTING
        await db_group.update(group)

    await batch_verify.task(
        context=stq3_context,
        task_info=TaskInfo(),
        campaign_id=campaign_id,
        groups_id_list=groups_id_list,
    )

    assert _create_verification_sending.calls

    groups = await db_group.fetch_by_campaign_id(campaign_id)
    for group in groups:
        if group.group_id in groups_id_list:
            assert group.params.state == settings.GROUP_STATE_NEW
        else:
            assert group.params.state == settings.GROUP_STATE_TESTING

    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.VERIFY_ERROR
    assert campaign.error_code == error_codes.VERIFICATION_FAILED
    assert campaign.error_description == {
        'kibana': kibana.make_url(
            f'ngroups:taxi_crm-admin*'
            f' and stq_task_id:campaign_{campaign.campaign_id}_verify*',
        ),
        'error_msg': reason,
    }


# =============================================================================
