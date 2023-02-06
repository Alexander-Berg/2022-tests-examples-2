import pytest

HANDLER_PATH = '/v1/config/rule/activity/points'


@pytest.mark.config(
    DRIVER_METRICS_CONFIG_SERVICE_USAGE_SETTINGS={'__default__': ['activity']},
)
@pytest.mark.rules_config(
    ACTIVITY={
        'default': [
            {
                'name': 'ActivityTrip',
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 3}],
                        'tags': '\'event::tariff_comfortplus\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': 2}],
                        'tags': '\'event::dispatch_long\'',
                    },
                    {'action': [{'type': 'activity', 'value': 1}]},
                ],
                'events': [{'topic': 'order', 'name': 'complete'}],
            },
            {
                'name': 'ActivityDriverCancel',
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 0}],
                        'tags': (
                            '\'event::long_waiting\' '
                            'OR \'event::tariff_selfdriving\''
                        ),
                    },
                    {'action': [{'type': 'activity', 'value': -10}]},
                ],
                'events': [
                    {'topic': 'order', 'name': 'auto_reorder'},
                    {'topic': 'order', 'name': 'park_cancel'},
                    {'topic': 'order', 'name': 'park_fail'},
                ],
            },
            {
                'name': 'ActivityOT',
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': -1}],
                        'tags': '\'event::tariff_econom\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': -2}],
                        'tags': '\'event::tariff_comfort\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': -3}],
                        'tags': '\'event::tariff_comfortplus\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': 0}],
                        'tags': '\'event::tariff_selfdriving\'',
                    },
                    {'action': [{'type': 'activity', 'value': 0}]},
                ],
                'events': [
                    {'topic': 'order', 'name': 'offer_timeout'},
                    {'topic': 'order', 'name': 'seen_timeout'},
                ],
            },
        ],
        'anapa': [
            {
                'name': 'ActivityReject',
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 0}],
                        'tags': (
                            '\'event::dispatch_long\' '
                            'OR \'event::explicit_antisurge\' '
                            'OR \'event::long_trip\''
                        ),
                    },
                    {
                        'action': [{'type': 'activity', 'value': -2}],
                        'tags': '\'event::dispatch_medium\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': -4}],
                        'tags': '\'event::dispatch_short\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': -5}],
                        'tags': '\'event::dispatch_medium\'',
                    },
                    {'action': [{'type': 'activity', 'value': -7}]},
                ],
                'events': [
                    {'name': 'reject_manual', 'topic': 'order'},
                    {'name': 'reject_auto_cancel', 'topic': 'order'},
                    {'name': 'reject_missing_tariff', 'topic': 'order'},
                ],
            },
            {
                'name': 'ActivityDriverCancel',
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 0}],
                        'tags': (
                            '\'event::tariff_selfdriving\' OR'
                            ' \'event::long_waiting\''
                        ),
                    },
                    {'action': [{'type': 'activity', 'value': -14}]},
                ],
                'events': [
                    {'name': 'auto_reorder', 'topic': 'order'},
                    {'name': 'park_cancel', 'topic': 'order'},
                    {'name': 'park_fail', 'topic': 'order'},
                ],
            },
            {
                'name': 'ActivityTrip',
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 5}],
                        'tags': '\'event::tariff_comfortplus\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': 4}],
                        'tags': '\'event::dispatch_long\'',
                    },
                    {'action': [{'type': 'activity', 'value': 2}]},
                ],
                'events': [{'topic': 'order', 'name': 'complete'}],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'zone, classes, expected_status, expected_response',
    (
        (
            'anapa',
            ['econom', 'comfort', 'comfortplus', 'selfdriving'],
            200,
            [
                {
                    'long': {'cancel': -14, 'complete': 4, 'skip': -1},
                    'medium': {
                        'cancel': -14,
                        'complete': 2,
                        'reject': -2,
                        'skip': -1,
                    },
                    'short': {
                        'cancel': -14,
                        'complete': 2,
                        'reject': -4,
                        'skip': -1,
                    },
                    'tariff_class': 'econom',
                },
                {
                    'long': {'cancel': -14, 'complete': 4, 'skip': -2},
                    'medium': {
                        'cancel': -14,
                        'complete': 2,
                        'reject': -2,
                        'skip': -2,
                    },
                    'short': {
                        'cancel': -14,
                        'complete': 2,
                        'reject': -4,
                        'skip': -2,
                    },
                    'tariff_class': 'comfort',
                },
                {
                    'long': {'cancel': -14, 'complete': 5, 'skip': -3},
                    'medium': {
                        'cancel': -14,
                        'complete': 5,
                        'reject': -2,
                        'skip': -3,
                    },
                    'short': {
                        'cancel': -14,
                        'complete': 5,
                        'reject': -4,
                        'skip': -3,
                    },
                    'tariff_class': 'comfortplus',
                },
                {
                    'long': {'complete': 4},
                    'medium': {'complete': 2, 'reject': -2},
                    'short': {'complete': 2, 'reject': -4},
                    'tariff_class': 'selfdriving',
                },
            ],
        ),
        (
            'ashenvale',
            ['econom', 'comfort', 'comfortplus', 'selfdriving'],
            200,
            [
                {
                    'long': {'cancel': -10, 'complete': 2, 'skip': -1},
                    'medium': {'cancel': -10, 'complete': 1, 'skip': -1},
                    'short': {'cancel': -10, 'complete': 1, 'skip': -1},
                    'tariff_class': 'econom',
                },
                {
                    'long': {'cancel': -10, 'complete': 2, 'skip': -2},
                    'medium': {'cancel': -10, 'complete': 1, 'skip': -2},
                    'short': {'cancel': -10, 'complete': 1, 'skip': -2},
                    'tariff_class': 'comfort',
                },
                {
                    'long': {'cancel': -10, 'complete': 3, 'skip': -3},
                    'medium': {'cancel': -10, 'complete': 3, 'skip': -3},
                    'short': {'cancel': -10, 'complete': 3, 'skip': -3},
                    'tariff_class': 'comfortplus',
                },
                {
                    'long': {'complete': 2},
                    'medium': {'complete': 1},
                    'short': {'complete': 1},
                    'tariff_class': 'selfdriving',
                },
            ],
        ),
    ),
)
async def test_activity_points(
        taxi_driver_metrics, zone, classes, expected_status, expected_response,
):
    body = {'zone': zone, 'tariff_classes': classes}

    response = await taxi_driver_metrics.post(HANDLER_PATH, json=body)

    assert response.status == expected_status

    json = await response.json()

    assert json['items'] == expected_response
