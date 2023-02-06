import pytest


from generated.clients import crm_policy as crm_client
from generated.models import crm_policy
from taxi.util import dates

from crm_hub.logic import yt_absorber_v2
from crm_hub.logic.bulk_sending import bulk_policy


@pytest.mark.parametrize(
    'campaign_id, group_id, combination, verify, allowed',
    [
        (1, 1, 1, False, True),
        (1, 1, 1, True, False),
        (1, 1, 2, False, False),
        (1, 1, 3, False, False),
        (1, 1, 4, False, False),
        (1, 1, 5, False, False),
        (1, 2, 1, False, True),
        (1, 2, 1, True, False),
        (1, 2, 2, False, False),
        (1, 2, 3, False, False),
        (1, 2, 4, False, False),
        (1, 2, 5, False, False),
        (1, 3, 1, False, True),
        (1, 3, 1, True, False),
        (1, 3, 2, False, False),
        (1, 3, 3, False, False),
        (1, 3, 4, False, False),
        (1, 3, 5, False, False),
        (2, 1, 1, False, True),
        (2, 1, 1, True, False),
        (2, 1, 2, False, False),
        (2, 1, 3, False, False),
        (2, 1, 4, False, False),
        (2, 1, 5, False, False),
        (2, 2, 1, False, True),
        (2, 2, 1, True, False),
        (2, 2, 2, False, False),
        (2, 2, 3, False, False),
        (2, 2, 4, False, False),
        (2, 2, 5, False, False),
        (2, 3, 1, False, True),
        (2, 3, 1, True, False),
        (2, 3, 2, False, False),
        (2, 3, 3, False, False),
        (2, 3, 4, False, False),
        (2, 3, 5, False, False),
    ],
)
async def test_policy(
        web_context,
        patch,
        mockserver,
        pgsql,
        load_json,
        campaign_id,
        group_id,
        combination,
        verify,
        allowed,
):
    sending_key = f'batch_{campaign_id}_{group_id}'
    sending_settings_key = f'batch_{campaign_id}_{group_id}_{combination}'

    @mockserver.json_handler('crm-admin/v1/batch-sending/item')
    async def _batch_sending_item(*_a, **_kw):
        batch_sendings = load_json('crm_admin_policy.json')
        return batch_sendings[sending_key]

    @patch('crm_hub.logic.channels.get_sender_settings')
    def _get_sender_settings(context):
        batch_sending_settings = load_json('crm_admin_policy_settings.json')
        return batch_sending_settings[sending_settings_key]

    @patch('crm_hub.logic.yt_absorber_v2._call_yt_absorber_task')
    async def _call_yt_absorber_task(
            context,
            sending_full_info,
            verify,
            control,
            global_control_enabled,
            send_at,
            dependency_id,
    ):
        pass

    send_at = dates.utcnow()
    await yt_absorber_v2.create_absorber_task(
        context=web_context,
        campaign_id=campaign_id,
        group_id=group_id,
        verify=verify,
        send_at=send_at,
        subfilters=[],
        start_id=0,
    )

    query = f'SELECT use_policy FROM crm_hub.batch_sending '
    query += f'WHERE campaign_id = {campaign_id} and group_id = {group_id};'

    cursor = pgsql['crm_hub'].cursor()
    cursor.execute(query)
    for row in cursor.fetchall():
        assert row[0] == allowed


@pytest.mark.parametrize(
    'entities, result, ignore',
    [
        (['id_1', 'id_2', 'id_3'], ([True, True, True], []), True),
        (
            ['id_1', 'id_2', 'id_3', 'id_4'],
            ([True, True, True, True], []),
            True,
        ),
        (['id_1', 'id_2', 'id_3'], None, False),
    ],
)
async def test_ignore_policy_exceptions(
        stq3_context, mockserver, entities, result, ignore,
):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message_bulk')
    async def _(_):
        return mockserver.make_response(
            json={'code': '400', 'message': 'error'}, status=400,
        )

    policy_request = crm_client.V1CheckUpdateSendMessageBulkPostBody(
        campaign_id='campaign_id',
        items=[
            crm_policy.CheckUpdateSendItem(
                entity_id=item, experiment_group_id='group_id',
            )
            for item in entities
        ],
    )
    retry_settings = dict(max_attempts=5, delay_ms=100)
    policy_client = stq3_context.clients.crm_policy
    if not ignore:
        with pytest.raises(Exception):
            await bulk_policy.call_bulk_policy(
                policy_client, policy_request, retry_settings, ignore,
            )
    else:
        filtered = await bulk_policy.call_bulk_policy(
            policy_client, policy_request, retry_settings, ignore,
        )

        assert filtered == result
