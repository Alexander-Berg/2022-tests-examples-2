# pylint: disable=import-only-modules
# pylint: disable=redefined-outer-name
# pylint: disable=line-too-long
# flake8: noqa: E501

import datetime

import dateutil.parser
import pytest

from tests_crm_scheduler.utils import read_count
from tests_crm_scheduler.utils import select_columns_from_table


CAMPAIGN1_ID, GROUP1_ID = 123, 456
CAMPAIGN2_ID, GROUP2_ID = 987, 654


def crm_admin_response(using_timezone_for_date, using_timezone_for_daytime):
    return {
        'campaigns': [
            {
                'campaign_id': 9188,
                'groups': [
                    {
                        'group_id': 20744,
                        'allowed_time_scope': {
                            'start_scope_time': '2022-07-14T11:08:00+03:00',
                            'end_scope_time': '2022-07-14T13:08:00+03:00',
                            'start_time_sec': 75600,
                            'stop_time_sec': 161940,
                            'using_timezone_for_date': False,
                            'using_timezone_for_daytime': False,
                        },
                    },
                ],
            },
            {
                'campaign_id': 8902,
                'groups': [
                    {
                        'group_id': 20150,
                        'allowed_time_scope': {
                            'start_scope_time': (
                                '2022-07-01T14:25:21.169000+03:00'
                            ),
                            'end_scope_time': (
                                '2022-07-04T22:30:34.169000+03:00'
                            ),
                            'start_time_sec': 20 * 60 * 60,
                            'stop_time_sec': (21 * 60 * 60 - 1),
                            'using_timezone_for_date': False,
                            'using_timezone_for_daytime': False,
                        },
                    },
                ],
            },
            {
                'campaign_id': 8898,
                'groups': [
                    {
                        'group_id': 20125,
                        'allowed_time_scope': {
                            'start_scope_time': (
                                '2022-07-01T10:59:28.932000+03:00'
                            ),
                            'end_scope_time': (
                                '2022-07-04T19:00:32.932000+03:00'
                            ),
                            'start_time_sec': 36000,
                            'stop_time_sec': 64800,
                            'using_timezone_for_date': False,
                            'using_timezone_for_daytime': False,
                        },
                    },
                ],
            },
            {
                'campaign_id': 8822,
                'groups': [
                    {
                        'group_id': 19911,
                        'allowed_time_scope': {
                            'start_scope_time': (
                                '2022-07-01T10:59:28.932000+03:00'
                            ),
                            'end_scope_time': (
                                '2022-07-01T19:00:32.932000+03:00'
                            ),
                            'start_time_sec': 13 * 60 * 60,
                            'stop_time_sec': 18 * 60 * 60,
                            'using_timezone_for_date': False,
                            'using_timezone_for_daytime': False,
                        },
                    },
                ],
            },
            {
                'campaign_id': 8820,
                'groups': [
                    {
                        'group_id': 19905,
                        'allowed_time_scope': {
                            'start_scope_time': (
                                '2022-06-29T04:53:22.607000+03:00'
                            ),
                            'end_scope_time': (
                                '2022-07-03T23:00:00.349000+03:00'
                            ),
                            'start_time_sec': (11 * 60 + 40) * 60,
                            'stop_time_sec': (20 * 60 + 59) * 60,
                            'using_timezone_for_date': False,
                            'using_timezone_for_daytime': False,
                        },
                    },
                ],
            },
            {
                'campaign_id': CAMPAIGN1_ID,
                'groups': [
                    {
                        'group_id': GROUP1_ID,
                        'allowed_time_scope': {
                            'start_scope_time': '2021-12-14T10:00:00Z',
                            'end_scope_time': '2022-12-10T10:00:00Z',
                            'using_timezone_for_date': using_timezone_for_date,
                            'start_time_sec': 8 * 60 * 60,
                            'stop_time_sec': 18 * 60 * 60,
                            'using_timezone_for_daytime': (
                                using_timezone_for_daytime
                            ),
                        },
                    },
                ],
            },
            {
                'campaign_id': CAMPAIGN2_ID,
                'groups': [
                    {
                        'group_id': GROUP2_ID,
                        'allowed_time_scope': {
                            'start_scope_time': '2021-10-01T12:00:00Z',
                            'end_scope_time': '2021-10-31T15:00:00Z',
                            'using_timezone_for_date': using_timezone_for_date,
                            'start_time_sec': 10 * 60 * 60,
                            'stop_time_sec': 18 * 60 * 60,
                            'using_timezone_for_daytime': (
                                using_timezone_for_daytime
                            ),
                        },
                    },
                ],
            },
        ],
        'actual_ts': '2021-12-14T14:00:00Z',
    }


@pytest.fixture(name='crm_admin_get_list_mock_with_tz')
def crm_admin_get_list_mock_with_tz(mockserver):
    @mockserver.json_handler('/crm-admin/v1/campaigns/meta/list')
    def _mock_crm_admin(request):
        return crm_admin_response(True, True)


@pytest.fixture(name='crm_admin_get_list_mock_without_tz')
# pylint: disable=invalid-name
def crm_admin_get_list_mock_without_tz(mockserver):
    @mockserver.json_handler('/crm-admin/v1/campaigns/meta/list')
    def _mock_crm_admin(request):
        return crm_admin_response(False, False)


def generate_payload(task_id, allowed, logs_saved=None):
    ret = {
        'task_id': task_id,
        'new_state': 'ok',
        'filter_approved': allowed,
        'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
    }
    if logs_saved:
        ret['logs_saved'] = logs_saved
    return ret


def admin_get_meta_list_response(
        using_timezone_for_date=True, using_timezone_for_daytime=True,
):
    return {
        'campaigns': [
            {
                'campaign_id': CAMPAIGN1_ID,
                'groups': [
                    {
                        'group_id': GROUP1_ID,
                        'allowed_time_scope': {
                            'start_scope_time': '2021-12-14T10:00:00Z',
                            'end_scope_time': '2022-12-10T10:00:00Z',
                            'using_timezone_for_date': using_timezone_for_date,
                            'start_time_sec': 8 * 60 * 60,
                            'stop_time_sec': 18 * 60 * 60,
                            'using_timezone_for_daytime': (
                                using_timezone_for_daytime
                            ),
                        },
                    },
                ],
            },
            {
                'campaign_id': CAMPAIGN2_ID,
                'groups': [
                    {
                        'group_id': GROUP2_ID,
                        'allowed_time_scope': {
                            'start_scope_time': '2021-10-01T12:00:00Z',
                            'end_scope_time': '2021-10-31T15:00:00Z',
                            'using_timezone_for_date': using_timezone_for_date,
                            'start_time_sec': 10 * 60 * 60,
                            'stop_time_sec': 18 * 60 * 60,
                            'using_timezone_for_daytime': (
                                using_timezone_for_daytime
                            ),
                        },
                    },
                ],
            },
        ],
        'actual_ts': '2021-12-14T14:00:00Z',
    }


EXPECTED_SENDINGS = {
    (CAMPAIGN1_ID, GROUP1_ID): [
        {
            'work_date_start': datetime.datetime(2021, 12, 14, 10, 0),
            'work_date_finish': datetime.datetime(2022, 12, 10, 10, 0),
            'work_time_start': 8 * 60 * 60,
            'work_time_finish': 18 * 60 * 60,
        },
    ],
    (CAMPAIGN2_ID, GROUP2_ID): [
        {
            'work_date_start': datetime.datetime(2021, 10, 1, 12, 0),
            'work_date_finish': datetime.datetime(2021, 10, 31, 15, 0),
            'work_time_start': 10 * 60 * 60,
            'work_time_finish': 18 * 60 * 60,
        },
    ],
}


@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': False,
    },
)
@pytest.mark.parametrize(
    ('success', 'now', 'campaign_id', 'group_id'),
    [
        # fmt: off
        pytest.param(True, '2020-04-21T12:17:42+00:00', CAMPAIGN1_ID, GROUP1_ID, id='communication_will_be_actual'),
        pytest.param(True, '2021-12-31T11:00+00:00', CAMPAIGN1_ID, GROUP1_ID, id='communication_is_actual'),
        pytest.param(False, '2022-12-31T11:00+00:00', CAMPAIGN1_ID, GROUP1_ID, id='communication_has_expired_A'),
        pytest.param(False, '2021-10-31T15:01:42+00:00', CAMPAIGN2_ID, GROUP2_ID, id='communication_has_expired_B'),
        pytest.param(True, '2021-10-31T14:29:42+00:00', CAMPAIGN2_ID, GROUP2_ID, id='communication_is_valid_B'),
        # fmt: on
    ],
)
async def test_crm_admin_check_work_time_on_registry_api1(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        success,
        now,
        group_id,
        campaign_id,
        crm_admin_get_list_mock_with_tz,
):
    now = dateutil.parser.parse(now)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=True)

    response = await taxi_crm_scheduler.put(
        '/v1/register_communiction_to_send',
        params={
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': campaign_id,
            'channel_type': 'driver_push',
            'group_id': group_id,
            'policy_enabled': True,
            'send_enabled': True,
            'company_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
        },
    )

    if not success:
        assert response.status == 400
        return

    assert response.status == 200

    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'work_date_start',
            'work_date_finish',
            'work_time_start',
            'work_time_finish',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == EXPECTED_SENDINGS[(campaign_id, group_id)]


@pytest.mark.pgsql(
    'crm_scheduler', files=['create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': False,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.parametrize(
    ('success', 'now', 'campaign_id', 'group_id'),
    [
        # fmt: off
        pytest.param(True, '2020-04-21T12:17:42+00:00', CAMPAIGN1_ID, GROUP1_ID, id='communication_will_be_actual'),
        pytest.param(True, '2021-12-31T11:00+00:00', CAMPAIGN1_ID, GROUP1_ID, id='communication_is_actual'),
        pytest.param(False, '2022-12-31T11:00+00:00', CAMPAIGN1_ID, GROUP1_ID, id='communication_has_expired_A'),
        pytest.param(False, '2021-10-31T15:01:42+00:00', CAMPAIGN2_ID, GROUP2_ID, id='communication_has_expired_B'),
        pytest.param(True, '2021-10-31T14:29:42+00:00', CAMPAIGN2_ID, GROUP2_ID, id='communication_is_valid_B'),
        # fmt: on
    ],
)
async def test_crm_admin_check_work_time_on_registry_api2(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        success,
        now,
        group_id,
        campaign_id,
        crm_admin_get_list_mock_with_tz,
):
    now = dateutil.parser.parse(now)
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=True)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': str(campaign_id),
            'group_id': str(group_id),
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_push',
            'steps': ['crm_policy', 'eda_push', 'driver_push', 'logs'],
        },
    )
    if not success:
        assert response.status == 400
        return

    assert response.status == 200
    sendings = select_columns_from_table(
        'crm_scheduler.sendings',
        [
            'work_date_start',
            'work_date_finish',
            'work_time_start',
            'work_time_finish',
        ],
        pgsql['crm_scheduler'],
        1000,
    )
    assert sendings == EXPECTED_SENDINGS[(campaign_id, group_id)]


async def helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        timezone_name,
        now,
        group_id=GROUP1_ID,
        campaign_id=CAMPAIGN1_ID,
):
    mocked_time.set(now)

    await taxi_crm_scheduler.invalidate_caches(clean_update=True)

    response = await taxi_crm_scheduler.post(
        '/v2/register_communiction_to_send',
        {
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': str(campaign_id),
            'group_id': str(group_id),
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'policy_step_channel': 'driver_push',
            'steps': ['crm_policy', 'eda_push', 'driver_push', 'logs'],
            'timezone_name': timezone_name,
        },
    )
    if expired:
        assert response.status == 400
        return
    assert response.status == 200
    assert read_count(pgsql, 'sendings') == 1
    assert read_count(pgsql, 'task_pool_crm_policy') == 0
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    expected_tasks_in_pool = 1 if in_time else 0
    assert read_count(pgsql, 'task_pool_crm_policy') == expected_tasks_in_pool


@pytest.mark.pgsql(
    'crm_scheduler',
    files=['drop_sequence.sql', 'create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
# For Moscow offset is +3 but TZ name can be Etc/GMT-3,
# please look https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
@pytest.mark.parametrize(
    ('expired', 'in_time', 'timezone_name'),
    [
        # fmt: off
        pytest.param(False, True, 'Etc/GMT-6', id='Nonlocal early evening'),
        pytest.param(False, True, 'Etc/GMT-7', id='Nonlocal late evening'),
        pytest.param(False, True, 'Etc/GMT-3', id='Nonlocal late morning'),
        pytest.param(False, True, 'Europe/Moscow', id='Moscow::Nonlocal late morning'),
        pytest.param(False, True, 'Etc/GMT+4', id='Nonlocal early morning'),
        # fmt: on
    ],
)
async def test_time_zone_api_v2(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        crm_admin_get_list_mock_without_tz,
        timezone_name,
):
    now = dateutil.parser.parse('2022-01-12T11:17:42+00:00')
    await helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        timezone_name,
        now,
    )


@pytest.mark.pgsql(
    'crm_scheduler',
    files=['drop_sequence.sql', 'create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 2,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.parametrize(
    ('expired', 'in_time', 'timezone_name'),
    [
        # fmt: off
        pytest.param(False, True, 'Etc/GMT-6', id='Nonlocal early evening'),  # UTC +6
        pytest.param(False, True, 'Asia/Shanghai', id='Beijing:Nonlocal early evening'),  # UTC +5
        pytest.param(False, True, 'Etc/GMT+7', id='Nonlocal late evening'),
        pytest.param(False, True, 'Etc/GMT+3', id='Nonlocal late morning'),
        pytest.param(False, True, 'Etc/GMT+4', id='Nonlocal early morning'),
        # fmt: on
    ],
)
async def test_time_zone_api_v1(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        crm_admin_get_list_mock_without_tz,
        timezone_name,
):
    now = dateutil.parser.parse('2022-01-12T11:17:42+00:00')
    mocked_time.set(now)
    group_id = GROUP1_ID
    campaign_id = CAMPAIGN1_ID

    await taxi_crm_scheduler.invalidate_caches(clean_update=True)

    response = await taxi_crm_scheduler.put(
        '/v1/register_communiction_to_send',
        params={
            'size': 123,
            'sending_id': '7d27b35a-0032-11ec-9a03-0242ac130003',
            'campaign_id': str(campaign_id),
            'group_id': str(group_id),
            'channel_type': 'user_push',
            'policy_enabled': True,
            'send_enabled': True,
            'sending_dependency_uuid': '8430b07a-0032-11ec-9a03-0242ac130003',
            'timezone_name': timezone_name,
        },
    )
    if expired:
        assert response.status == 400
        return
    assert response.status == 200
    assert read_count(pgsql, 'sendings') == 1
    assert read_count(pgsql, 'task_pool_crm_policy') == 0
    await taxi_crm_scheduler.run_periodic_task('task-generator-periodic')
    expected_tasks_in_pool = 1 if in_time else 0
    assert read_count(pgsql, 'task_pool_crm_policy') == expected_tasks_in_pool


@pytest.mark.pgsql(
    'crm_scheduler',
    files=['drop_sequence.sql', 'create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.parametrize(
    ('expired', 'in_time', 'timezone_name'),
    [
        # fmt: off
        pytest.param(False, False, 'Etc/GMT+4', id='Local early morning'),
        pytest.param(False, True, 'Europe/Moscow', id='Local late morning'),
        pytest.param(False, True, 'Etc/GMT+3', id='Moscow Local late morning'),
        pytest.param(False, True, 'Etc/GMT-6', id='Local early evening'),
        pytest.param(False, False, 'Etc/GMT-7', id='Local late evening'),
        # fmt: on
    ],
)
async def test_time_zone_api_v2_with_tz(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        crm_admin_get_list_mock_with_tz,
        timezone_name,
):
    now = dateutil.parser.parse('2022-01-12T11:17:42+00:00')
    await helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        timezone_name,
        now,
    )


@pytest.mark.pgsql(
    'crm_scheduler',
    files=['drop_sequence.sql', 'create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.parametrize(
    ('expired', 'in_time', 'timezone_name'),
    [
        # fmt: off
        pytest.param(True, None, 'Etc/GMT-7', id='Expired at the east'),
        pytest.param(False, True, 'Etc/GMT-3', id='Not expired in Moscow'),
        # fmt: on
    ],
)
async def test_early_expiration_at_the_east(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        crm_admin_get_list_mock_with_tz,
        timezone_name,
):
    now = dateutil.parser.parse('2022-12-10T6:00:00Z')
    await helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        timezone_name,
        now,
    )


@pytest.mark.pgsql(
    'crm_scheduler',
    files=['drop_sequence.sql', 'create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
@pytest.mark.parametrize(
    ('expired', 'in_time', 'timezone_name'),
    [
        # fmt: off
        pytest.param(False, False, 'Etc/GMT-7', id='Not expired at the east'),
        pytest.param(False, False, 'Etc/GMT-3', id='Not expired in Moscow'),
        # fmt: on
    ],
)
async def test_no_early_expiration_without_timezone(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        crm_admin_get_list_mock_without_tz,
        timezone_name,
):
    now = dateutil.parser.parse('2022-12-10T6:00:00Z')
    await helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        timezone_name,
        now,
    )


@pytest.mark.pgsql(
    'crm_scheduler',
    files=['drop_sequence.sql', 'create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
async def test_bit_early_in_msk(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock_without_tz,
):
    expired = False
    in_time = False
    timezone_name = 'Europe/Moscow'
    now = dateutil.parser.parse('2022-06-30T13:50:00+03:00')
    await helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired=expired,
        in_time=in_time,
        timezone_name=timezone_name,
        now=now,
        group_id=19905,
        campaign_id=8820,
    )


@pytest.mark.pgsql(
    'crm_scheduler',
    files=['drop_sequence.sql', 'create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
async def test_group_19911(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock_without_tz,
):
    expired = False
    in_time = True
    timezone_name = 'Europe/Moscow'
    now = dateutil.parser.parse('2022-07-01T17:05:00+03:00')
    await helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired=expired,
        in_time=in_time,
        timezone_name=timezone_name,
        now=now,
        group_id=19911,
        campaign_id=8822,
    )


@pytest.mark.pgsql(
    'crm_scheduler',
    files=['drop_sequence.sql', 'create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
async def test_group_20125(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock_without_tz,
):
    expired = False
    in_time = True
    timezone_name = 'Europe/Moscow'
    now = dateutil.parser.parse('2022-07-04T18:42:00+03:00')

    await helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired=expired,
        in_time=in_time,
        timezone_name=timezone_name,
        now=now,
        group_id=20125,
        campaign_id=8898,
    )


@pytest.mark.pgsql(
    'crm_scheduler',
    files=['drop_sequence.sql', 'create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
async def test_group_20150(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock_without_tz,
):
    expired = True
    in_time = False
    timezone_name = 'Europe/Moscow'
    now = dateutil.parser.parse('2022-07-04T19:42:00+03:00')
    await helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired=expired,
        in_time=in_time,
        timezone_name=timezone_name,
        now=now,
        group_id=20150,
        campaign_id=8902,
    )


@pytest.mark.pgsql(
    'crm_scheduler',
    files=['drop_sequence.sql', 'create_channels_and_priorities_default.sql'],
)
@pytest.mark.config(
    CRM_SCHEDULER_WORK_TIME={
        'check_work_time_on_registration': True,
        'check_work_time_on_generation': True,
    },
    CRM_SCHEDULER_GENERATION_V5={
        'generate_period_in_seconds': 60,
        'workers_period_in_seconds': 20,
        'send_wait_period_in_seconds': 120,
        'logs_wait_period_in_seconds': 120,
        'generation_version': 3,
        'policy_allowance_in_seconds': 1000,
    },
)
async def test_group_20744(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        crm_admin_get_list_mock_without_tz,
):
    expired = False
    in_time = True
    timezone_name = 'Europe/Moscow'
    now = dateutil.parser.parse('2022-07-14T11:42:00+03:00')
    await helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired=expired,
        in_time=in_time,
        timezone_name=timezone_name,
        now=now,
        group_id=20744,
        campaign_id=9188,
    )
