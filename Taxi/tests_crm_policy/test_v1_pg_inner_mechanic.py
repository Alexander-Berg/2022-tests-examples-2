# pylint: disable=import-only-modules
import pytest

from tests_crm_policy.utils import select_columns_from_table


async def send_one(taxi_crm_policy, channel):
    response = await taxi_crm_policy.get(
        '/v1/check_update_send_message',
        params={
            'entity_id': 'test_reciever',
            'entity_type': 'user_id',
            'channel_type': channel,
            'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
            'experiment_id': 'crm:hub:push_transporting_seatbelts_poll',
            'experiment_group_id': '2_testing',
        },
    )
    return response


@pytest.mark.pgsql('crm_policy', files=['create_channels_default.sql'])
async def test_update_pg_updated_on_changes(
        taxi_crm_policy, mockserver, pgsql, mocked_time,
):
    first_time = True

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    def _mock_crm_admin_base(request):
        resp = [{}]
        nonlocal first_time
        if first_time:
            first_time = False
            resp = [
                {
                    'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                    'valid_until': '2020-12-31T23:59:59+00:00',
                    'experiment': {
                        'experiment_id': (
                            'crm:hub:push_transporting_seatbelts_poll'
                        ),
                        'groups': [
                            {
                                'group_id': '2_testing',
                                'channel': 'sms',
                                'cooldown': 10000,
                            },
                            {
                                'group_id': '3_testing',
                                'channel': 'wall',
                                'cooldown': 10000,
                            },
                        ],
                    },
                },
            ]
        else:
            resp = [
                {
                    'campaign_id': '8a457abd-c10d-4450-a3ab-199f43ed44bc',
                    'valid_until': '2020-12-31T23:59:59+00:00',
                    'experiment': {
                        'experiment_id': (
                            'crm:hub:push_transporting_seatbelts_poll'
                        ),
                        'groups': [
                            {
                                'group_id': '3_testing',
                                'channel': 'wall',
                                'cooldown': 100000,
                            },
                        ],
                    },
                },
            ]
        return resp

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    mocked_time.sleep(4000)

    response = await send_one(taxi_crm_policy, 'sms')

    assert response.json() == {'allowed': True}

    pg_updated_init_checkpoint = select_columns_from_table(
        'crm_policy.external_communications_groups',
        ['group_id', 'pg_updated'],
        pgsql['crm_policy'],
    )

    updt_tsmp_init_checkpoint = select_columns_from_table(
        'crm_policy.external_communications_groups',
        ['group_id', 'update_timestamp'],
        pgsql['crm_policy'],
    )

    await taxi_crm_policy.invalidate_caches(clean_update=False)

    pg_updated_check_checkpoint = select_columns_from_table(
        'crm_policy.external_communications_groups',
        ['group_id', 'pg_updated'],
        pgsql['crm_policy'],
    )

    upd_tsmp_check_checkpoint = select_columns_from_table(
        'crm_policy.external_communications_groups',
        ['group_id', 'update_timestamp'],
        pgsql['crm_policy'],
    )

    assert pg_updated_init_checkpoint != pg_updated_check_checkpoint
    assert updt_tsmp_init_checkpoint != upd_tsmp_check_checkpoint
