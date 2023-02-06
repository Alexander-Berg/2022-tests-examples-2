import datetime
from typing import List
from typing import NamedTuple
from typing import Optional

import pytest

NOW = datetime.datetime(
    2018,
    6,
    27,
    15,
    15,
    0,
    tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
)
NOW_TZLESS = datetime.datetime.utcfromtimestamp(NOW.timestamp())

NOW_GMT_STR = 'Wed, 27 Jun 2018 12:15:00 GMT'

LOG_RECORD_BASE = (
    'tskv',
    'tskv_format=yandex-taxi-adjust-dev-ev-log',
    'timestamp=%d' % NOW.timestamp(),
    'h_date=%s' % NOW_GMT_STR,
)


@pytest.mark.now(NOW.isoformat())
async def test_log_event(web_app_client, event_logger_logs):
    multi_dict_stub = [('a', 'b'), ('c', 'd'), ('c', 'e')]
    resp = await web_app_client.get(
        '/event', params=multi_dict_stub, headers=multi_dict_stub,
    )
    assert resp.status == 200
    assert (await resp.text()) == ''

    expected_log = LOG_RECORD_BASE + (
        'method=event',
        'a_a=b',
        'a_c=[\'d\', \'e\']',
    )
    assert len(event_logger_logs) == 1
    actual_log = event_logger_logs[0].split('\t')
    assert len(actual_log) == len(expected_log)
    assert set(actual_log) == set(expected_log)


class Params(NamedTuple):
    main_device_id_key: Optional[str]
    device_id_keys: Optional[List[str]]
    device_id: Optional[str]
    user_id_key: Optional[str]
    user_id: Optional[str]
    app_token: Optional[str]
    platform: Optional[str]
    expected_device_type: Optional[str]
    error: bool


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(ADJUST_SWITCH_TO_NEW_POSTBACK_QUERY=True)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                main_device_id_key='android_id',
                device_id_keys=['android_id'],
                device_id='12',
                user_id_key='uid',
                user_id='09',
                app_token='55ug2ntb3uzf',
                platform='android',
                expected_device_type='android',
                error=False,
            ),
            id='ok',
        ),
        pytest.param(
            Params(
                main_device_id_key='gps_adid',
                device_id_keys=['gps_adid', 'android_id'],
                device_id='12',
                user_id_key='uid',
                user_id='09',
                app_token='55ug2ntb3uzf',
                platform='android',
                expected_device_type='android',
                error=False,
            ),
            id='android_device_ids_ok',
        ),
        pytest.param(
            Params(
                main_device_id_key='idfa',
                device_id_keys=['idfa'],
                device_id='12',
                user_id_key='user_id',
                user_id='09',
                app_token='cs75zaz26h8x',
                platform='ios',
                expected_device_type='iOs',
                error=False,
            ),
            id='ios_device_ids_ok',
        ),
        pytest.param(
            Params(
                main_device_id_key='android_id',
                device_id_keys=None,
                device_id=None,
                user_id_key='uid',
                user_id='09',
                app_token='55ug2ntb3uzf',
                platform='android',
                expected_device_type='android',
                error=True,
            ),
            id='no_device_id_error',
        ),
        pytest.param(
            Params(
                main_device_id_key='android_id',
                device_id_keys=['android_id'],
                device_id='12',
                user_id_key=None,
                user_id=None,
                app_token='55ug2ntb3uzf',
                platform='android',
                expected_device_type='android',
                error=True,
            ),
            id='no_user_id_error',
        ),
        pytest.param(
            Params(
                main_device_id_key='android_id',
                device_id_keys=['android_id'],
                device_id='12',
                user_id_key='uid',
                user_id='09',
                app_token=None,
                platform='android',
                expected_device_type='android',
                error=True,
            ),
            id='no_app_token_error',
        ),
    ],
)
async def test_postback(params, web_app_client, event_logger_logs, db):
    query = [('a', 'b')]
    if params.device_id_keys and params.device_id:
        for key in params.device_id_keys:
            query.append((key, params.device_id))
    if params.user_id_key:
        query.append((params.user_id_key, params.user_id))

    if params.app_token:
        query.append(('app_token', params.app_token))

    adjust_id = 'adjust_id'
    query.append(('adid', adjust_id))

    if params.platform:
        query.append(('ya_platform', params.platform))

    resp = await web_app_client.get('/postback', params=query)
    assert resp.status == 200

    if params.error:
        assert event_logger_logs == []
        assert await db.adjust_users.count({}) == 0
    else:
        expected_log = LOG_RECORD_BASE + (
            'method=postback',
            'user_id=%s' % params.user_id,
            'device_id=%s' % params.device_id,
            'device_type=%s' % params.expected_device_type,
            'device_id_key=%s' % params.main_device_id_key,
            'adjust_id=%s' % adjust_id,
            'app_token=%s' % params.app_token,
            *('a_%s=%s' % (key, value) for key, value in query),
        )
        assert len(event_logger_logs) == 1
        actual_log = event_logger_logs[0].split('\t')
        assert set(actual_log) == set(expected_log)
        assert len(actual_log) == len(expected_log)
        added_users = await db.adjust_users.find(
            {'uid': params.user_id},
        ).to_list(None)
        assert len(added_users) == 1

        user = added_users[0]
        assert user == {
            '_id': added_users[0]['_id'],
            'uid': params.user_id,
            't': params.expected_device_type,
            'i': params.device_id,
            'k': params.main_device_id_key,
            'adid': adjust_id,
            'a': params.app_token,
            'updated': NOW_TZLESS,
        }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ADJUST_SEND_WITHOUT_DEVICE_ID=True,
    ADJUST_SWITCH_TO_NEW_POSTBACK_QUERY=True,
)
async def test_postback_save_without_device_id(
        web_app_client, event_logger_logs, db,
):
    user_id = '09'
    query = [
        ('a', 'b'),
        ('uid', user_id),
        ('adid', 'adjust_id'),
        ('app_token', '55ug2ntb3uzf'),
        ('ya_platform', 'android'),
    ]

    resp = await web_app_client.get('/postback', params=query)
    assert resp.status == 200

    expected_log = LOG_RECORD_BASE + (
        'method=postback',
        'user_id=%s' % user_id,
        'device_id=%s' % 'None',
        'device_id_key=%s' % 'None',
        'device_type=%s' % 'android',
        'adjust_id=%s' % 'adjust_id',
        'app_token=%s' % '55ug2ntb3uzf',
        *('a_%s=%s' % (key, value) for key, value in query),
    )
    assert len(event_logger_logs) == 1
    actual_log = event_logger_logs[0].split('\t')
    assert set(actual_log) == set(expected_log)
    assert len(actual_log) == len(expected_log)
    added_users = await db.adjust_users.find({'uid': user_id}).to_list(None)
    assert len(added_users) == 1
    user = added_users[0]

    assert user == {
        '_id': added_users[0]['_id'],
        'uid': user_id,
        't': 'android',
        'adid': 'adjust_id',
        'a': '55ug2ntb3uzf',
        'updated': NOW_TZLESS,
    }


@pytest.mark.parametrize(
    'app_token_existed', [pytest.param(True), pytest.param(False)],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(ADJUST_SWITCH_TO_NEW_POSTBACK_QUERY=True)
async def test_app_token_migration(
        app_token_existed, web_app_client, event_logger_logs, db,
):
    user_id = '09'
    app_token = '55ug2ntb3uzf'
    old_device_id = '12'
    new_device_id = '13'

    document = {
        'uid': user_id,
        't': 'android',
        'k': 'android_id',
        'i': old_device_id,
        'adid': 'adjust_id',
    }

    if app_token_existed:
        document['a'] = app_token

    await db.adjust_users.insert(document)

    query = [
        ('a', 'b'),
        ('uid', user_id),
        ('adid', 'adjust_id'),
        ('app_token', app_token),
        ('ya_platform', 'android'),
        ('android_id', new_device_id),
    ]

    resp = await web_app_client.get('/postback', params=query)
    assert resp.status == 200

    expected_log = LOG_RECORD_BASE + (
        'method=postback',
        'user_id=%s' % user_id,
        'device_id=%s' % new_device_id,
        'device_id_key=%s' % 'android_id',
        'device_type=%s' % 'android',
        'adjust_id=%s' % 'adjust_id',
        'app_token=%s' % app_token,
        *('a_%s=%s' % (key, value) for key, value in query),
    )
    assert len(event_logger_logs) == 1
    actual_log = event_logger_logs[0].split('\t')
    assert set(actual_log) == set(expected_log)
    assert len(actual_log) == len(expected_log)
    adjust_users = await db.adjust_users.find({'uid': user_id}).to_list(None)
    assert len(adjust_users) == 1
    user = adjust_users[0]

    assert user == {
        '_id': adjust_users[0]['_id'],
        'uid': user_id,
        't': 'android',
        'adid': 'adjust_id',
        'k': 'android_id',
        'i': new_device_id,
        'a': app_token,
        'updated': NOW_TZLESS,
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(ADJUST_SEND_WITHOUT_DEVICE_ID=True)
async def test_not_saving_data_without_both_ids(
        web_app_client, event_logger_logs, db,
):
    query = [('a', 'b'), ('uid', '09')]

    resp = await web_app_client.get('/postback', params=query)
    assert resp.status == 200

    assert event_logger_logs == []
    assert await db.adjust_users.count({}) == 0


def _get_user_id_keys_config(platform_names: List[str]):
    return {
        'default': {
            'uuid': {'platform_names': ['iOs']},
            'user_id': {'platform_names': ['android']},
        },
        'SMZ_driver_registered': {
            'driver_id': {'platform_names': platform_names},
        },
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ADJUST_SWITCH_TO_NEW_POSTBACK_QUERY=True,
    ADJUST_SEND_WITHOUT_DEVICE_ID=True,
)
@pytest.mark.parametrize(
    'ya_platform, device_type_reference',
    [
        pytest.param(
            'android',
            'android',
            id='ya_platform_name is passed',
            marks=[
                pytest.mark.config(
                    ADJUST_POSTBACK_USER_ID_KEY_NAMES=_get_user_id_keys_config(
                        ['iOs'],
                    ),
                ),
            ],
        ),
        pytest.param(
            None,
            None,
            id='user id doesn\'t identify platform',
            marks=[
                pytest.mark.config(
                    ADJUST_POSTBACK_USER_ID_KEY_NAMES=_get_user_id_keys_config(
                        [],
                    ),
                ),
            ],
        ),
        pytest.param(
            None,
            'android',
            id='user id identifies one platform',
            marks=[
                pytest.mark.config(
                    ADJUST_POSTBACK_USER_ID_KEY_NAMES=_get_user_id_keys_config(
                        ['android'],
                    ),
                ),
            ],
        ),
        pytest.param(
            None,
            None,
            id='user id identifies several platforms',
            marks=[
                pytest.mark.config(
                    ADJUST_POSTBACK_USER_ID_KEY_NAMES=_get_user_id_keys_config(
                        ['android', 'iOs'],
                    ),
                ),
            ],
        ),
    ],
)
async def test_custom_user_id(
        taxi_adjust_py3_web,
        web_app_client,
        taxi_config,
        ya_platform,
        device_type_reference,
        db,
):
    driver_id = '09'
    query = [
        ('driver_id', driver_id),
        ('adid', 'adjust_id'),
        ('app_token', '55ug2ntb3uzf'),
        ('request_type', 'SMZ_driver_registered'),
    ]

    if ya_platform is not None:
        query.append(('ya_platform', ya_platform))

    resp = await web_app_client.get('/postback', params=query)
    assert resp.status == 200

    added_users = await db.adjust_users.find({'uid': driver_id}).to_list(None)

    if device_type_reference is None:
        assert not added_users
    else:
        assert len(added_users) == 1
        assert added_users[0] == {
            '_id': added_users[0]['_id'],
            'uid': driver_id,
            't': device_type_reference,
            'a': '55ug2ntb3uzf',
            'adid': 'adjust_id',
            'updated': NOW_TZLESS,
        }
