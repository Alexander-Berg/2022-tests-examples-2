import pytest

from metrics_processing.rules.common import utils


@pytest.mark.parametrize(
    'body',
    (
        {
            'service_name': 'driver-metrics',
            'type': 'stq_callback',
            'zone': 'default',
            'actions': [
                {
                    'action': [
                        {
                            'queues': [
                                {
                                    'data': [
                                        {
                                            'expr': 'event.dbid_uuid',
                                            'name': 'park_driver_profile_id',
                                        },
                                    ],
                                    'default_data_policy': 'replace',
                                    'name': 'medic_order_event',
                                },
                            ],
                            'type': 'stq_callback',
                        },
                    ],
                },
            ],
            'disabled': False,
            'events': [
                {
                    'name': 'complete',
                    'tags': '\'event::tariff_promo\'',
                    'topic': 'order',
                },
            ],
            'additional_params': {
                'events_period_sec': 3600,
                'events_to_trigger_cnt': 1,
                'tags': '\'tags::driverfix_medic_test\'',
            },
            'name': 'MedicOrderEvent',
        },
        {
            'zone': 'spb',
            'type': 'dispatch_length_thresholds',
            'service_name': 'driver-metrics',
            'actions': [
                {
                    'action': [
                        {
                            'distance': [800, 3000],
                            'time': [86400, 86400],
                            'type': 'dispatch_length_thresholds',
                        },
                    ],
                },
            ],
            'events': [{'topic': 'order'}],
            'name': 'CommonDispatchRule',
        },
        {
            'zone': 'default',
            'type': 'blocking',
            'service_name': 'driver-metrics',
            'actions': [
                {
                    'action': [
                        {
                            'blocking_duration_sec': 600,
                            'max_blocked_cnt': 50,
                            'tanker_key_template': (
                                'DriverMetricsDriverFixTempBlock'
                            ),
                            'type': 'blocking',
                        },
                    ],
                },
            ],
            'events': [{'topic': 'order'}],
            'additional_params': {
                'events_period_sec': 3600,
                'events_to_trigger_cnt': 3,
                'are_events_in_a_row': True,
                'tags': (
                    '\'tags::driver_fix\' AND'
                    ' \'tags::driverfix_experiment_group_A\''
                ),
            },
            'name': 'DriverFixBlocking2',
        },
        {
            'zone': 'default',
            'type': 'blocking',
            'importance': 'tier_2',
            'service_name': 'driver-metrics',
            'actions': [
                {
                    'action': [
                        {
                            'blocking_duration_sec': 600,
                            'max_blocked_cnt': 50,
                            'tanker_key_template': (
                                'DriverMetricsDriverFixTempBlock'
                            ),
                            'type': 'blocking',
                        },
                    ],
                },
            ],
            'events': [{'topic': 'order'}],
            'delayed': True,
            'additional_params': {
                'events_period_sec': 3600,
                'events_to_trigger_cnt': 3,
                'tags': (
                    '\'tags::driver_fix\' AND'
                    ' \'tags::driverfix_experiment_group_A\''
                ),
            },
            'name': 'DriverFixBlocking2',
        },
        {
            'zone': 'default',
            'type': 'activity_blocking',
            'responsible_staff_login': 'abd-damir',
            'deadline_seconds': 123,
            'service_name': 'driver-metrics',
            'actions': [
                {
                    'action': [
                        {
                            'activity_threshold': 30,
                            'blocking_duration_sec': 3600,
                            'tanker_key_template': (
                                'DriverMetricsTooManyOfferTimeoutsTempBlock'
                            ),
                            'type': 'activity_blocking',
                        },
                    ],
                },
            ],
            'events': [{'topic': 'dm_service_manual'}],
            'name': 'manual_block',
        },
        pytest.param(
            {
                'zone': 'default',
                'type': 'tagging',
                'service_name': 'driver-metrics',
                'actions': [
                    {
                        'action': [
                            {
                                'exam': 'dkvu',
                                'entity_type': 'driver',
                                'media': ['lol'],
                                'sanctions': ['no_macdonalds'],
                                'reason': {
                                    'keys': ['first_key', 'second_key'],
                                },
                                'comment': 'Razberites s gospodinom',
                                'expires_after_sec': 10,
                                'type': 'qc_invites',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'dm_service_manual'}],
                'name': 'QcInvite',
            },
            id='mayak_qc_invite',
        ),
        pytest.param(
            {
                'zone': 'default',
                'type': 'tagging',  # fallback
                'tariff': '__default__',
                'service_name': 'driver-metrics',
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'tariff_block_startrek',
                                'tariff': 'low_tariff',
                                'message': 'message',
                                'mark': 1,
                                'author': 'me',
                                'queue': 'TEST',
                                'summary': 'mayak - tariff blocking',
                                'summonees': 'me,you',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'mayak_tariff_startrek',
            },
            id='mayak_tariff_startrek',
        ),
        pytest.param(
            {
                'zone': 'default',
                'type': 'tagging',  # fallback
                'tariff': '__default__',
                'service_name': 'driver-metrics',
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'blocklist',
                                'entity_type': 'driver',
                                'comment': 'internal comment for admin',
                                'mechanics': (
                                    'blocklist.mechanics.support_taxi_urgent'
                                ),
                                'expires_after_min': 120,
                                'message_key': (
                                    'blocklist.support_passenger_claim'
                                    '.aggressive_driver'
                                ),
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'mayak_blocklist',
            },
            id='mayak_blocklist',
        ),
    ),
)
@pytest.mark.translations(
    taximeter_messages={
        'DriverMetricsTooManyOfferTimeoutsTempBlockTitle': {
            'ru': 'title-ru',
            'fr': 'title-fr-',
            'en': 'title-en-',
        },
        'DriverMetricsTooManyOfferTimeoutsTempBlockMessage': {
            'ru': 'message-ru-',
            'fr': 'message-fr-',
            'en': 'message-en-',
        },
        'DriverMetricsDriverFixTempBlockTitle': {
            'ru': 'title-ru-DriverMetricsTempBlockTitle',
            'fr': 'title-fr-DriverMetricsTempBlockTitle',
            'en': 'title-en-DriverMetricsTempBlockTitle',
        },
        'DriverMetricsDriverFixTempBlockMessage': {
            'ru': 'message-ru-DriverMetricsTempBlockTitle',
            'fr': 'message-fr-DriverMetricsTempBlockTitle',
            'en': 'message-en-DriverMetricsTempBlockTitle',
        },
    },
)
async def test_create_rule(taxi_driver_metrics, stq3_context, patch, body):
    @patch('metrics_processing.utils.helpers.check_title_message_tanker_key')
    def _(_):
        return True

    @patch(
        'metrics_processing.rules_config.config_service.common.rules.'
        'rule_includes_chatterbox_action',
    )
    def _(_):
        return False

    result = await taxi_driver_metrics.post(
        f'/v1/config/rule/modify',
        json=body,
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    assert result.status == 200

    await stq3_context.metrics_rules_config.handler.refresh_cache_locally()

    rule_type = body['type']
    zone = body['zone']
    name = body['name']
    delayed = body.get('delayed')
    found = False

    rules = utils.get_cached_rules(stq3_context, rule_type)
    for rule in rules[zone]:
        if rule.name == name:
            found = True
            assert rule
            assert rule.delayed if delayed else True
    assert found
