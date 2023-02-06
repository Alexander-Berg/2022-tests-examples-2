# pylint: disable=unused-variable
import pytest

from crm_efficiency.generated.cron import run_cron

CRM_EFFICIENCY_SETTINGS = {
    'NirvanaSettings': {
        'instance_id': 'a12d3940-1bcd-424b-9a57-b3b02762c493',
        'workflow_id': '1363da95-a6cc-45bb-ae7b-643ed902812f',
        'workflow_timeout_in_seconds': 86400,
        'workflow_retry_period_in_seconds': 60,
    },
    'SparkSettings': {
        'spark3_discovery_path': '//home/taxi-crm/production/spark',
        'output_path': '//tmp/crm-efficiency/testing',
        'temp_path': '//tmp/crm-efficiency',
    },
    'CrmPolicySettings': {
        'channel_config_path': '//home/taxi-dwh/raw/mdb/config/config',
        'channel_config_id': 'CRM_POLICY_CHANNEL_DEFAULTS_V4',
        'postgres_replica_path': (
            '//home/taxi/production/replica/postgres/crm_policy'
        ),
    },
    'CrmAdminSettings': {
        'admin_root_path': '//home/taxi-crm/robot-crm-admin',
        'postgres_replica_path': (
            '//home/taxi/production/replica/postgres/crm_admin'
        ),
        'ready_to_send_group_state': 'SENDING',
        'experiments_path': '//home/taxi-crm/test',
        'campaign_columns_to_save': [
            'group_name',
            'entity_id',
            'recipient_context',
            'campaign_id',
            'entity_type',
            'channel_type',
            'experiment_id',
            'segment_id',
        ],
    },
}

CRM_EFFICIENCY_BLACKBOX_AB = {
    'blackbox_experiment_id': 'first',
    'salt': 'first',
    'models': [
        {
            'enabled': True,
            'version': 1.0,
            'ratio': 0.5,
            'instance_id': '1926e17c-38e4-466e-af1d-fa6404c27859',
            'workflow_id': 'bb5f4a9c-3682-412e-b1b2-4dde0ac07d49',
            'model_settings': {
                'segment_path': '//tmp/crm-efficiency/segments_to_send',
                'output_path': (
                    '//tmp/crm-efficiency/segments_to_send_filtered'
                ),
                'output_banned_path': (
                    '//tmp/crm-efficiency/segments_to_send_banned'
                ),
                'output_frozen_path': (
                    '//tmp/crm-efficiency/segments_to_send_frozen'
                ),
                'campaign_log': '//tmp/crm-efficiency/campaign_log',
                'comm_status_filter': '(\'sent\', \'error\')',
                'efficiency_segments_log': (
                    '//tmp/crm-efficiency/efficiency_segments_log'
                ),
                'prestable_size': 20000,
                'push_default_threshold': '0.5',
                'push_monoapp_threshold': '-1',
                'push_payed_threshold': '0.01',
                'resolution_timeout_days': 3,
                'setting_path': '//tmp/crm-efficiency/settings_log',
                'order_data': {
                    'big_food_order_cancel_path': (
                        '//home/taxi-dwh/ods/food/bigfood/order_cancel'
                    ),
                    'big_food_order_cancel_reason_path': (
                        '//home/taxi-dwh/ods/food/bigfood/order_cancel_reason'
                    ),
                    'big_food_order_path': (
                        '//home/taxi-dwh/ods/food/bigfood/order'
                    ),
                    'big_food_order_revision_path': (
                        '//home/eda-dwh/ods/bigfood/order_revision'
                    ),
                    'currency_rate_path': (
                        '//home/taxi-dwh/dds/dim_currency_rate'
                    ),
                    'taxi_order_path': (
                        '//home/taxi-dwh/ods/dbprocessing/order'
                    ),
                    'user_phone_path': (
                        '//home/taxi-dwh/ods/mdb/user_phone/user_phone'
                    ),
                    'users_bigfood_path': (
                        '//home/eda-dwh/ods/bigfood/user/user'
                    ),
                },
            },
        },
        {
            'enabled': True,
            'version': 1.1,
            'ratio': 0.5,
            'instance_id': '22d2b319-ba02-46f4-b4fa-c62b6ceac851',
            'workflow_id': '16f7fcb0-2367-49f0-840b-344646100d92',
            'model_settings': {
                'segment_path': '//tmp/crm-efficiency/segments_to_send',
                'output_path': (
                    '//tmp/crm-efficiency/segments_to_send_filtered'
                ),
                'output_banned_path': (
                    '//tmp/crm-efficiency/segments_to_send_banned'
                ),
                'campaign_log': '//tmp/crm-efficiency/campaign_log',
                'comm_status_filter': '(\'sent\', \'error\')',
                'efficiency_segments_log': (
                    '//tmp/crm-efficiency/efficiency_segments_log'
                ),
                'prestable_size': 20000,
                'push_default_threshold': '0.5',
                'push_monoapp_threshold': '-1',
                'push_payed_threshold': '0.01',
                'resolution_timeout_days': 3,
                'setting_path': '//tmp/crm-efficiency/settings_log',
                'order_data': {
                    'big_food_order_cancel_path': (
                        '//home/taxi-dwh/ods/food/bigfood/order_cancel'
                    ),
                    'big_food_order_cancel_reason_path': (
                        '//home/taxi-dwh/ods/food/bigfood/order_cancel_reason'
                    ),
                    'big_food_order_path': (
                        '//home/taxi-dwh/ods/food/bigfood/order'
                    ),
                    'big_food_order_revision_path': (
                        '//home/eda-dwh/ods/bigfood/order_revision'
                    ),
                    'currency_rate_path': (
                        '//home/taxi-dwh/dds/dim_currency_rate'
                    ),
                    'taxi_order_path': (
                        '//home/taxi-dwh/ods/dbprocessing/order'
                    ),
                    'user_phone_path': (
                        '//home/taxi-dwh/ods/mdb/user_phone/user_phone'
                    ),
                    'users_bigfood_path': (
                        '//home/eda-dwh/ods/bigfood/user/user'
                    ),
                },
            },
        },
    ],
}


@pytest.mark.config(
    CRM_EFFICIENCY_SETTINGS=CRM_EFFICIENCY_SETTINGS,
    CRM_EFFICIENCY_BLACKBOX_AB=CRM_EFFICIENCY_BLACKBOX_AB,
)
async def test_run_spark(cron_context, mock_crm_efficiency, patch, pgsql, stq):
    @patch('crm_efficiency.utils.run_spark.run_spark')
    async def spark_submit(context, *args, **kwargs):
        pass

    @mock_crm_efficiency('/v1/internal/nirvana/run')
    async def nirvana_run(*args, **vargs):
        return {}

    @patch('crm_efficiency.crontasks.prepare_segment.check_if_exists')
    async def check_if_exists(context, *args, **kwargs):
        return True

    await run_cron.main(
        ['crm_efficiency.crontasks.prepare_segment', '-t', '0'],
    )
    cursor = pgsql['crm_efficiency'].cursor()
    cursor.execute('select id, status from crm_efficiency.runs')
    result = list((row[0], row[1]) for row in cursor)
    expected = [(1, 'True'), (2, 'True')]
    assert result == expected


@pytest.mark.config(CRM_EFFICIENCY_SETTINGS=CRM_EFFICIENCY_SETTINGS)
@pytest.mark.pgsql('crm_efficiency', files=['started.sql'])
async def test_stil_running(
        cron_context, mock_crm_efficiency, patch, pgsql, stq,
):
    result = await run_cron.main(
        ['crm_efficiency.crontasks.prepare_segment', '-t', '0'],
    )
    cursor = pgsql['crm_efficiency'].cursor()
    cursor.execute('select id, status from crm_efficiency.runs')
    result = list((row[0], row[1]) for row in cursor)
    assert result == []
