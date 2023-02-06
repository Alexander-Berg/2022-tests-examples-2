import datetime

import pytest

from taxi.clients.helpers import base as api_utils

from taxi_driver_metrics.common.models import run_dms_processing


TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)

DRIVER_UDID = '5b05621ee6c22ea2654849c9'


@pytest.mark.rules_config(
    TAGGING={
        'default': [
            {
                'name': 'some_rule',
                'events_period_sec': 7200,
                'events_to_trigger_cnt': 1,
                'events': [{'topic': 'order', 'name': 'complete'}],
                'expr': (
                    '"user_total_price" in event.extra_data_json and '
                    'event.extra_data_json["user_total_price"] == 0'
                ),
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'chatterbox_chat',
                                'macro_ids': [1, 2],
                                'status': 'open',
                            },
                        ],
                    },
                ],
            },
        ],
    },
)
@pytest.mark.config(
    DRIVER_METRICS_CHATTERBOX_USAGE_SETTINGS={
        'enabled': True,
        'policy': 'strict',
    },
    DRIVER_METRICS_ENABLE_TAGGING_RULES=True,
)
@pytest.mark.filldb(unique_drivers='common')
async def test_chatterbox_action_apply(
        stq3_context,
        taxi_config,
        mockserver,
        patch,
        entity_processor,
        predict_activity,
        dms_mockserver,
):
    @patch(
        'taxi_driver_metrics.common.models.'
        '_processor.Processor.make_entity_processor',
    )
    def _(*args, **kwargs):
        return entity_processor

    @mockserver.json_handler('/driver-metrics-storage/v3/event/complete')
    def _(*args, **kwargs):
        return {}

    @mockserver.json_handler(
        '/driver-metrics-storage/v3/events/unprocessed/list',
    )
    async def _(*args, **kwargs):
        return {
            'items': [
                {
                    'ticket_id': 1,
                    'unique_driver_id': DRIVER_UDID,
                    'current_activity': 98,
                    'current_complete_score': {'value': 1},
                    'events': [
                        {
                            'event_id': 4,
                            'park_driver_profile_id': 'dbid_uuid',
                            'created': api_utils.time_to_iso_string_or_none(
                                TIMESTAMP,
                            ),
                            'type': 'order',
                            'name': 'complete',
                            'order_alias': 'alias',
                            'order_id': '123',
                            'descriptor': {'type': 'complete'},
                            'extra_data': {
                                'dispatch_id': 'a',
                                'replace_activity_with_priority': True,
                                'calculate_priority': True,
                                'user_total_price': 0,
                            },
                        },
                    ],
                },
            ],
        }

    @mockserver.json_handler('/chatterbox-py3/v1/tasks/init/driver_care/')
    async def chatterbox_api(*args, **kwargs):
        return {}

    await run_dms_processing(stq3_context, 100)

    res = chatterbox_api.next_call()['args'][0].json

    assert res == {'macro_ids': [1, 2], 'order_id': '123', 'status': 'open'}
