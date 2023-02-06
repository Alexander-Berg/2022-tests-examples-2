#  pylint: disable=protected-access

import pytest


@pytest.mark.rules_config(
    TAGGING={
        'default': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'campaign_id': 'communication_69',
                                'type': 'communications',
                                'entity_type': 'park_profile_id',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'unique3',
            },
        ],
    },
    ACTIVITY={
        'default': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'campaign_id': 'communication_69',
                                'type': 'communications',
                                'entity_type': 'park_profile_id',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'unique5',
            },
        ],
    },
)
async def test_config_cache(
        stq3_context,
        taxi_driver_metrics,
        dm_mockserver,
        set_dm_mockserver_500,
):
    config_getter = stq3_context.metrics_rules_config.handler._config_getter
    cached_values = config_getter._load_from_file()

    assert sorted(list(cached_values.keys())) == [
        'activity',
        'activity_blocking',
        'blocking',
        'dispatch_length_thresholds',
        'loyalty',
        'query',
        'stq_callback',
        'tagging',
    ]  # values on application's start

    dm_mockserver.set_response(
        {
            'activity': {
                'default': [
                    {
                        'actions': [
                            {
                                'action': [
                                    {
                                        'campaign_id': 'communication_69',
                                        'type': 'communications',
                                        'entity_type': 'park_profile_id',
                                    },
                                ],
                            },
                        ],
                        'events': [],
                        'name': 'unique5',
                    },
                ],
            },
        },
    )

    await stq3_context.metrics_rules_config.handler.refresh_cache()

    cached_values = config_getter._load_from_file()

    assert cached_values == {
        'activity': {
            'default': [
                {
                    'actions': [
                        {
                            'action': [
                                {
                                    'campaign_id': 'communication_69',
                                    'entity_type': 'park_profile_id',
                                    'type': 'communications',
                                },
                            ],
                        },
                    ],
                    'events': [],
                    'name': 'unique5',
                    'type': 'activity',
                    'zone': 'default',
                },
            ],
        },
        'activity_blocking': {'default': []},
        'blocking': {'default': []},
        'dispatch_length_thresholds': {'default': []},
        'loyalty': {'default': []},
        'query': {'default': []},
        'stq_callback': {'default': []},
        'tagging': {
            'default': [
                {
                    'actions': [
                        {
                            'action': [
                                {
                                    'campaign_id': 'communication_69',
                                    'entity_type': 'park_profile_id',
                                    'type': 'communications',
                                },
                            ],
                        },
                    ],
                    'events': [{'topic': 'order'}],
                    'name': 'unique3',
                    'type': 'tagging',
                    'zone': 'default',
                },
            ],
        },
    }

    await config_getter.save_to_file(
        {
            'activity': {
                'izhevsk': [
                    {
                        'actions': [
                            {
                                'action': [
                                    {
                                        'campaign_id': 'communication',
                                        'entity_type': 'park_profile_id',
                                        'type': 'communications',
                                    },
                                ],
                            },
                        ],
                        'events': [],  # changed in files
                        'name': 'unique5',
                        'type': 'activity',
                        'zone': 'default',
                    },
                ],
            },
        },
    )

    set_dm_mockserver_500()
    stq3_context.metrics_rules_config.handler._is_first_launch = True
    await stq3_context.metrics_rules_config.handler.init_cache()
    assert 'izhevsk' in stq3_context.metrics_rules_config.handler.ACTIVITY
