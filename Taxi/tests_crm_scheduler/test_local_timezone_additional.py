# pylint: disable=import-only-modules
# pylint: disable=redefined-outer-name
# pylint: disable=line-too-long
# flake8: noqa: E501
import dateutil.parser
import pytest

from tests_crm_scheduler.utils import read_count


@pytest.fixture(name='crm_admin_get_list_mock')
def crm_admin_get_list_mock(mockserver):
    @mockserver.json_handler('/crm-admin/v1/campaigns/meta/list')
    def _mock_crm_admin(request):
        return {
            'campaigns': [
                {
                    'campaign_id': 1,
                    'groups': [
                        {
                            'group_id': 1,
                            'allowed_time_scope': {
                                'start_scope_time': '2021-10-01T12:00:00Z',
                                'end_scope_time': '2021-10-31T15:00:00Z',
                                'using_timezone_for_date': True,
                                'start_time_sec': 0 * 60 * 60,
                                'stop_time_sec': 24 * 60 * 60 - 1,
                                'using_timezone_for_daytime': True,
                            },
                        },
                        {
                            'group_id': 2,
                            'allowed_time_scope': {
                                'start_scope_time': (
                                    '2021-10-01T15:00:00+03:00'
                                ),
                                'end_scope_time': '2021-10-31T18:00:00+03:00',
                                'using_timezone_for_date': True,
                                'start_time_sec': 0 * 60 * 60,
                                'stop_time_sec': 24 * 60 * 60 - 1,
                                'using_timezone_for_daytime': True,
                            },
                        },
                    ],
                },
                {
                    'campaign_id': 2,
                    'groups': [
                        {
                            'group_id': 4,
                            'allowed_time_scope': {
                                'start_scope_time': '2021-10-01T12:00:00Z',
                                'end_scope_time': '2021-10-31T15:00:00Z',
                                'using_timezone_for_date': False,
                                'start_time_sec': 0 * 60 * 60,
                                'stop_time_sec': 24 * 60 * 60 - 1,
                                'using_timezone_for_daytime': False,
                            },
                        },
                        {
                            'group_id': 3,
                            'allowed_time_scope': {
                                'start_scope_time': (
                                    '2021-10-01T15:00:00+03:00'
                                ),
                                'end_scope_time': '2021-10-31T18:00:00+03:00',
                                'using_timezone_for_date': False,
                                'start_time_sec': 0 * 60 * 60,
                                'stop_time_sec': 24 * 60 * 60 - 1,
                                'using_timezone_for_daytime': False,
                            },
                        },
                    ],
                },
                {
                    'campaign_id': 3,
                    'groups': [
                        {
                            'group_id': 6,
                            'allowed_time_scope': {
                                'start_scope_time': '2021-10-01T12:00:00Z',
                                'end_scope_time': '2021-10-31T15:00:00Z',
                                'using_timezone_for_date': True,
                                'start_time_sec': 10 * 60 * 60,
                                'stop_time_sec': 19 * 60 * 60,
                                'using_timezone_for_daytime': True,
                            },
                        },
                        {
                            'group_id': 5,
                            'allowed_time_scope': {
                                'start_scope_time': (
                                    '2021-10-01T15:00:00+03:00'
                                ),
                                'end_scope_time': '2021-10-31T18:00:00+03:00',
                                'using_timezone_for_date': True,
                                'start_time_sec': 10 * 60 * 60,
                                'stop_time_sec': 19 * 60 * 60,
                                'using_timezone_for_daytime': True,
                            },
                        },
                    ],
                },
                {
                    'campaign_id': 4,
                    'groups': [
                        {
                            'group_id': 8,
                            'allowed_time_scope': {
                                'start_scope_time': '2021-10-01T12:00:00Z',
                                'end_scope_time': '2021-10-31T15:00:00Z',
                                'using_timezone_for_date': False,
                                'start_time_sec': 10 * 60 * 60,
                                'stop_time_sec': 19 * 60 * 60,
                                'using_timezone_for_daytime': False,
                            },
                        },
                        {
                            'group_id': 7,
                            'allowed_time_scope': {
                                'start_scope_time': (
                                    '2021-10-01T15:00:00+03:00'
                                ),
                                'end_scope_time': '2021-10-31T18:00:00+03:00',
                                'using_timezone_for_date': False,
                                'start_time_sec': 10 * 60 * 60,
                                'stop_time_sec': 19 * 60 * 60,
                                'using_timezone_for_daytime': False,
                            },
                        },
                    ],
                },
            ],
            'actual_ts': '2021-12-14T14:00:00Z',
        }


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


async def helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        timezone_name,
        now,
        campaign_id,
        group_id,
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
# for each campaign_id two groups with id = 2 * c_id and id = 2 * c_id - 1 exist
# I want to use both these groups without duplicating number of parameter lines.
@pytest.mark.parametrize('group_shift', [pytest.param(0), pytest.param(-1)])

# For Moscow offset is +3 but TZ name can be Etc/GMT-3,
# please look https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
@pytest.mark.parametrize(
    ('campaign_id', 'now', 'expired', 'in_time', 'timezone_name'),
    [
        # fmt: off
        # for campaign_id=group_id=2 timezone flags set to False so passed timezone does not affect result
        pytest.param(2, '2021-10-31T14:30:00Z', False, True, 'Etc/UTC', id='UTC, 0.5h before expiration'),
        pytest.param(2, '2021-10-31T14:30:00Z', False, True, 'Europe/Moscow', id='Msk, 0.5h before expiration'),
        pytest.param(2, '2021-10-31T14:30:00Z', False, True, 'Etc/GMT-3', id='Msk, GMT mark, 0.5h before expiration'),
        pytest.param(2, '2021-10-31T14:30:00Z', False, True, 'Etc/GMT+3', id='UTC-3, 0.5h before expiration'),
        pytest.param(2, '2021-10-31T15:30:00Z', True, None, 'Etc/UTC', id='UTC, 0.5h before expiration'),
        pytest.param(2, '2021-10-31T15:30:00Z', True, None, 'Europe/Moscow', id='Msk, 0.5h before expiration'),
        pytest.param(2, '2021-10-01T12:30:00Z', False, True, 'Etc/UTC', id='UTC, 0.5h after start'),
        pytest.param(2, '2021-10-01T12:30:00Z', False, True, 'Europe/Moscow', id='UTC, 0.5h after start'),
        pytest.param(2, '2021-10-01T11:30:00Z', False, False, 'Etc/UTC', id='UTC, 0.5h after start'),
        pytest.param(2, '2021-10-01T11:30:00Z', False, False, 'Europe/Moscow', id='UTC, 0.5h after start'),
        # for campaign_id=group_id=1 timezone flags set to True so passed timezone affects result
        pytest.param(1, '2021-10-31T14:30:00Z', False, True, 'Etc/UTC', id='UTC, 0.5h before expiration'),
        pytest.param(1, '2021-10-31T14:30:00Z', True, None, 'Europe/Moscow', id='Msk, 2.5h after expiration'),
        pytest.param(1, '2021-10-31T14:30:00Z', True, None, 'Etc/GMT-3', id='Msk, GMT mark, 0.5h before expiration'),
        pytest.param(1, '2021-10-31T14:30:00Z', False, True, 'Etc/GMT+3', id='UTC-3, 0.5h before expiration'),
        pytest.param(1, '2021-10-01T12:30:00Z', False, True, 'Etc/UTC', id='UTC, 0.5h after start'),
        pytest.param(1, '2021-10-01T12:30:00Z', False, True, 'Europe/Moscow', id='Msk, 3.5h after start'),
        pytest.param(1, '2021-10-01T12:30:00Z', False, False, 'Etc/GMT+3', id='UTC-3, 2.5h before start'),
        pytest.param(1, '2021-10-01T11:30:00Z', False, False, 'Etc/UTC', id='UTC, 0.5h before start'),
        pytest.param(1, '2021-10-01T11:30:00Z', False, True, 'Europe/Moscow', id='UTC, 2.5h after start'),
        # for campaign_id=group_id=4 timezone flags set to False so passed timezone does not affect result
        pytest.param(4, '2021-10-15T18:30:00Z', False, True, 'Etc/UTC', id='UTC, 0.5h before day end'),
        pytest.param(4, '2021-10-15T18:30:00Z', False, True, 'Europe/Moscow', id='Msk, 0.5h before day end'),
        pytest.param(4, '2021-10-15T18:30:00Z', False, True, 'Etc/GMT-3', id='Msk, GMT mark, 0.5h before day end'),
        pytest.param(4, '2021-10-15T18:30:00Z', False, True, 'Etc/GMT+3', id='UTC-3, 0.5h before day end'),
        pytest.param(4, '2021-10-15T19:30:00Z', False, False, 'Etc/UTC', id='UTC, 0.5h after day end'),
        pytest.param(4, '2021-10-15T19:30:00Z', False, False, 'Europe/Moscow', id='Msk, 0.5h after day end'),
        pytest.param(4, '2021-10-15T10:30:00Z', False, True, 'Etc/UTC', id='UTC, 0.5h after day start'),
        pytest.param(4, '2021-10-15T10:30:00Z', False, True, 'Europe/Moscow', id='UTC, 0.5h after day start'),
        pytest.param(4, '2021-10-15T9:30:00Z', False, False, 'Etc/UTC', id='UTC, 0.5h before day start'),
        pytest.param(4, '2021-10-15T9:30:00Z', False, False, 'Europe/Moscow', id='UTC, half before day start'),
        # for campaign_id=group_id=3 timezone flags set to True so passed timezone affects result
        pytest.param(3, '2021-10-15T18:30:00Z', False, True, 'Etc/UTC', id='UTC, 0.5h before day end'),
        pytest.param(3, '2021-10-15T18:30:00Z', False, False, 'Europe/Moscow', id='Msk, 2.5h after day end'),
        pytest.param(3, '2021-10-15T18:30:00Z', False, False, 'Etc/GMT-3', id='Msk, GMT mark, 2.5h before day end'),
        pytest.param(3, '2021-10-15T18:30:00Z', False, True, 'Etc/GMT+3', id='UTC-3, 3.5h before day end'),
        pytest.param(3, '2021-10-15T19:30:00Z', False, False, 'Etc/UTC', id='UTC, 0.5h after day end'),
        pytest.param(3, '2021-10-15T19:30:00Z', False, False, 'Europe/Moscow', id='Msk, 3.5h after day end'),
        pytest.param(3, '2021-10-15T10:30:00Z', False, True, 'Etc/UTC', id='UTC, 0.5h after day start'),
        pytest.param(3, '2021-10-15T10:30:00Z', False, True, 'Europe/Moscow', id='UTC, 3.5h after day start'),
        pytest.param(3, '2021-10-15T9:30:00Z', False, False, 'Etc/UTC', id='UTC, 0.5h before day start'),
        pytest.param(3, '2021-10-15T9:30:00Z', False, True, 'Europe/Moscow', id='Msk, 2.5h after day start'),
        # fmt: on
    ],
)
async def test_time_zone_api_v2(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        now,
        campaign_id,
        expired,
        in_time,
        crm_admin_get_list_mock,
        timezone_name,
        group_shift,
):
    now = dateutil.parser.parse(now)
    await helper(
        taxi_crm_scheduler,
        pgsql,
        mocked_time,
        expired,
        in_time,
        timezone_name,
        now,
        campaign_id,
        group_id=2 * campaign_id + group_shift,
    )
