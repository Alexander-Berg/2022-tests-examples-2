import datetime
import json

import pytest

from tests_subventions_events_filter import helpers
from . import test_common


@pytest.fixture(name='bs_mock')
def _bs(mockserver):
    class Context:
        def __init__(self):
            self.reset()
            self.mock_rules_select = None

        def reset(self):
            self.rules_select_body = []
            self.rules = []

        def add_rule(self, rule):
            self.rules.append(rule)

    context = Context()

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        context.rules_select_body.append(json.loads(request.get_data()))
        return {'subventions': context.rules}

    context.mock_rules_select = _mock_rules_select
    return context


def _make_sef_settings(use_rules_select_cache=False):
    return {
        'enabled': False,
        'bulk_size': 100,
        'use_rules_select_cache': use_rules_select_cache,
        'enable_saving_data_to_redis': True,
        'logbroker_producer_settings': {
            'max_in_fly_messages': 11,
            'partitions_number': 2,
            'commit_timeout': 100,
        },
        'logbroker_consumer_settings': {
            'enabled': True,
            'queue_timeout': 100,
            'chunk_size': 100,
            'config_poll_period': 1000,
        },
    }


def _time_plus_delta(time_str, delta):
    time_format = '%Y-%m-%dT%H:%M:%S+00:00'
    time = datetime.datetime.strptime(time_str, time_format)
    return (time + delta).strftime(time_format)


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_EVENTS_FILTER_SETTINGS=_make_sef_settings(
                        use_rules_select_cache=False,
                    ),
                ),
            ],
            id='no_cache',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_EVENTS_FILTER_SETTINGS=_make_sef_settings(
                        use_rules_select_cache=True,
                    ),
                ),
            ],
            id='use_cache',
        ),
    ],
)
@pytest.mark.parametrize(
    'message_data,expect_processing',
    [
        pytest.param(
            # message_data
            {
                'drivers': [
                    {
                        'unique_driver_id': 'udid1',
                        'dbid': 'dbid1',
                        'uuid': 'uuid1',
                    },
                ],
                'timestamp': '2019-10-11T19:27:49+00:00',
                'tariff_zone': 'msc',
                'tags': ['tag1'],
                'driver_branding': 'full_branding',
                'payment_type_restrictions': 'none',
                'geoarea': 'msc',
            },
            # expect_processing
            True,
            id='good_message',
        ),
        pytest.param(
            # message_data
            {'invalid': 'mesage_data'},
            # expect_processing
            False,
            id='unparsable_message',
        ),
    ],
)
@pytest.mark.config(
    SUBVENTIONS_EVENTS_FILTER_TAGGING_RULES={
        'default_tag_ttl_s': 60,
        'rules': [{'tag': 'mock_tag'}],
    },
)
@pytest.mark.servicetest
async def test_processing(
        taxi_subventions_events_filter,
        redis_store,
        testpoint,
        bs_mock,
        message_data,
        expect_processing,
):
    bs_mock.add_rule(test_common.RULES_SELECT_RULE)

    await test_common.send_message(
        taxi_subventions_events_filter, testpoint, json.dumps(message_data),
    )

    if not expect_processing:
        assert bs_mock.mock_rules_select.times_called == 0
        return

    assert bs_mock.rules_select_body == [
        {
            'tariff_zone': message_data['tariff_zone'],
            'geoarea': message_data['geoarea'],
            'is_personal': False,
            'limit': 1,
            'profile_tags': message_data['tags'],
            'status': 'enabled',
            'profile_payment_type_restrictions': message_data[
                'payment_type_restrictions'
            ],
            'driver_branding': message_data['driver_branding'],
            'time_range': {
                'end': _time_plus_delta(
                    message_data['timestamp'], datetime.timedelta(seconds=1),
                ),
                'start': message_data['timestamp'],
            },
            'types': ['geo_booking', 'driver_fix'],
        },
    ]

    keys_in_redis = helpers.get_redis_state(redis_store)
    assert bool(len(keys_in_redis)) == expect_processing
