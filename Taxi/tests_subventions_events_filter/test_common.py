import json

RULES_SELECT_RULE = {
    'tariff_zones': [],
    'status': 'enabled',
    'start': '2020-03-07T06:00:00+0000',
    'end': '2120-03-07T06:00:00+0000',
    'type': 'driver_fix',
    'is_personal': False,
    'taxirate': 'TAXIRATE-1',
    'subvention_rule_id': '_id/subvention_rule_id_1',
    'cursor': 'cursor_1',
    'tags': [],
    'time_zone': {'id': 'moscow', 'offset': '+03:00'},
    'updated': '2020-03-07T06:00:00+0000',
    'currency': 'RUB',
    'visible_to_driver': False,
    'week_days': [],
    'hours': [],
    'log': [],
    'extra': {},
    'profile_payment_type_restrictions': 'online',
    'profile_tariff_classes': ['business', 'econom'],
    'rates': [
        {'week_day': 'mon', 'start': '00:00', 'rate_per_minute': '5.0'},
        {'week_day': 'mon', 'start': '05:00', 'rate_per_minute': '5.5'},
        {'week_day': 'mon', 'start': '13:00', 'rate_per_minute': '6.0'},
        {'week_day': 'tue', 'start': '01:02', 'rate_per_minute': '4.8'},
        {'week_day': 'wed', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'thu', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'fri', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'sat', 'start': '12:00', 'rate_per_minute': '4.5'},
        {'week_day': 'sun', 'start': '12:00', 'rate_per_minute': '4.5'},
    ],
    'commission_rate_if_fraud': '90.90',
}


async def send_message(
        taxi_subventions_events_filter, testpoint, message_data,
):
    messages = [
        json.dumps(
            {
                'consumer': 'online-events-consumer',
                'data': message_data,
                'topic': 'online-events',
                'cookie': 'cookie1',
            },
        ),
    ]

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    for msg_data in messages:
        await taxi_subventions_events_filter.post(
            'tests/logbroker/messages', data=msg_data,
        )

    await commit.wait_call()


class _DoesntMatter:
    def __eq__(self, other):
        return True


# Used to skip equality check for values
DOESNT_MATTER = _DoesntMatter()
