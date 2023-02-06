import datetime

from aiohttp import web
import pytest


from taxi_antifraud.crontasks import amayak_users
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import data as data_module
from test_taxi_antifraud.cron.utils import mock
from test_taxi_antifraud.cron.utils import state

YT_DIRECTORY_PATH = '//home/taxi-fraud/unittests/amayak_users'
YT_TABLE_PATH = YT_DIRECTORY_PATH + '/input'

DEFAULT_CONFIG: dict = {
    'AFS_CRON_AMAYAK_USERS_BAN_SANCTION_ENABLED': True,
    'AFS_CRON_AMAYAK_USERS_ENABLED': True,
    'AFS_CRON_AMAYAK_USERS_INPUT_TABLE_SUFFIX': 'amayak_users/input',
    'AFS_CRON_AMAYAK_USERS_SLEEP_TIME_SECONDS': 0.01,
    'AFS_CRON_AMAYAK_USERS_TAGGING_SANCTION_ENABLED': True,
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
        assert request_id.endswith('_pd_id')
        return {'phone': request_id[:-6]}


@pytest.mark.now('2021-08-26T16:27:04')
@pytest.mark.parametrize(
    'config,config_rules,data,expected_amayak_counters',
    [
        (
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'cashrun', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'type': 'tagging',
                                'append': [
                                    {
                                        'name': 'forbid_cash_orders',
                                        'ttl_seconds': 86400,
                                    },
                                ],
                                'remove': [],
                            },
                            'threshold': 100000,  # effectively disable it
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1629908879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1629908979,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id2',
                },
                {
                    'event_timestamp': 1629918879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id3',
                },
                {
                    'event_timestamp': 1629928879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id4',
                },
                {
                    'event_timestamp': 1629938879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id5',
                },
                {
                    'event_timestamp': 1629948879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id6',
                },
            ],
            [
                {
                    'additional_info': {'device_id': 'some_device_id1'},
                    'counter_name': 'cashrun:86400:0:1',
                    'event_timestamp': 1629908879,
                    'key': '+79001234567_pd_id',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 7, 27, 16, 27, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {'device_id': 'some_device_id2'},
                    'counter_name': 'cashrun:86400:0:1',
                    'event_timestamp': 1629908979,
                    'key': '+79001234567_pd_id',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 7, 27, 16, 29, 39,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {'device_id': 'some_device_id3'},
                    'counter_name': 'cashrun:86400:0:1',
                    'event_timestamp': 1629918879,
                    'key': '+79001234567_pd_id',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 7, 27, 19, 14, 39,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {'device_id': 'some_device_id4'},
                    'counter_name': 'cashrun:86400:0:1',
                    'event_timestamp': 1629928879,
                    'key': '+79001234567_pd_id',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 7, 27, 22, 1, 19,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {'device_id': 'some_device_id5'},
                    'counter_name': 'cashrun:86400:0:1',
                    'event_timestamp': 1629938879,
                    'key': '+79001234567_pd_id',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 7, 28, 0, 47, 59,
                    ),
                    'weight_index': 0,
                },
                {
                    'additional_info': {'device_id': 'some_device_id6'},
                    'counter_name': 'cashrun:86400:0:1',
                    'event_timestamp': 1629948879,
                    'key': '+79001234567_pd_id',
                    'timestamp_for_expiration': datetime.datetime(
                        2021, 7, 28, 3, 34, 39,
                    ),
                    'weight_index': 0,
                },
            ],
        ),
    ],
)
async def test_cron(
        yt_apply,
        yt_client,
        taxi_config,
        cron_context,
        db,
        config,
        config_rules,
        data,
        expected_amayak_counters,
):
    config['AFS_CRON_AMAYAK_USERS_RULES'] = config_rules
    taxi_config.set_values(config)

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        amayak_users.CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )

    await run_cron.main(['taxi_antifraud.crontasks.amayak_users', '-t', '0'])

    assert (
        await db.antifraud_amayak_users_counters.find(
            {}, {'_id': False},
        ).to_list(None)
        == expected_amayak_counters
    )

    assert await state.get_all_cron_state(master_pool) == {
        amayak_users.CURSOR_STATE_NAME: str(len(data)),
    }


@pytest.mark.now('2021-08-26T16:48:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_ban_users_response',
    [
        (
            'test_regular_ban',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'cashrun', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason': 'some reason',
                                'type': 'ban',
                                'ban_related_ids': False,
                            },
                            'threshold': 5,
                        },
                        {
                            'sanction': {
                                'duration_seconds': 86400,
                                'reason': 'some another reason',
                                'type': 'ban',
                                'ban_related_ids': False,
                            },
                            'threshold': 6,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1629908879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1629908979,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id2',
                },
                {
                    'event_timestamp': 1629918879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id3',
                },
                {
                    'event_timestamp': 1629928879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id4',
                },
                {
                    'event_timestamp': 1629938879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id5',
                },
                {
                    'event_timestamp': 1629948879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id6',
                },
            ],
            [
                {
                    'phone_type': 'all',
                    'reason': 'some reason',
                    'till': '2021-08-26T20:48:04+03:00',
                    'type': 'phone',
                    'value': '+79001234567',
                },
                {
                    'phone_type': 'all',
                    'reason': 'some another reason',
                    'till': '2021-08-27T19:48:04+03:00',
                    'type': 'phone',
                    'value': '+79001234567',
                },
            ],
        ),
        (
            'test_ban_all_ids',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'cashrun', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason': 'some reason',
                                'type': 'ban',
                                'ban_related_ids': False,
                            },
                            'threshold': 1,
                        },
                        {
                            'sanction': {
                                'duration_seconds': 3600,
                                'reason': 'some other reason',
                                'type': 'ban',
                                'ban_related_ids': True,
                            },
                            'threshold': 2,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1629908879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1629908979,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id2',
                },
            ],
            [
                {
                    'phone_type': 'all',
                    'reason': 'some reason',
                    'till': '2021-08-26T20:48:04+03:00',
                    'type': 'phone',
                    'value': '+79001234567',
                },
                {
                    'phone_type': 'all',
                    'reason': 'some other reason',
                    'till': '2021-08-26T20:48:04+03:00',
                    'type': 'all',
                    'value': '+79001234567',
                },
            ],
        ),
    ],
)
async def test_ban(
        mock_personal,  # pylint: disable=redefined-outer-name
        mock_antifraud_py,
        yt_apply,
        yt_client,
        taxi_config,
        cron_context,
        comment,
        config,
        config_rules,
        data,
        expected_ban_users_response,
):
    config['AFS_CRON_AMAYAK_USERS_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_antifraud_py('/bad_users/v1/admin/user/ban')
    async def _ban_user(request):
        return web.json_response({})

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        amayak_users.CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )
    await run_cron.main(['taxi_antifraud.crontasks.amayak_users', '-t', '0'])

    assert mock.get_requests(_ban_user) == expected_ban_users_response


@pytest.mark.now('2021-08-26T16:48:04')
@pytest.mark.parametrize(
    'comment,config,config_rules,data,expected_tags_response',
    [
        (
            'test_regular_tagging',
            DEFAULT_CONFIG,
            {
                'test_rule': {
                    'counters': [
                        {'event_type': 'cashrun', 'window_seconds': 86400},
                    ],
                    'levels': [
                        {
                            'sanction': {
                                'type': 'tagging',
                                'append': [
                                    {
                                        'name': 'forbid_cash_orders',
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
                                        'name': 'forbid_all_orders',
                                        'ttl_seconds': 86400,
                                    },
                                    {'name': 'got_2'},
                                ],
                                'remove': [{'name': 'forbid_cash_orders'}],
                            },
                            'threshold': 2,
                        },
                    ],
                },
            },
            [
                {
                    'event_timestamp': 1629908879,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id1',
                },
                {
                    'event_timestamp': 1629908979,
                    'event_type': 'cashrun',
                    'user_phone_pd_id': '+79001234567_pd_id',
                    'device_id': 'some_device_id2',
                },
            ],
            [
                {
                    'idempotency_token': '4bf1827f34e1ba0f2b4f4ee66422dca6',
                    'json': {
                        'append': [
                            {
                                'entity_type': 'personal_phone_id',
                                'tags': [
                                    {
                                        'entity': '+79001234567_pd_id',
                                        'name': 'forbid_cash_orders',
                                        'ttl': 86400,
                                    },
                                ],
                            },
                        ],
                        'provider_id': 'antifraud',
                    },
                },
                {
                    'idempotency_token': 'a5cd77a18cf5ac37961de81652fb1c6a',
                    'json': {
                        'append': [
                            {
                                'entity_type': 'personal_phone_id',
                                'tags': [
                                    {
                                        'entity': '+79001234567_pd_id',
                                        'name': 'forbid_all_orders',
                                        'ttl': 86400,
                                    },
                                    {
                                        'entity': '+79001234567_pd_id',
                                        'name': 'got_2',
                                    },
                                ],
                            },
                        ],
                        'provider_id': 'antifraud',
                        'remove': [
                            {
                                'entity_type': 'personal_phone_id',
                                'tags': [
                                    {
                                        'entity': '+79001234567_pd_id',
                                        'name': 'forbid_cash_orders',
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
        mock_passenger_tags,
        yt_apply,
        yt_client,
        taxi_config,
        cron_context,
        comment,
        config,
        config_rules,
        data,
        expected_tags_response,
):
    config['AFS_CRON_AMAYAK_USERS_RULES'] = config_rules
    taxi_config.set_values(config)

    @mock_passenger_tags('/v2/upload')
    async def _upload(request):
        return {'status': 'ok'}

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(
        master_pool, amayak_users.CURSOR_STATE_NAME,
    )
    yt_client.create(
        'table', path=YT_TABLE_PATH, recursive=True, ignore_existing=True,
    )
    yt_client.write_table(YT_TABLE_PATH, data)
    await run_cron.main(['taxi_antifraud.crontasks.amayak_users', '-t', '0'])

    assert [
        _serialize_request(_upload.next_call()['request'])
        for _ in range(_upload.times_called)
    ] == expected_tags_response
