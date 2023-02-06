import datetime

from metrics_processing import utils

from rider_metrics.models import processor
from rider_metrics.models import rider as rider_module
from rider_metrics.models import rider_event


TST_ENTITY_ID = 'entity_id'
TST_EVENT_ID = 'event_id'
TST_EVENT_TYPE = 'event_type'
TST_CAMPAIGN_ID = 'communication_69'
COMMUNICATION_ACTION_DICT = {
    'campaign_id': TST_CAMPAIGN_ID,
    'type': 'communications',
}
TST_TAG_NAME = 'ManyOTsWarning'
TST_TAG_TTL = 86400
TAGGING_ACTION_DICT = {
    'tags': [{'name': TST_TAG_NAME, 'ttl': TST_TAG_TTL}],
    'type': 'tagging',
}


# pylint: disable=protected-access
async def test_action_journal(
        stq3_context, test_entity_processor, mock_processing_service,
):

    patch = mock_processing_service([], [])

    event = rider_event.RiderEvent(
        event_id=TST_EVENT_ID,
        timestamp=datetime.datetime.utcnow(),
        entity_id=TST_ENTITY_ID,
        event_type=TST_EVENT_TYPE,
        extra_data={'user_id': TST_ENTITY_ID},
    )
    rider = rider_module.Rider(entity_id=TST_ENTITY_ID)
    rider.update_event(event)
    communication_action = utils.make_action_object(
        app=stq3_context,
        entity=rider,
        action=COMMUNICATION_ACTION_DICT,
        event=event,
        actions=processor.EntityProcessor.ACTIONS,
    )
    tagging_action = utils.make_action_object(
        app=stq3_context,
        entity=rider,
        action=TAGGING_ACTION_DICT,
        event=event,
        actions=processor.EntityProcessor.ACTIONS,
    )
    test_entity_processor._context = rider

    await test_entity_processor._action_journal.do_action(tagging_action)
    tagging_calls = patch.tags_upload
    assert tagging_calls.times_called == 1
    tags_json_call = tagging_calls.next_call()['_args'][0].json
    assert tags_json_call['merge_policy'] == 'append'
    assert tags_json_call['entity_type'] == 'user_phone_id'
    assert len(tags_json_call['tags']) == 1
    assert tags_json_call['tags'][0]['name'] == TST_TAG_NAME
    assert tags_json_call['tags'][0]['match']['id'] == TST_ENTITY_ID
    assert tags_json_call['tags'][0]['match']['ttl'] == TST_TAG_TTL

    await test_entity_processor._action_journal.do_action(communication_action)
    communication_calls = patch.communications
    assert communication_calls.times_called == 1
    communication_json_call = communication_calls.next_call()['_args'][0].json
    assert communication_json_call['entity_id'] == TST_ENTITY_ID
    assert communication_json_call['campaign_id'] == TST_CAMPAIGN_ID
    assert communication_json_call['event_id'] == TST_EVENT_ID
    assert communication_json_call['extra_data'] == {'user_id': TST_ENTITY_ID}

    assert not rider.tags
    test_entity_processor._action_journal.modify_local_context()
    assert rider.tags
