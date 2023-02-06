# pylint: disable=too-many-lines
import datetime

from aiohttp import web
import pytest


from taxi_antifraud.crontasks import amayak
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import data as data_module
from test_taxi_antifraud.cron.utils import mock
from test_taxi_antifraud.cron.utils import state

CURSOR_STATE_NAME = amayak.CURSOR_STATE_NAME

YT_DIRECTORY_PATH = '//home/taxi-fraud/unittests/amayak'
YT_TABLE_PATH = YT_DIRECTORY_PATH + '/input'

DEFAULT_CONFIG: dict = {
    'AFS_CRON_AMAYAK_BAN_CAR_SANCTION_ENABLED': True,
    'AFS_CRON_AMAYAK_BAN_SANCTION_ENABLED': True,
    'AFS_CRON_AMAYAK_COMMUNICATION_SANCTION_ENABLED': True,
    'AFS_CRON_AMAYAK_DKVU_INVITE_SANCTION_ENABLED': True,
    'AFS_CRON_AMAYAK_ENABLED': True,
    'AFS_CRON_AMAYAK_INPUT_TABLE_SUFFIX': 'amayak/input',
    'AFS_CRON_AMAYAK_LEGACY_BAN_SANCTION_ENABLED': True,
    'AFS_CRON_AMAYAK_REMOVE_BRANDING_SANCTION_ENABLED': True,
    'AFS_CRON_AMAYAK_SLEEP_TIME_SECONDS': 0.01,
    'AFS_CRON_AMAYAK_STS_INVITE_SANCTION_ENABLED': True,
    'AFS_CRON_AMAYAK_IDENTITY_INVITE_SANCTION_ENABLED': True,
    'AFS_CRON_AMAYAK_TAGGING_SANCTION_ENABLED': True,
    'AFS_CRON_CURSOR_USE_PGSQL': 'enabled',
}


def _serialize_request(request) -> dict:
    return {
        'json': request.json,
        'idempotency_token': request.headers.getone('X-Idempotency-Token'),
    }


@pytest.fixture
def mock_personal(patch):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(data_type, request_id, *args, **kwargs):
        return {'license': '123123'}


@pytest.mark.now('2021-02-19T23:58:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_amayak_counters_response,'
    'expected_driver_wall_add_response,expected_invite_exam_response,'
    'expected_legacy_ban_response,expected_ban_drivers_response,'
    'expected_invite_sts_response',
    [
        (
            'test_crontask',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Do not be',
                                'title': 'You are bad',
                                'type': 'communication',
                            },
                            'threshold': 1,
                        },
                        {
                            'sanction': {
                                'comment': 'Be adviced',
                                'use_park_id': False,
                                'type': 'dkvu_invite',
                            },
                            'threshold': 1,
                        },
                        {
                            'sanction': {
                                'comment': 'Be aware',
                                'use_park_id': True,
                                'type': 'dkvu_invite',
                            },
                            'threshold': 2,
                        },
                        {
                            'sanction': {
                                'text': 'Hey',
                                'title': (
                                    'Two more times and you gonna be banned'
                                ),
                                'type': 'communication',
                            },
                            'threshold': 3,
                        },
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason_tanker_key': 'some_key',
                                'type': 'ban',
                                'mechanics': 'amayak',
                            },
                            'threshold': 5,
                        },
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason': 'You are banned',
                                'type': 'legacy_ban',
                            },
                            'threshold': 5,
                        },
                        {
                            'sanction': {
                                'reason_tanker_key': 'some_another_key',
                                'type': 'ban',
                                'mechanics': 'amayak',
                            },
                            'threshold': 6,
                        },
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason': 'You are banned again',
                                'type': 'legacy_ban',
                            },
                            'threshold': 6,
                        },
                    ],
                },
                'test_rule_with_round_down': {
                    'counters': [
                        {
                            'event_type': 'collusion',
                            'window_seconds': 604800,
                            'minimum_seconds_between_events': 21600,
                        },
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'What are you doing?',
                                'title': 'Hey',
                                'type': 'communication',
                            },
                            'threshold': 1,
                        },
                        {
                            'sanction': {
                                'text': 'Stop',
                                'title': 'Please',
                                'type': 'communication',
                            },
                            'threshold': 3,
                        },
                        {
                            'sanction': {
                                'duration_seconds': 86400,
                                'reason_tanker_key': 'some_other_key',
                                'type': 'ban',
                                'mechanics': 'amayak',
                            },
                            'threshold': 5,
                        },
                    ],
                },
                'test_rule_with_random': {
                    'counters': [
                        {
                            'event_type': 'taxa',
                            'window_seconds': 2592000,
                            'minimum_seconds_between_events': {
                                'min_value': 28800,
                                'max_value': 172800,
                            },
                        },
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Why are you using taxa?',
                                'title': 'Hello',
                                'type': 'communication',
                            },
                            'threshold': 1,
                        },
                        {
                            'sanction': {
                                'text': 'Stop using taxa',
                                'title': 'Pretty please',
                                'type': 'communication',
                            },
                            'threshold': 3,
                        },
                    ],
                },
                'test_rule_sts': {
                    'counters': [
                        {'event_type': 'hook_sts', 'window_seconds': 2592000},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'comment': 'Be adviced',
                                'use_park_id': False,
                                'type': 'sts_invite',
                            },
                            'threshold': 1,
                        },
                        {
                            'sanction': {
                                'comment': 'Be aware',
                                'use_park_id': True,
                                'type': 'sts_invite',
                            },
                            'threshold': 2,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613708979,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid2',
                    'db_id': 'some_db_id2',
                    'driver_uuid': 'some_driver_uuid2',
                    'device_id': 'some_device_id2',
                },
                {
                    'event_timestamp': 1613718879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid3',
                    'db_id': 'some_db_id3',
                    'driver_uuid': 'some_driver_uuid3',
                    'device_id': 'some_device_id3',
                },
                {
                    'event_timestamp': 1613728879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid4',
                    'db_id': 'some_db_id4',
                    'driver_uuid': 'some_driver_uuid4',
                    'device_id': 'some_device_id4',
                },
                {
                    'event_timestamp': 1613738879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid5',
                    'db_id': 'some_db_id5',
                    'driver_uuid': 'some_driver_uuid5',
                    'device_id': 'some_device_id5',
                },
                {
                    'event_timestamp': 1613748879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid6',
                    'db_id': 'some_db_id6',
                    'driver_uuid': 'some_driver_uuid6',
                    'device_id': 'some_device_id6',
                },
                {
                    'event_timestamp': 1613363279,
                    'event_type': 'taxa',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613530018,
                    'event_type': 'taxa',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613530118,
                    'event_type': 'taxa',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613696858,
                    'event_type': 'taxa',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613696958,
                    'event_type': 'taxa',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613696958,
                    'event_type': 'hook_sts',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                    'additional_info': {'car_number': 'A001AA01'},
                },
                {
                    'event_timestamp': 1613696959,
                    'event_type': 'hook_sts',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid2',
                    'db_id': 'some_db_id2',
                    'driver_uuid': 'some_driver_uuid2',
                    'device_id': 'some_device_id2',
                    'additional_info': {'car_number': 'A001AA01'},
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 27, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'collusion:604800:21600:1',
                    'event_timestamp': 1613708879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 27, 4, 27, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id2',
                        'device_id': 'some_device_id2',
                        'driver_uuid': 'some_driver_uuid2',
                        'udid': 'some_udid2',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708979,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 29, 39,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id3',
                        'device_id': 'some_device_id3',
                        'driver_uuid': 'some_driver_uuid3',
                        'udid': 'some_udid3',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613718879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 7, 14, 39,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id4',
                        'device_id': 'some_device_id4',
                        'driver_uuid': 'some_driver_uuid4',
                        'udid': 'some_udid4',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613728879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 10, 1, 19,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id5',
                        'device_id': 'some_device_id5',
                        'driver_uuid': 'some_driver_uuid5',
                        'udid': 'some_udid5',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613738879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 12, 47, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id5',
                        'device_id': 'some_device_id5',
                        'driver_uuid': 'some_driver_uuid5',
                        'udid': 'some_udid5',
                    },
                    'counter_name': 'collusion:604800:21600:1',
                    'event_timestamp': 1613738879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 27, 12, 47, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id6',
                        'device_id': 'some_device_id6',
                        'driver_uuid': 'some_driver_uuid6',
                        'udid': 'some_udid6',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613748879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 15, 34, 39,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'taxa:2592000:random:1',
                    'event_timestamp': 1613363279,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 15, 4, 27, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'taxa:2592000:random:1',
                    'event_timestamp': 1613530118,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 17, 2, 48, 38,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'taxa:2592000:random:1',
                    'event_timestamp': 1613696958,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 1, 9, 18,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'car_number': 'A001AA01',
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'hook_sts:2592000:0:1',
                    'event_timestamp': 1613696958,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 1, 9, 18,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'car_number': 'A001AA01',
                        'db_id': 'some_db_id2',
                        'device_id': 'some_device_id2',
                        'driver_uuid': 'some_driver_uuid2',
                        'udid': 'some_udid2',
                    },
                    'counter_name': 'hook_sts:2592000:0:1',
                    'event_timestamp': 1613696959,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 1, 9, 19,
                    ),
                    'weight_index': 0,
                },
            ],
            [
                {
                    'idempotency_token': '31c6097afb51e113be53350661c2fc2d',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Do not be',
                            'title': 'You are bad',
                        },
                    },
                },
                {
                    'idempotency_token': '5ec9b3963d554ede9b95c30a2bd4a846',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': 'amayak_test_rule_with_round_down_06e273a2f46a4f8ca5068ed1ad0b73a0',  # noqa: E501 pylint: disable=line-too-long
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'What are you doing?',
                            'title': 'Hey',
                        },
                    },
                },
                {
                    'idempotency_token': 'bd4ccba8292724ad8723f8c6110ce5cd',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                            {'driver': 'some_db_id2_some_driver_uuid2'},
                            {'driver': 'some_db_id3_some_driver_uuid3'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Hey',
                            'title': 'Two more times and you gonna be banned',
                        },
                    },
                },
                {
                    'idempotency_token': '747741c6600433a7954334e99a3f3822',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': 'amayak_test_rule_with_random_06e273a2f46a4f8ca5068ed1ad0b73a0',  # noqa: E501 pylint: disable=line-too-long
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Why are you using taxa?',
                            'title': 'Hello',
                        },
                    },
                },
                {
                    'idempotency_token': '4e129fcabde20bd8737dc55d0f53e27e',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': 'amayak_test_rule_with_random_06e273a2f46a4f8ca5068ed1ad0b73a0',  # noqa: E501 pylint: disable=line-too-long
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Stop using taxa',
                            'title': 'Pretty please',
                        },
                    },
                },
            ],
            [
                {
                    'idempotency_token': 'b237b15108f6ed451b98abea411cc0a1',
                    'json': {
                        'comment': 'Be adviced',
                        'filters': {
                            'license_pd_id': (
                                '06e273a2f46a4f8ca5068ed1ad0b73a0'
                            ),
                        },
                        'identity_type': 'service',
                    },
                },
                {
                    'idempotency_token': '5a19d81a0373dff91ca71cc32ca24030',
                    'json': {
                        'comment': 'Be aware',
                        'filters': {
                            'license_pd_id': (
                                '06e273a2f46a4f8ca5068ed1ad0b73a0'
                            ),
                            'park_id': 'some_db_id1',
                        },
                        'identity_type': 'service',
                    },
                },
                {
                    'idempotency_token': '0088f6ccaa4dbfae1bc240a0c67b540d',
                    'json': {
                        'comment': 'Be aware',
                        'filters': {
                            'license_pd_id': (
                                '06e273a2f46a4f8ca5068ed1ad0b73a0'
                            ),
                            'park_id': 'some_db_id2',
                        },
                        'identity_type': 'service',
                    },
                },
            ],
            [
                {
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'kwargs': {
                                'license_id': (
                                    '06e273a2f46a4f8ca5068ed1ad0b73a0'
                                ),
                            },
                            'predicate_id': (
                                '33333333-3333-3333-3333-333333333333'
                            ),
                            'reason': {'key': 'some_key'},
                            'expires': '2021-02-20T03:58:04+03:00',
                            'mechanics': 'amayak',
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                    'idempotency_token': '8b99e5b6182c25848a4d2fdf5a04f029',
                },
                {
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'kwargs': {
                                'license_id': (
                                    '06e273a2f46a4f8ca5068ed1ad0b73a0'
                                ),
                            },
                            'predicate_id': (
                                '33333333-3333-3333-3333-333333333333'
                            ),
                            'reason': {'key': 'some_another_key'},
                            'mechanics': 'amayak',
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                    'idempotency_token': '1ea4a9d27fc54f15561322d6b44d35be',
                },
            ],
            [
                {
                    'license': '123123',
                    'login': 'robot-amayak',
                    'reason': 'You are banned',
                    'ticket': 'antifraud_amayak_rule_test_rule',
                    'till': '2021-02-20T03:58:04+03:00',
                },
                {
                    'license': '123123',
                    'login': 'robot-amayak',
                    'reason': 'You are banned again',
                    'ticket': 'antifraud_amayak_rule_test_rule',
                    'till': '2021-02-20T03:58:04+03:00',
                },
            ],
            [
                {
                    'idempotency_token': '490d470381e947826134b18b503b2d1b',
                    'json': {
                        'comment': 'Be adviced',
                        'filters': {'car_number': 'A001AA01'},
                        'identity_type': 'service',
                    },
                },
                {
                    'idempotency_token': 'de49d0a372963f59a5f62da6d9640c32',
                    'json': {
                        'comment': 'Be aware',
                        'filters': {
                            'car_number': 'A001AA01',
                            'park_id': 'some_db_id1',
                        },
                        'identity_type': 'service',
                    },
                },
                {
                    'idempotency_token': 'f1e181c85b1fea7f60812242d6569286',
                    'json': {
                        'comment': 'Be aware',
                        'filters': {
                            'car_number': 'A001AA01',
                            'park_id': 'some_db_id2',
                        },
                        'identity_type': 'service',
                    },
                },
            ],
        ),
    ],
)
async def test_cron(
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_taxi_driver_wall,
        mock_blocklist,
        mock_taximeter_xservice,
        mock_driver_profiles,
        mock_qc_invites,
        yt_apply,
        yt_client,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        config_rules,
        data,
        expected_amayak_counters_response,
        expected_driver_wall_add_response,
        expected_invite_exam_response,
        expected_legacy_ban_response,
        expected_ban_drivers_response,
        expected_invite_sts_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_taxi_driver_wall('/internal/driver-wall/v1/add')
    async def _driver_wall_add(request):
        return web.json_response({'id': 'some_id'})

    @mock_blocklist('/internal/blocklist/v1/add')
    async def _blocklist_add(request):
        return web.json_response({'block_id': 'some_block_id'})

    @mock_taximeter_xservice('/utils/blacklist/drivers/ban')
    def _ban_drivers(request):
        return web.json_response(data=dict())

    @mock_driver_profiles('/v1/driver/app/profiles/retrieve')
    async def _retrieve(request):
        return {
            'profiles': [
                {
                    'data': {'locale': 'ru'},
                    'park_driver_profile_id': 'driver_park_id_driver_id',
                },
            ],
        }

    @mock_qc_invites('/admin/qc-invites/v1/dkvu/invite')
    async def _invite_dkvu_exam(request):
        return web.json_response({'invite_id': 'some_invite_id'})

    @mock_qc_invites('/admin/qc-invites/v1/sts/invite')
    async def _invite_sts_exam(request):
        return web.json_response({'invite_id': 'some_invite_id'})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )

    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert (
        await db.antifraud_amayak_counters_mdb.find(
            {}, {'_id': False},
        ).to_list(None)
        == expected_amayak_counters_response
    )

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_NAME: str(len(data)),
    }

    assert [
        _serialize_request(_driver_wall_add.next_call()['request'])
        for _ in range(_driver_wall_add.times_called)
    ] == expected_driver_wall_add_response

    assert [
        _serialize_request(_invite_dkvu_exam.next_call()['request'])
        for _ in range(_invite_dkvu_exam.times_called)
    ] == expected_invite_exam_response

    assert [
        _serialize_request(_blocklist_add.next_call()['request'])
        for _ in range(_blocklist_add.times_called)
    ] == expected_legacy_ban_response

    assert mock.get_requests(_ban_drivers) == expected_ban_drivers_response

    assert [
        _serialize_request(_invite_sts_exam.next_call()['request'])
        for _ in range(_invite_sts_exam.times_called)
    ] == expected_invite_sts_response


@pytest.mark.now('2021-02-19T23:58:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_driver_wall_add_response',
    [
        (
            'test_without_format',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Do not be',
                                'title': 'You are bad',
                                'type': 'communication',
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'idempotency_token': '31c6097afb51e113be53350661c2fc2d',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Do not be',
                            'title': 'You are bad',
                        },
                    },
                },
            ],
        ),
        (
            'test_with_format_row',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Do not be',
                                'title': 'You are bad',
                                'type': 'communication',
                                'format': 'Raw',
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'idempotency_token': '31c6097afb51e113be53350661c2fc2d',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Do not be',
                            'title': 'You are bad',
                        },
                    },
                },
            ],
        ),
        (
            'test_with_format_markdown',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Do not be',
                                'title': 'You are bad',
                                'type': 'communication',
                                'format': 'Markdown',
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'idempotency_token': 'feaea95a4ded607597e21a7bc5070a28',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Markdown',
                            'text': 'Do not be',
                            'title': 'You are bad',
                        },
                    },
                },
            ],
        ),
    ],
)
async def test_communication_format(
        mock_taxi_driver_wall,
        yt_client,
        taxi_config,
        cron_context,
        comment,
        config,
        config_rules,
        data,
        expected_driver_wall_add_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_taxi_driver_wall('/internal/driver-wall/v1/add')
    async def _driver_wall_add(request):
        return web.json_response({'id': 'some_id'})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert [
        _serialize_request(_driver_wall_add.next_call()['request'])
        for _ in range(_driver_wall_add.times_called)
    ] == expected_driver_wall_add_response


@pytest.mark.now('2021-02-19T23:58:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_driver_wall_add_response',
    [
        (
            'send_image',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Do not be',
                                'title': 'You are bad',
                                'type': 'communication',
                                'image_id': 'bad_photo',
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'idempotency_token': 'b218a6b7a3bbaf4a380ef005cbb8b26c',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Do not be',
                            'title': 'You are bad',
                            'image_id': 'bad_photo',
                        },
                    },
                },
            ],
        ),
    ],
)
async def test_send_image(
        mock_taxi_driver_wall,
        yt_client,
        taxi_config,
        cron_context,
        comment,
        config,
        config_rules,
        data,
        expected_driver_wall_add_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_taxi_driver_wall('/internal/driver-wall/v1/add')
    async def _driver_wall_add(request):
        return web.json_response({'id': 'some_id'})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert [
        _serialize_request(_driver_wall_add.next_call()['request'])
        for _ in range(_driver_wall_add.times_called)
    ] == expected_driver_wall_add_response


@pytest.mark.now('2021-02-19T23:58:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_driver_wall_add_response',
    [
        (
            'alert is False',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Do not be',
                                'title': 'You are bad',
                                'type': 'communication',
                                'image_id': 'bad_photo',
                                'alert': False,
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'idempotency_token': 'b218a6b7a3bbaf4a380ef005cbb8b26c',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Do not be',
                            'title': 'You are bad',
                            'image_id': 'bad_photo',
                        },
                    },
                },
            ],
        ),
        (
            'without alert',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Do not be',
                                'title': 'You are bad',
                                'type': 'communication',
                                'image_id': 'bad_photo',
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'idempotency_token': 'b218a6b7a3bbaf4a380ef005cbb8b26c',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Do not be',
                            'title': 'You are bad',
                            'image_id': 'bad_photo',
                        },
                    },
                },
            ],
        ),
        (
            'alert is True',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Do not be',
                                'title': 'You are bad',
                                'type': 'communication',
                                'image_id': 'bad_photo',
                                'alert': True,
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'idempotency_token': 'bc47cd684169158b14f4fd1a22905c93',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': True,
                            'format': 'Raw',
                            'text': 'Do not be',
                            'title': 'You are bad',
                            'image_id': 'bad_photo',
                        },
                    },
                },
            ],
        ),
        (
            'alert is False, config is True',
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_DRIVER_COMMUNICATION_USE_ALERT': True,
            },
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Do not be',
                                'title': 'You are bad',
                                'type': 'communication',
                                'image_id': 'bad_photo',
                                'alert': False,
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'idempotency_token': 'b218a6b7a3bbaf4a380ef005cbb8b26c',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Do not be',
                            'title': 'You are bad',
                            'image_id': 'bad_photo',
                        },
                    },
                },
            ],
        ),
    ],
)
async def test_alert_from_amayak_config(
        mock_taxi_driver_wall,
        yt_client,
        taxi_config,
        cron_context,
        comment,
        config,
        config_rules,
        data,
        expected_driver_wall_add_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_taxi_driver_wall('/internal/driver-wall/v1/add')
    async def _driver_wall_add(request):
        return web.json_response({'id': 'some_id'})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert [
        _serialize_request(_driver_wall_add.next_call()['request'])
        for _ in range(_driver_wall_add.times_called)
    ] == expected_driver_wall_add_response


@pytest.mark.now('2021-02-19T23:58:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_amayak_counters_response,'
    'expected_invite_identity_response,',
    [
        (
            'test_invite_identity_rule',
            DEFAULT_CONFIG,
            {
                'test_rule_identity': {
                    'counters': [
                        {
                            'event_type': 'hook_identity',
                            'window_seconds': 2592000,
                        },
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'comment': 'Identity_without_park',
                                'use_park_id': False,
                                'type': 'identity_invite',
                            },
                            'threshold': 2,
                        },
                        {
                            'sanction': {
                                'comment': 'Identity_with_park',
                                'use_park_id': True,
                                'type': 'identity_invite',
                            },
                            'threshold': 2,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613696960,
                    'event_type': 'hook_identity',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid3',
                    'db_id': 'some_db_id3',
                    'driver_uuid': 'some_driver_uuid3',
                    'device_id': 'some_device_id3',
                },
                {
                    'event_timestamp': 1613696961,
                    'event_type': 'hook_identity',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid4',
                    'db_id': 'some_db_id4',
                    'driver_uuid': 'some_driver_uuid4',
                    'device_id': 'some_device_id4',
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id3',
                        'device_id': 'some_device_id3',
                        'driver_uuid': 'some_driver_uuid3',
                        'udid': 'some_udid3',
                    },
                    'counter_name': 'hook_identity:2592000:0:1',
                    'event_timestamp': 1613696960,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 1, 9, 20,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id4',
                        'device_id': 'some_device_id4',
                        'driver_uuid': 'some_driver_uuid4',
                        'udid': 'some_udid4',
                    },
                    'counter_name': 'hook_identity:2592000:0:1',
                    'event_timestamp': 1613696961,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 1, 9, 21,
                    ),
                    'weight_index': 0,
                },
            ],
            [
                {
                    'idempotency_token': '79ff4dc21a155c71dc8dfff9c9aac5d7',
                    'json': {
                        'comment': 'Identity_without_park',
                        'filters': {
                            'license_pd_id': (
                                '06e273a2f46a4f8ca5068ed1ad0b73a0'
                            ),
                        },
                        'identity_type': 'service',
                    },
                },
                {
                    'idempotency_token': '82b11e62afc115c7029c3c3bc1ed712e',
                    'json': {
                        'comment': 'Identity_with_park',
                        'filters': {
                            'license_pd_id': (
                                '06e273a2f46a4f8ca5068ed1ad0b73a0'
                            ),
                            'park_id': 'some_db_id3',
                        },
                        'identity_type': 'service',
                    },
                },
                {
                    'idempotency_token': '670a57f9d7a9b9ac31590067c95c1d26',
                    'json': {
                        'comment': 'Identity_with_park',
                        'filters': {
                            'license_pd_id': (
                                '06e273a2f46a4f8ca5068ed1ad0b73a0'
                            ),
                            'park_id': 'some_db_id4',
                        },
                        'identity_type': 'service',
                    },
                },
            ],
        ),
    ],
)
async def test_identity_invite(
        mock_qc_invites,
        yt_apply,
        yt_client,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        config_rules,
        data,
        expected_amayak_counters_response,
        expected_invite_identity_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_qc_invites('/admin/qc-invites/v1/identity/invite')
    async def _invite_identity_exam(request):
        return web.json_response({'invite_id': 'some_invite_id'})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])
    assert (
        await db.antifraud_amayak_counters_mdb.find(
            {}, {'_id': False},
        ).to_list(None)
        == expected_amayak_counters_response
    )

    assert [
        _serialize_request(_invite_identity_exam.next_call()['request'])
        for _ in range(_invite_identity_exam.times_called)
    ] == expected_invite_identity_response


@pytest.mark.now('2021-02-21T23:58:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_driver_wall_add_response',
    [
        (
            'test_range_sanctions',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'hook_dkvu', 'window_seconds': 2592000},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Be careful',
                                'title': 'You are bad',
                                'type': 'communication',
                            },
                            'threshold': {'begin': 1, 'end': 3},
                        },
                        {
                            'sanction': {
                                'text': 'Be more careful',
                                'title': 'You are very bad',
                                'type': 'communication',
                            },
                            'threshold': {'begin': 3, 'end': 5},
                        },
                        {
                            'sanction': {
                                'text': 'I will ban you',
                                'title': 'You are frauder',
                                'type': 'communication',
                            },
                            'threshold': {'begin': 6, 'end': 10},
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613718879,
                    'event_type': 'hook_dkvu',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613728879,
                    'event_type': 'hook_dkvu',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613738879,
                    'event_type': 'hook_dkvu',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613748879,
                    'event_type': 'hook_dkvu',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613758879,
                    'event_type': 'hook_dkvu',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613768879,
                    'event_type': 'hook_dkvu',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613778879,
                    'event_type': 'hook_dkvu',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613788879,
                    'event_type': 'hook_dkvu',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'idempotency_token': '7373e06fabccabb52887280a1502f32f',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Be careful',
                            'title': 'You are bad',
                        },
                    },
                },
                {
                    'idempotency_token': 'e75b8cf5f9016e254c0820b1ac4c4996',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Be careful',
                            'title': 'You are bad',
                        },
                    },
                },
                {
                    'idempotency_token': 'e9b3ee11588f873af1c6c7aaf0468913',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Be careful',
                            'title': 'You are bad',
                        },
                    },
                },
                {
                    'idempotency_token': '6ceeb39ef2ab836118cf1f65baa3d7a1',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Be more careful',
                            'title': 'You are very bad',
                        },
                    },
                },
                {
                    'idempotency_token': '9f7cf481dc887671476e95fb8b2f4845',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Be more careful',
                            'title': 'You are very bad',
                        },
                    },
                },
                {
                    'idempotency_token': '6397f71c27ad219125d8ca2d7a58f4fb',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Be more careful',
                            'title': 'You are very bad',
                        },
                    },
                },
                {
                    'idempotency_token': 'e7543cd0870b6e7916ba6a637a7c9308',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'I will ban you',
                            'title': 'You are frauder',
                        },
                    },
                },
                {
                    'idempotency_token': '7b1802ec7e88cff86b9b2cab52868e56',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'I will ban you',
                            'title': 'You are frauder',
                        },
                    },
                },
                {
                    'idempotency_token': '60f20073364e34bd509837244d28cf57',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'I will ban you',
                            'title': 'You are frauder',
                        },
                    },
                },
            ],
        ),
    ],
)
async def test_range_sanctions(
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_taxi_driver_wall,
        yt_apply,
        yt_client,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        config_rules,
        data,
        expected_driver_wall_add_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_taxi_driver_wall('/internal/driver-wall/v1/add')
    async def _driver_wall_add(request):
        return web.json_response({'id': 'some_id'})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert [
        _serialize_request(_driver_wall_add.next_call()['request'])
        for _ in range(_driver_wall_add.times_called)
    ] == expected_driver_wall_add_response


@pytest.mark.now('2021-02-19T23:58:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_counters,'
    'expected_ban_drivers_response',
    [
        (
            'test_regular_ban',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason_tanker_key': 'some_key',
                                'type': 'ban',
                                'mechanics': 'amayak',
                            },
                            'threshold': 5,
                        },
                        {
                            'sanction': {
                                'reason_tanker_key': 'some_another_key',
                                'type': 'ban',
                                'mechanics': 'amayak',
                            },
                            'threshold': 6,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613708979,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid2',
                    'db_id': 'some_db_id2',
                    'driver_uuid': 'some_driver_uuid2',
                    'device_id': 'some_device_id2',
                },
                {
                    'event_timestamp': 1613718879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid3',
                    'db_id': 'some_db_id3',
                    'driver_uuid': 'some_driver_uuid3',
                    'device_id': 'some_device_id3',
                },
                {
                    'event_timestamp': 1613728879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid4',
                    'db_id': 'some_db_id4',
                    'driver_uuid': 'some_driver_uuid4',
                    'device_id': 'some_device_id4',
                },
                {
                    'event_timestamp': 1613738879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid5',
                    'db_id': 'some_db_id5',
                    'driver_uuid': 'some_driver_uuid5',
                    'device_id': 'some_device_id5',
                },
                {
                    'event_timestamp': 1613748879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid6',
                    'db_id': 'some_db_id6',
                    'driver_uuid': 'some_driver_uuid6',
                    'device_id': 'some_device_id6',
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 27, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id2',
                        'device_id': 'some_device_id2',
                        'driver_uuid': 'some_driver_uuid2',
                        'udid': 'some_udid2',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708979,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 29, 39,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id3',
                        'device_id': 'some_device_id3',
                        'driver_uuid': 'some_driver_uuid3',
                        'udid': 'some_udid3',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613718879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 7, 14, 39,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id4',
                        'device_id': 'some_device_id4',
                        'driver_uuid': 'some_driver_uuid4',
                        'udid': 'some_udid4',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613728879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 10, 1, 19,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id5',
                        'device_id': 'some_device_id5',
                        'driver_uuid': 'some_driver_uuid5',
                        'udid': 'some_udid5',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613738879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 12, 47, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id6',
                        'device_id': 'some_device_id6',
                        'driver_uuid': 'some_driver_uuid6',
                        'udid': 'some_udid6',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613748879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 15, 34, 39,
                    ),
                    'weight_index': 0,
                },
            ],
            [
                {
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'kwargs': {
                                'license_id': (
                                    '06e273a2f46a4f8ca5068ed1ad0b73a0'
                                ),
                            },
                            'predicate_id': (
                                '33333333-3333-3333-3333-333333333333'
                            ),
                            'reason': {'key': 'some_key'},
                            'expires': '2021-02-20T03:58:04+03:00',
                            'mechanics': 'amayak',
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                    'idempotency_token': '8b99e5b6182c25848a4d2fdf5a04f029',
                },
                {
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'kwargs': {
                                'license_id': (
                                    '06e273a2f46a4f8ca5068ed1ad0b73a0'
                                ),
                            },
                            'predicate_id': (
                                '33333333-3333-3333-3333-333333333333'
                            ),
                            'reason': {'key': 'some_another_key'},
                            'mechanics': 'amayak',
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                    'idempotency_token': '1ea4a9d27fc54f15561322d6b44d35be',
                },
            ],
        ),
        (
            'test_park_id',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason_tanker_key': 'some_key',
                                'type': 'ban',
                                'use_park_id': False,
                                'mechanics': 'amayak',
                            },
                            'threshold': 1,
                        },
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason_tanker_key': 'some_key',
                                'type': 'ban',
                                'use_park_id': True,
                                'mechanics': 'amayak',
                            },
                            'threshold': 2,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613708979,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid2',
                    'db_id': 'some_db_id2',
                    'driver_uuid': 'some_driver_uuid2',
                    'device_id': 'some_device_id2',
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 27, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id2',
                        'device_id': 'some_device_id2',
                        'driver_uuid': 'some_driver_uuid2',
                        'udid': 'some_udid2',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708979,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 29, 39,
                    ),
                    'weight_index': 0,
                },
            ],
            [
                {
                    'idempotency_token': 'c72a7ee5185c9e9e7fa0ef4e9994288f',
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'expires': '2021-02-20T03:58:04+03:00',
                            'kwargs': {
                                'license_id': (
                                    '06e273a2f46a4f8ca5068ed1ad0b73a0'
                                ),
                            },
                            'predicate_id': (
                                '33333333-3333-3333-3333-333333333333'
                            ),
                            'reason': {'key': 'some_key'},
                            'mechanics': 'amayak',
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                },
                {
                    'idempotency_token': '942cbead51dc8e9033acb35e15e1e1d6',
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'expires': '2021-02-20T03:58:04+03:00',
                            'kwargs': {
                                'license_id': (
                                    '06e273a2f46a4f8ca5068ed1ad0b73a0'
                                ),
                                'park_id': 'some_db_id1',
                            },
                            'predicate_id': (
                                '44444444-4444-4444-4444-444444444444'
                            ),
                            'reason': {'key': 'some_key'},
                            'mechanics': 'amayak',
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                },
                {
                    'idempotency_token': 'e50e8af2c2f7dfb03106f1ba2059558e',
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'expires': '2021-02-20T03:58:04+03:00',
                            'kwargs': {
                                'license_id': (
                                    '06e273a2f46a4f8ca5068ed1ad0b73a0'
                                ),
                                'park_id': 'some_db_id2',
                            },
                            'predicate_id': (
                                '44444444-4444-4444-4444-444444444444'
                            ),
                            'reason': {'key': 'some_key'},
                            'mechanics': 'amayak',
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                },
            ],
        ),
        (
            'test_license_pd_id_in_additional_info',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason_tanker_key': 'some_key',
                                'type': 'ban',
                                'use_park_id': False,
                                'mechanics': 'amayak',
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                    'additional_info': {'license_pd_id': 'some_license_pd_id'},
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'license_pd_id': 'some_license_pd_id',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 27, 59,
                    ),
                    'weight_index': 0,
                },
            ],
            [
                {
                    'idempotency_token': 'e603dfb5abcc5e512b8e7bd0dcc1bd0a',
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'expires': '2021-02-20T03:58:04+03:00',
                            'kwargs': {'license_id': 'some_license_pd_id'},
                            'predicate_id': (
                                '33333333-3333-3333-3333-333333333333'
                            ),
                            'reason': {'key': 'some_key'},
                            'mechanics': 'amayak',
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                },
            ],
        ),
    ],
)
async def test_ban(
        mock_blocklist,
        yt_apply,
        yt_client,
        taxi_config,
        db,
        cron_context,
        comment,
        config,
        config_rules,
        data,
        expected_counters,
        expected_ban_drivers_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_blocklist('/internal/blocklist/v1/add')
    async def _blocklist_add(request):
        return web.json_response({'block_id': 'some_block_id'})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert (
        await db.antifraud_amayak_counters_mdb.find(
            {}, {'_id': False},
        ).to_list(None)
        == expected_counters
    )

    assert [
        _serialize_request(_blocklist_add.next_call()['request'])
        for _ in range(_blocklist_add.times_called)
    ] == expected_ban_drivers_response


@pytest.mark.now('2021-02-19T23:58:04')
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'blocklist.reasons.terms_of_service_violation': {
            'ru': 'Нарушение сервисных стандартов.',
            'en': 'Service standard violation.',
        },
    },
)
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_counters,'
    'expected_legacy_ban_response',
    [
        (
            'test_regular_ban',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason': 'You are banned',
                                'type': 'legacy_ban',
                            },
                            'threshold': 5,
                        },
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason': 'You are banned again',
                                'type': 'legacy_ban',
                            },
                            'threshold': 6,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613708979,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid2',
                    'db_id': 'some_db_id2',
                    'driver_uuid': 'some_driver_uuid2',
                    'device_id': 'some_device_id2',
                },
                {
                    'event_timestamp': 1613718879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid3',
                    'db_id': 'some_db_id3',
                    'driver_uuid': 'some_driver_uuid3',
                    'device_id': 'some_device_id3',
                },
                {
                    'event_timestamp': 1613728879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid4',
                    'db_id': 'some_db_id4',
                    'driver_uuid': 'some_driver_uuid4',
                    'device_id': 'some_device_id4',
                },
                {
                    'event_timestamp': 1613738879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid5',
                    'db_id': 'some_db_id5',
                    'driver_uuid': 'some_driver_uuid5',
                    'device_id': 'some_device_id5',
                },
                {
                    'event_timestamp': 1613748879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid6',
                    'db_id': 'some_db_id6',
                    'driver_uuid': 'some_driver_uuid6',
                    'device_id': 'some_device_id6',
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 27, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id2',
                        'device_id': 'some_device_id2',
                        'driver_uuid': 'some_driver_uuid2',
                        'udid': 'some_udid2',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708979,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 29, 39,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id3',
                        'device_id': 'some_device_id3',
                        'driver_uuid': 'some_driver_uuid3',
                        'udid': 'some_udid3',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613718879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 7, 14, 39,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id4',
                        'device_id': 'some_device_id4',
                        'driver_uuid': 'some_driver_uuid4',
                        'udid': 'some_udid4',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613728879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 10, 1, 19,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id5',
                        'device_id': 'some_device_id5',
                        'driver_uuid': 'some_driver_uuid5',
                        'udid': 'some_udid5',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613738879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 12, 47, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id6',
                        'device_id': 'some_device_id6',
                        'driver_uuid': 'some_driver_uuid6',
                        'udid': 'some_udid6',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613748879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 15, 34, 39,
                    ),
                    'weight_index': 0,
                },
            ],
            [
                {
                    'license': '123123',
                    'login': 'robot-amayak',
                    'reason': 'You are banned',
                    'ticket': 'antifraud_amayak_rule_test_rule',
                    'till': '2021-02-20T03:58:04+03:00',
                },
                {
                    'license': '123123',
                    'login': 'robot-amayak',
                    'reason': 'You are banned again',
                    'ticket': 'antifraud_amayak_rule_test_rule',
                    'till': '2021-02-20T03:58:04+03:00',
                },
            ],
        ),
        (
            'test_park_id',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason': 'You are banned',
                                'type': 'legacy_ban',
                                'use_park_id': False,
                            },
                            'threshold': 1,
                        },
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason': 'You are banned again',
                                'type': 'legacy_ban',
                                'use_park_id': True,
                            },
                            'threshold': 2,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613708979,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid2',
                    'db_id': 'some_db_id2',
                    'driver_uuid': 'some_driver_uuid2',
                    'device_id': 'some_device_id2',
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 27, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id2',
                        'device_id': 'some_device_id2',
                        'driver_uuid': 'some_driver_uuid2',
                        'udid': 'some_udid2',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708979,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 29, 39,
                    ),
                    'weight_index': 0,
                },
            ],
            [
                {
                    'license': '123123',
                    'login': 'robot-amayak',
                    'reason': 'You are banned',
                    'ticket': 'antifraud_amayak_rule_test_rule',
                    'till': '2021-02-20T03:58:04+03:00',
                },
                {
                    'license': '123123',
                    'login': 'robot-amayak',
                    'park_id': 'some_db_id1',
                    'reason': 'You are banned again',
                    'ticket': 'antifraud_amayak_rule_test_rule',
                    'till': '2021-02-20T03:58:04+03:00',
                },
                {
                    'license': '123123',
                    'login': 'robot-amayak',
                    'park_id': 'some_db_id2',
                    'reason': 'You are banned again',
                    'ticket': 'antifraud_amayak_rule_test_rule',
                    'till': '2021-02-20T03:58:04+03:00',
                },
            ],
        ),
        (
            'test_tanker_key',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason': '',
                                'reason_tanker_key': 'blocklist.reasons.terms_of_service_violation',  # noqa: E501 pylint: disable=line-too-long
                                'type': 'legacy_ban',
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1613708879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 1, 21, 4, 27, 59,
                    ),
                    'weight_index': 0,
                },
            ],
            [
                {
                    'license': '123123',
                    'login': 'robot-amayak',
                    'reason': 'Нарушение сервисных стандартов.',
                    'ticket': 'antifraud_amayak_rule_test_rule',
                    'till': '2021-02-20T03:58:04+03:00',
                },
            ],
        ),
    ],
)
async def test_legacy_ban(
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_taximeter_xservice,
        mock_driver_profiles,
        yt_apply,
        yt_client,
        taxi_config,
        db,
        cron_context,
        comment,
        config,
        config_rules,
        data,
        expected_counters,
        expected_legacy_ban_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_taximeter_xservice('/utils/blacklist/drivers/ban')
    def _ban_drivers(request):
        return web.json_response(data=dict())

    @mock_driver_profiles('/v1/driver/app/profiles/retrieve')
    async def _retrieve(request):
        return {
            'profiles': [
                {
                    'data': {'locale': 'ru'},
                    'park_driver_profile_id': 'driver_park_id_driver_id',
                },
            ],
        }

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert (
        await db.antifraud_amayak_counters_mdb.find(
            {}, {'_id': False},
        ).to_list(None)
        == expected_counters
    )

    assert mock.get_requests(_ban_drivers) == expected_legacy_ban_response


@pytest.mark.now('2021-06-20T20:03:04+03:00')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_counters,'
    'expected_tags_response',
    [
        (
            'test_regular_tagging',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'type': 'tagging',
                                'append': [
                                    {
                                        'name': 'deprioritize_1',
                                        'ttl_seconds': 86400,
                                    },
                                ],
                                'remove': [],
                            },
                            'threshold': 1,
                        },
                        {
                            'sanction': {
                                'type': 'tagging',
                                'append': [
                                    {
                                        'name': 'deprioritize_3',
                                        'ttl_seconds': 86400,
                                    },
                                    {'name': 'got_3'},
                                ],
                                'remove': [{'name': 'deprioritize_1'}],
                            },
                            'threshold': 2,
                        },
                        {
                            'sanction': {
                                'type': 'tagging',
                                'append': [{'name': 'deprioritize_5'}],
                                'remove': [
                                    {'name': 'deprioritize_1'},
                                    {'name': 'deprioritize_3'},
                                ],
                            },
                            'threshold': 3,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1624208254,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1624208354,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid2',
                    'db_id': 'some_db_id2',
                    'driver_uuid': 'some_driver_uuid2',
                    'device_id': 'some_device_id2',
                },
                {
                    'event_timestamp': 1624208454,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid3',
                    'db_id': 'some_db_id3',
                    'driver_uuid': 'some_driver_uuid3',
                    'device_id': 'some_device_id3',
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1624208254,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 5, 22, 16, 57, 34,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id2',
                        'device_id': 'some_device_id2',
                        'driver_uuid': 'some_driver_uuid2',
                        'udid': 'some_udid2',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1624208354,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 5, 22, 16, 59, 14,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id3',
                        'device_id': 'some_device_id3',
                        'driver_uuid': 'some_driver_uuid3',
                        'udid': 'some_udid3',
                    },
                    'counter_name': 'collusion:86400:0:1',
                    'event_timestamp': 1624208454,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 5, 22, 17, 0, 54,
                    ),
                    'weight_index': 0,
                },
            ],
            [
                {
                    'idempotency_token': '2d3e0fa1f3944fdc75466ecaf15b00f9',
                    'json': {
                        'append': [
                            {
                                'entity_type': 'udid',
                                'tags': [
                                    {
                                        'entity': 'some_udid1',
                                        'name': 'deprioritize_1',
                                        'ttl': 86400,
                                    },
                                ],
                            },
                        ],
                        'provider_id': 'antifraud',
                    },
                },
                {
                    'idempotency_token': '8b1958d8a644e2e21b1aee7b8dc30872',
                    'json': {
                        'append': [
                            {
                                'entity_type': 'udid',
                                'tags': [
                                    {
                                        'entity': 'some_udid1',
                                        'name': 'deprioritize_3',
                                        'ttl': 86400,
                                    },
                                    {'entity': 'some_udid1', 'name': 'got_3'},
                                    {
                                        'entity': 'some_udid2',
                                        'name': 'deprioritize_3',
                                        'ttl': 86400,
                                    },
                                    {'entity': 'some_udid2', 'name': 'got_3'},
                                ],
                            },
                        ],
                        'provider_id': 'antifraud',
                        'remove': [
                            {
                                'entity_type': 'udid',
                                'tags': [
                                    {
                                        'entity': 'some_udid1',
                                        'name': 'deprioritize_1',
                                    },
                                    {
                                        'entity': 'some_udid2',
                                        'name': 'deprioritize_1',
                                    },
                                ],
                            },
                        ],
                    },
                },
                {
                    'idempotency_token': '6bbba414b37780238161564f1f7f4ed9',
                    'json': {
                        'append': [
                            {
                                'entity_type': 'udid',
                                'tags': [
                                    {
                                        'entity': 'some_udid1',
                                        'name': 'deprioritize_5',
                                    },
                                    {
                                        'entity': 'some_udid2',
                                        'name': 'deprioritize_5',
                                    },
                                    {
                                        'entity': 'some_udid3',
                                        'name': 'deprioritize_5',
                                    },
                                ],
                            },
                        ],
                        'provider_id': 'antifraud',
                        'remove': [
                            {
                                'entity_type': 'udid',
                                'tags': [
                                    {
                                        'entity': 'some_udid1',
                                        'name': 'deprioritize_1',
                                    },
                                    {
                                        'entity': 'some_udid1',
                                        'name': 'deprioritize_3',
                                    },
                                    {
                                        'entity': 'some_udid2',
                                        'name': 'deprioritize_1',
                                    },
                                    {
                                        'entity': 'some_udid2',
                                        'name': 'deprioritize_3',
                                    },
                                    {
                                        'entity': 'some_udid3',
                                        'name': 'deprioritize_1',
                                    },
                                    {
                                        'entity': 'some_udid3',
                                        'name': 'deprioritize_3',
                                    },
                                ],
                            },
                        ],
                    },
                },
            ],
        ),
    ],
)
async def test_tagging(
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_tags,
        yt_apply,
        yt_client,
        taxi_config,
        db,
        cron_context,
        comment,
        config,
        config_rules,
        data,
        expected_counters,
        expected_tags_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_tags('/v2/upload')
    async def _upload(request):
        return {'status': 'ok'}

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    yt_client.create(
        'table', path=YT_TABLE_PATH, recursive=True, ignore_existing=True,
    )
    yt_client.write_table(YT_TABLE_PATH, data)
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert (
        await db.antifraud_amayak_counters_mdb.find(
            {}, {'_id': False},
        ).to_list(None)
        == expected_counters
    )

    assert [
        _serialize_request(_upload.next_call()['request'])
        for _ in range(_upload.times_called)
    ] == expected_tags_response


@pytest.mark.now('2021-02-21T23:58:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_counters,'
    'expected_driver_wall_add_response',
    [
        (
            'test_multiple_weights',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {
                            'event_type': 'low_speed_limit',
                            'window_seconds': 2592000,
                            'weight': 1,
                        },
                        {
                            'event_type': 'medium_speed_limit',
                            'window_seconds': 2592000,
                            'weight': 3,
                        },
                        {
                            'event_type': 'high_speed_limit',
                            'window_seconds': 2592000,
                            'weight': 5,
                        },
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Low is reached',
                                'title': 'Low',
                                'type': 'communication',
                            },
                            'threshold': 1,
                        },
                        {
                            'sanction': {
                                'text': 'Medium is reached',
                                'title': 'Medium',
                                'type': 'communication',
                            },
                            'threshold': 4,
                        },
                        {
                            'sanction': {
                                'text': 'High is reached',
                                'title': 'High',
                                'type': 'communication',
                            },
                            'threshold': 9,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613718879,
                    'event_type': 'low_speed_limit',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613718880,
                    'event_type': 'medium_speed_limit',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613718881,
                    'event_type': 'high_speed_limit',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'low_speed_limit:2592000:0:1',
                    'event_timestamp': 1613718879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 39,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'medium_speed_limit:2592000:0:3',
                    'event_timestamp': 1613718880,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 40,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'medium_speed_limit:2592000:0:3',
                    'event_timestamp': 1613718880,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 40,
                    ),
                    'weight_index': 1,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'medium_speed_limit:2592000:0:3',
                    'event_timestamp': 1613718880,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 40,
                    ),
                    'weight_index': 2,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'high_speed_limit:2592000:0:5',
                    'event_timestamp': 1613718881,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 41,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'high_speed_limit:2592000:0:5',
                    'event_timestamp': 1613718881,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 41,
                    ),
                    'weight_index': 1,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'high_speed_limit:2592000:0:5',
                    'event_timestamp': 1613718881,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 41,
                    ),
                    'weight_index': 2,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'high_speed_limit:2592000:0:5',
                    'event_timestamp': 1613718881,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 41,
                    ),
                    'weight_index': 3,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'high_speed_limit:2592000:0:5',
                    'event_timestamp': 1613718881,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 41,
                    ),
                    'weight_index': 4,
                },
            ],
            [
                {
                    'idempotency_token': '4c8f67c459d8929d6f76be9b26e0ee56',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Low is reached',
                            'title': 'Low',
                        },
                    },
                },
                {
                    'idempotency_token': '24119f4b4dd76f3608aed620ce3f59ec',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Medium is reached',
                            'title': 'Medium',
                        },
                    },
                },
                {
                    'idempotency_token': '574c376385fdbb60ddc535c794afe79b',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'High is reached',
                            'title': 'High',
                        },
                    },
                },
            ],
        ),
        (
            'test_zero_weights',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {
                            'event_type': 'low_speed_limit',
                            'window_seconds': 2592000,
                            'weight': 0,
                        },
                        {
                            'event_type': 'medium_speed_limit',
                            'window_seconds': 2592000,
                            'weight': 0,
                        },
                        {
                            'event_type': 'high_speed_limit',
                            'window_seconds': 2592000,
                            'weight': 0,
                        },
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Let me tell you something',
                                'title': 'Hey',
                                'type': 'communication',
                            },
                            'threshold': {'begin': 1, 'end': 1000},
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613718879,
                    'event_type': 'low_speed_limit',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613718880,
                    'event_type': 'medium_speed_limit',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1613718881,
                    'event_type': 'high_speed_limit',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [],
            [],
        ),
    ],
)
async def test_weight(
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_taxi_driver_wall,
        yt_apply,
        yt_client,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        config_rules,
        data,
        expected_counters,
        expected_driver_wall_add_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_taxi_driver_wall('/internal/driver-wall/v1/add')
    async def _driver_wall_add(request):
        return web.json_response({'id': 'some_id'})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert (
        await db.antifraud_amayak_counters_mdb.find(
            {}, {'_id': False},
        ).to_list(None)
        == expected_counters
    )

    assert [
        _serialize_request(_driver_wall_add.next_call()['request'])
        for _ in range(_driver_wall_add.times_called)
    ] == expected_driver_wall_add_response


@pytest.mark.now('2021-06-20T20:03:04+03:00')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_qc_response',
    [
        (
            'test_regular_remove_branding',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'type': 'remove_branding',
                                'reason_tanker_key': 'because_we_can',
                                'duration_seconds': 86400,
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1624208254,
                    'event_type': 'collusion',
                    'driver_license_pd_id': 'something_completely_random',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                    'additional_info': {'car_id': 'some_car_id1'},
                },
            ],
            [
                {
                    'enabled': True,
                    'future': [
                        {
                            'begin': '2021-06-21T20:03:04+03:00',
                            'can_pass': True,
                            'sanctions': ['sticker_off', 'lightbox_off'],
                        },
                    ],
                    'identity': {
                        'yandex_team': {'yandex_login': 'robot-amayak'},
                    },
                    'present': {
                        'can_pass': False,
                        'sanctions': ['sticker_off', 'lightbox_off'],
                    },
                    'reason': {'keys': ['because_we_can']},
                },
            ],
        ),
    ],
)
async def test_remove_branding(
        mock_quality_control_py3,
        yt_client,
        taxi_config,
        cron_context,
        comment,
        config,
        config_rules,
        data,
        expected_qc_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_quality_control_py3('/api/v1/state')
    async def _qc_state(request):
        if request.method == 'POST':
            return {}
        return {
            'id': 'some_id',
            'exams': [{'code': 'branding', 'modified': '2021-01-01T00:00:00'}],
            'type': 'car',
        }

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    yt_client.create(
        'table', path=YT_TABLE_PATH, recursive=True, ignore_existing=True,
    )
    yt_client.write_table(YT_TABLE_PATH, data)

    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    _qc_state.next_call()  # skip GET request

    assert mock.get_requests(_qc_state) == expected_qc_response


@pytest.mark.now('2021-02-19T23:58:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_ban_cars_response',
    [
        (
            'test_regular_ban_car',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'collusion', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason_tanker_key': 'some_key',
                                'type': 'ban_car',
                                'use_park_id': False,
                                'mechanics': 'amayak',
                            },
                            'threshold': 1,
                        },
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason_tanker_key': 'some_key',
                                'type': 'ban_car',
                                'use_park_id': True,
                                'mechanics': 'amayak',
                            },
                            'threshold': 2,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613708879,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                    'additional_info': {'car_number': 'A123BC77'},
                },
                {
                    'event_timestamp': 1613708979,
                    'event_type': 'collusion',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid2',
                    'db_id': 'some_db_id2',
                    'driver_uuid': 'some_driver_uuid2',
                    'device_id': 'some_device_id2',
                    'additional_info': {'car_number': 'Z456YX88'},
                },
            ],
            [
                {
                    'idempotency_token': '6c5386b0c96b1d80be8c84d446c14d82',
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'expires': '2021-02-20T03:58:04+03:00',
                            'kwargs': {'car_number': 'A123BC77'},
                            'mechanics': 'amayak',
                            'predicate_id': (
                                '11111111-1111-1111-1111-111111111111'
                            ),
                            'reason': {'key': 'some_key'},
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                },
                {
                    'idempotency_token': '75a5e3dc97aa0a554484e402a069084d',
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'expires': '2021-02-20T03:58:04+03:00',
                            'kwargs': {
                                'car_number': 'A123BC77',
                                'park_id': 'some_db_id1',
                            },
                            'mechanics': 'amayak',
                            'predicate_id': (
                                '22222222-2222-2222-2222-222222222222'
                            ),
                            'reason': {'key': 'some_key'},
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                },
                {
                    'idempotency_token': 'b1997e0a8894f97d00c44f0becdd8867',
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'expires': '2021-02-20T03:58:04+03:00',
                            'kwargs': {
                                'car_number': 'A123BC77',
                                'park_id': 'some_db_id2',
                            },
                            'mechanics': 'amayak',
                            'predicate_id': (
                                '22222222-2222-2222-2222-222222222222'
                            ),
                            'reason': {'key': 'some_key'},
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                },
                {
                    'idempotency_token': '1f69dbb13529f5ec6ced2593988a8754',
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'expires': '2021-02-20T03:58:04+03:00',
                            'kwargs': {
                                'car_number': 'Z456YX88',
                                'park_id': 'some_db_id1',
                            },
                            'mechanics': 'amayak',
                            'predicate_id': (
                                '22222222-2222-2222-2222-222222222222'
                            ),
                            'reason': {'key': 'some_key'},
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                },
                {
                    'idempotency_token': '0f454f67b702524d1b0fefa66781beb1',
                    'json': {
                        'block': {
                            'comment': 'antifraud_amayak_rule_test_rule',
                            'expires': '2021-02-20T03:58:04+03:00',
                            'kwargs': {
                                'car_number': 'Z456YX88',
                                'park_id': 'some_db_id2',
                            },
                            'mechanics': 'amayak',
                            'predicate_id': (
                                '22222222-2222-2222-2222-222222222222'
                            ),
                            'reason': {'key': 'some_key'},
                        },
                        'identity': {
                            'name': 'robot-amayak',
                            'type': 'service',
                        },
                    },
                },
            ],
        ),
    ],
)
async def test_ban_car(
        mock_blocklist,
        yt_client,
        taxi_config,
        cron_context,
        comment,
        config,
        config_rules,
        data,
        expected_ban_cars_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_blocklist('/internal/blocklist/v1/add')
    async def _blocklist_add(request):
        return web.json_response({'block_id': 'some_block_id'})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert [
        _serialize_request(_blocklist_add.next_call()['request'])
        for _ in range(_blocklist_add.times_called)
    ] == expected_ban_cars_response


@pytest.mark.now('2021-02-21T23:58:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_counters,'
    'expected_driver_wall_add_response',
    [
        (
            'test_enabled_false',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'enabled': False,
                    'counters': [
                        {
                            'event_type': 'low_speed_limit',
                            'window_seconds': 2592000,
                        },
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Low is reached',
                                'title': 'Low',
                                'type': 'communication',
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613718879,
                    'event_type': 'low_speed_limit',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [],
            [],
        ),
        (
            'test_enabled_true',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'enabled': True,
                    'counters': [
                        {
                            'event_type': 'low_speed_limit',
                            'window_seconds': 2592000,
                        },
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Low is reached',
                                'title': 'Low',
                                'type': 'communication',
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613718879,
                    'event_type': 'low_speed_limit',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'low_speed_limit:2592000:0:1',
                    'event_timestamp': 1613718879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 39,
                    ),
                    'weight_index': 0,
                },
            ],
            [
                {
                    'idempotency_token': '4c8f67c459d8929d6f76be9b26e0ee56',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Low is reached',
                            'title': 'Low',
                        },
                    },
                },
            ],
        ),
    ],
)
async def test_enabled_rule(
        mock_taxi_driver_wall,
        yt_client,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        config_rules,
        data,
        expected_counters,
        expected_driver_wall_add_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_taxi_driver_wall('/internal/driver-wall/v1/add')
    async def _driver_wall_add(request):
        return web.json_response({'id': 'some_id'})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert (
        await db.antifraud_amayak_counters_mdb.find(
            {}, {'_id': False},
        ).to_list(None)
        == expected_counters
    )

    assert [
        _serialize_request(_driver_wall_add.next_call()['request'])
        for _ in range(_driver_wall_add.times_called)
    ] == expected_driver_wall_add_response


@pytest.mark.now('2021-02-21T23:58:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_counters,'
    'expected_driver_wall_add_response',
    [
        (
            'test_enabled_false',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {
                            'event_type': 'low_speed_limit',
                            'window_seconds': 2592000,
                        },
                    ],
                    'levels': [
                        {
                            'enabled': False,
                            'sanction': {
                                'text': 'Low is reached',
                                'title': 'Low',
                                'type': 'communication',
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613718879,
                    'event_type': 'low_speed_limit',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'low_speed_limit:2592000:0:1',
                    'event_timestamp': 1613718879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 39,
                    ),
                    'weight_index': 0,
                },
            ],
            [],
        ),
        (
            'test_enabled_true',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {
                            'event_type': 'low_speed_limit',
                            'window_seconds': 2592000,
                        },
                    ],
                    'levels': [
                        {
                            'enabled': True,
                            'sanction': {
                                'text': 'Low is reached',
                                'title': 'Low',
                                'type': 'communication',
                            },
                            'threshold': 1,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1613718879,
                    'event_type': 'low_speed_limit',
                    'driver_license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'udid': 'some_udid1',
                    'db_id': 'some_db_id1',
                    'driver_uuid': 'some_driver_uuid1',
                    'device_id': 'some_device_id1',
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'low_speed_limit:2592000:0:1',
                    'event_timestamp': 1613718879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 39,
                    ),
                    'weight_index': 0,
                },
            ],
            [
                {
                    'idempotency_token': '4c8f67c459d8929d6f76be9b26e0ee56',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Low is reached',
                            'title': 'Low',
                        },
                    },
                },
            ],
        ),
    ],
)
async def test_enabled_sanction(
        mock_taxi_driver_wall,
        yt_client,
        taxi_config,
        cron_context,
        db,
        comment,
        config,
        config_rules,
        data,
        expected_counters,
        expected_driver_wall_add_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_taxi_driver_wall('/internal/driver-wall/v1/add')
    async def _driver_wall_add(request):
        return web.json_response({'id': 'some_id'})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert (
        await db.antifraud_amayak_counters_mdb.find(
            {}, {'_id': False},
        ).to_list(None)
        == expected_counters
    )

    assert [
        _serialize_request(_driver_wall_add.next_call()['request'])
        for _ in range(_driver_wall_add.times_called)
    ] == expected_driver_wall_add_response


@pytest.mark.now('2021-02-21T23:58:04')
@pytest.mark.parametrize(
    'config,config_rules,config_input,data,expected_counters,'
    'expected_state,expected_driver_wall_add_response',
    [
        (
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {
                            'event_type': 'low_speed_limit',
                            'window_seconds': 2592000,
                        },
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'text': 'Low is reached',
                                'title': 'Low',
                                'type': 'communication',
                            },
                            'threshold': {'begin': 1, 'end': 999},
                        },
                    ],
                },
            },
            [
                {
                    'table_path': f'{YT_DIRECTORY_PATH}/input1',
                    'state_name': 'input1_cursor',
                },
                {
                    'enabled': False,
                    'table_path': f'{YT_DIRECTORY_PATH}/input2',
                    'state_name': 'input2_cursor',
                },
                {
                    'enabled': True,
                    'table_path': f'{YT_DIRECTORY_PATH}/input3',
                    'state_name': 'input3_cursor',
                },
            ],
            [
                {
                    'table_path': f'{YT_DIRECTORY_PATH}/input1',
                    'state_name': 'input1_cursor',
                    'data': [
                        {
                            'event_timestamp': 1613718879,
                            'event_type': 'low_speed_limit',
                            'driver_license_pd_id': (
                                '06e273a2f46a4f8ca5068ed1ad0b73a0'
                            ),
                            'udid': 'some_udid1',
                            'db_id': 'some_db_id1',
                            'driver_uuid': 'some_driver_uuid1',
                            'device_id': 'some_device_id1',
                        },
                    ],
                },
                {
                    'table_path': f'{YT_DIRECTORY_PATH}/input2',
                    'state_name': 'input2_cursor',
                    'data': [
                        {
                            'event_timestamp': 1613718879,
                            'event_type': 'low_speed_limit',
                            'driver_license_pd_id': (
                                '06e273a2f46a4f8ca5068ed1ad0b73a1'
                            ),
                            'udid': 'some_udid2',
                            'db_id': 'some_db_id2',
                            'driver_uuid': 'some_driver_uuid2',
                            'device_id': 'some_device_id2',
                        },
                    ],
                },
                {
                    'table_path': f'{YT_DIRECTORY_PATH}/input3',
                    'state_name': 'input3_cursor',
                    'data': [
                        {
                            'event_timestamp': 1613718879,
                            'event_type': 'low_speed_limit',
                            'driver_license_pd_id': (
                                '06e273a2f46a4f8ca5068ed1ad0b73a2'
                            ),
                            'udid': 'some_udid3',
                            'db_id': 'some_db_id3',
                            'driver_uuid': 'some_driver_uuid3',
                            'device_id': 'some_device_id3',
                        },
                    ],
                },
            ],
            [
                {
                    'additional_info': {
                        'db_id': 'some_db_id1',
                        'device_id': 'some_device_id1',
                        'driver_uuid': 'some_driver_uuid1',
                        'udid': 'some_udid1',
                    },
                    'counter_name': 'low_speed_limit:2592000:0:1',
                    'event_timestamp': 1613718879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 39,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {
                        'db_id': 'some_db_id3',
                        'device_id': 'some_device_id3',
                        'driver_uuid': 'some_driver_uuid3',
                        'udid': 'some_udid3',
                    },
                    'counter_name': 'low_speed_limit:2592000:0:1',
                    'event_timestamp': 1613718879,
                    'key': '06e273a2f46a4f8ca5068ed1ad0b73a2',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 2, 19, 7, 14, 39,
                    ),
                    'weight_index': 0,
                },
            ],
            {'input1_cursor': '1', 'input2_cursor': '0', 'input3_cursor': '1'},
            [
                {
                    'idempotency_token': '4c8f67c459d8929d6f76be9b26e0ee56',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id1_some_driver_uuid1'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a0'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Low is reached',
                            'title': 'Low',
                        },
                    },
                },
                {
                    'idempotency_token': '2a17245af81e5524ea26271614d5bbb6',
                    'json': {
                        'application': 'taximeter',
                        'drivers': [
                            {'driver': 'some_db_id3_some_driver_uuid3'},
                        ],
                        'id': (
                            'amayak_test_rule_06e273a2f46a4f8ca5068ed1ad0b73a2'
                        ),
                        'template': {
                            'alert': False,
                            'format': 'Raw',
                            'text': 'Low is reached',
                            'title': 'Low',
                        },
                    },
                },
            ],
        ),
    ],
)
async def test_multiple_input(
        mock_taxi_driver_wall,
        yt_client,
        taxi_config,
        cron_context,
        db,
        config,
        config_rules,
        config_input,
        data,
        expected_counters,
        expected_state,
        expected_driver_wall_add_response,
):
    config['AFS_CRON_AMAYAK_RULES'] = config_rules
    config['AFS_CRON_AMAYAK_MULTIPLE_INPUT_TABLES_CONFIG'] = config_input
    config['AFS_CRON_AMAYAK_MULTIPLE_INPUT_TABLES_ENABLED'] = True
    taxi_config.set_values(config)

    @mock_taxi_driver_wall('/internal/driver-wall/v1/add')
    async def _driver_wall_add(request):
        return web.json_response({'id': 'some_id'})

    master_pool = cron_context.pg.master_pool
    for data_item in data:
        await data_module.prepare_data(
            data_item['data'],
            yt_client,
            master_pool,
            data_item['state_name'],
            YT_DIRECTORY_PATH,
            data_item['table_path'],
        )
    await run_cron.main(['taxi_antifraud.crontasks.amayak', '-t', '0'])

    assert (
        await db.antifraud_amayak_counters_mdb.find(
            {}, {'_id': False},
        ).to_list(None)
        == expected_counters
    )

    assert await state.get_all_cron_state(master_pool) == expected_state

    assert [
        _serialize_request(_driver_wall_add.next_call()['request'])
        for _ in range(_driver_wall_add.times_called)
    ] == expected_driver_wall_add_response
