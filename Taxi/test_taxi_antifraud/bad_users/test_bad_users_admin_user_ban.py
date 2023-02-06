import datetime

import pytest

REQUEST_LOGIN = 'toropov'
TICKET = 'TAXIFRAUD-2254'


@pytest.fixture
def mock_secdist(simple_secdist):
    simple_secdist['settings_override']['STARTRACK_API_PROFILES'] = {
        'external': {
            'url': 'http://test-startrack-url-ext/',
            'org_id': 1,
            'oauth_token': 'some_other_startrack_token',
        },
    }
    return simple_secdist


@pytest.fixture
def mock_user_api(mockserver, load_json):
    @mockserver.json_handler('/user_api-api/user_phones/get')
    def _mock_user_api(request):
        user_phones = load_json('db_user_phones.json')
        phone_id = request.json['id']
        phone_doc = [x for x in user_phones if str(x['_id']) == phone_id][0]
        return {
            'id': str(phone_doc['_id']),
            'phone': phone_doc['phone'],
            'type': phone_doc['type'],
            'personal_phone_id': phone_doc['personal_phone_id'],
            'stat': {
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
            },
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
        }

    @mockserver.json_handler('/user_api-api//user_phones/by_personal/retrieve')
    def _retrieve_user_phone(request):
        user_phones = load_json('db_user_phones.json')
        found_phones = [
            x
            for x in user_phones
            if x['personal_phone_id'] == request.json['personal_phone_id']
            and x['type'] == request.json['type']
        ]
        if not found_phones:
            return mockserver.make_response(status=404)
        phone_doc = found_phones[0]
        return {'id': str(phone_doc['_id']), 'phone': phone_doc['phone']}

    @mockserver.json_handler('/user_api-api/users/search')
    async def _user_api(request):
        users = load_json('user_api_users.json')
        user_docs = [
            x for x in users if str(x['phone_id']) in request.json['phone_ids']
        ]
        return {
            'items': [
                {'id': str(x['_id']), 'device_id': x['device_id']}
                for x in user_docs
            ],
        }


@pytest.fixture
def mock_territories(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _list(request):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'code2': 'RU',
                    'name': 'Россия',
                    'phone_code': '7',
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '8',
                    'region_id': 0,
                },
            ],
        }


def get_collection_from_type(db, ban_type):
    if ban_type in ('phone', 'phone_id'):
        return db.antifraud_stat_phones
    if ban_type == 'user':
        return db.antifraud_stat_users
    if ban_type == 'device':
        return db.antifraud_stat_devices

    assert False
    return None


def _stat_type_by_ban_type(ban_type):
    return {
        'phone': 'phone_id',
        'phone_id': 'phone_id',
        'user': 'user_id',
        'device': 'device_id',
    }[ban_type]


def _check_equal_field(field1, dict1, dict2, field2=None):
    if field2 is None:
        field2 = field1
    if field1 in dict1:
        assert dict1[field1] == dict2[field2]
    else:
        assert field2 not in dict2


def _check_is_subdict(_dict, _sub_dict):
    return all(
        key in _dict and _dict[key] == _sub_dict[key] for key in _sub_dict
    )


@pytest.mark.config(
    AFS_STORE_USER_IDS_BLOCKS_SEPARATELY=True,
    AFS_USER_BAN_DEFAULT_DURATION={'days': 2, 'months': 3, 'years': 1},
    SVO_PHONE='+70000000000',
    SVO_USER_ID='297d52da8caf4b5f86abf4cbd58e5a88',
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
)
@pytest.mark.parametrize(
    'whitelists_enabled',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=pytest.mark.config(AFS_USER_BAN_ENABLE_WHITELISTS=True),
        ),
    ],
)
@pytest.mark.parametrize(
    'ban_data,code,entity_id,expected,exp_blocked_by_id',
    [
        ({}, 400, None, None, None),
        (
            {
                'type': 'phone',
                'value': '+7 (999) 666-33-21',
                'phone_type': 'yandex',
                'ticket': TICKET,
            },
            200,
            '5a09782d83b59b80e13ab0f1',
            {
                '_id': '5a09782d83b59b80e13ab0f1',
                'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'blocked_till': datetime.datetime(2018, 12, 12, 10, 0),
                'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'afs_block_reason': 'support_blocking',
                'block_reason': 'unknown reason',
                'blocked_times': 2,
                'block_initiator': {'login': REQUEST_LOGIN, 'ticket': TICKET},
            },
            {
                'value': '5a09782d83b59b80e13ab0f1',
                'type': 'phone_id',
                'until': datetime.datetime(2018, 12, 12, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
        ),
        (
            {
                'type': 'phone',
                'value': '+7 (000) 000-00-00',
                'phone_type': 'yandex',
                'ticket': TICKET,
            },
            403,
            None,
            None,
            None,
        ),
        (
            {
                'type': 'user',
                'value': '297d52da8caf4b5f86abf4cbd58e5a88',
                'ticket': TICKET,
            },
            403,
            None,
            None,
            None,
        ),
        (
            {
                'type': 'phone',
                'value': '7 999 666 33 21',
                'phone_type': 'yandex',
                'till': '2017-11-30T07:00:00.000Z',
                'ticket': TICKET,
            },
            200,
            '5a09782d83b59b80e13ab0f1',
            {
                '_id': '5a09782d83b59b80e13ab0f1',
                'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'block_reason': 'unknown reason',
                'afs_block_reason': 'support_blocking',
                'blocked_times': 2,
                'block_initiator': {'login': REQUEST_LOGIN, 'ticket': TICKET},
            },
            {
                'value': '5a09782d83b59b80e13ab0f1',
                'type': 'phone_id',
                'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
        ),
        (
            {
                'type': 'phone',
                'value': '8 999 111 22 35',
                'phone_type': 'yandex',
                'till': '2017-11-30T07:00:00.000Z',
                'reason': 'test_reason',
                'ticket': TICKET,
            },
            200,
            '5a09782d83b59b80e13ab0f5',
            {
                '_id': '5a09782d83b59b80e13ab0f5',
                'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'block_reason': 'test_reason',
                'blocked_times': 2,
                'block_initiator': {'login': REQUEST_LOGIN, 'ticket': TICKET},
                'total': 3,
                'complete': 1,
                'bad_driver_cancels': 2,
                'afs_block_reason': 'support_blocking',
                'multiorder_total': 1,
                'multiorder_complete': 1,
                'multiorder_blocked_till': datetime.datetime(
                    2018, 8, 31, 21, 0, 0,
                ),
                'multiorder_block_reason': 'bad gay',
                'multiorder_rehabilitated': datetime.datetime(
                    2019, 8, 31, 21, 0, 0,
                ),
                'multiorder_rehabilitate_reason': 'some reason',
                'multiorder_afs_rehabilitate_reason': 'some_reason',
                'multiorder_rehabilitate_initiator': 'support',
            },
            {
                'value': '5a09782d83b59b80e13ab0f5',
                'type': 'phone_id',
                'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
        ),
        (
            {
                'type': 'phone_id',
                'value': '5a09782d83b59b80e13ab0f3',
                'reason': 'test_reason',
                'till': '2017-11-30T07:00:00.000Z',
                'ticket': TICKET,
            },
            200,
            '5a09782d83b59b80e13ab0f3',
            {
                '_id': '5a09782d83b59b80e13ab0f3',
                'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'block_reason': 'test_reason',
                'afs_block_reason': 'support_blocking',
                'blocked_times': 3,
                'block_initiator': {'login': REQUEST_LOGIN, 'ticket': TICKET},
            },
            {
                'value': '5a09782d83b59b80e13ab0f3',
                'type': 'phone_id',
                'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
        ),
        (
            {
                'type': 'phone_id',
                'value': '5a09782d83b59b80e13ab0f3',
                'reason': 'test_reason',
                'till': '2017-11-30T07:00:00.000Z',
            },
            200,
            '5a09782d83b59b80e13ab0f3',
            {
                '_id': '5a09782d83b59b80e13ab0f3',
                'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'block_reason': 'test_reason',
                'afs_block_reason': 'support_blocking',
                'blocked_times': 3,
                'block_initiator': {'login': REQUEST_LOGIN},
            },
            {
                'value': '5a09782d83b59b80e13ab0f3',
                'type': 'phone_id',
                'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
        ),
        (
            {
                'type': 'user',
                'value': 'ban_user_id_test',
                'reason': 'test_reason',
                'till': '2017-11-30T07:00:00.000Z',
            },
            200,
            'ban_user_id_test',
            {
                '_id': 'ban_user_id_test',
                'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'block_reason': 'test_reason',
                'afs_block_reason': 'support_blocking',
                'blocked_times': 8,
                'block_initiator': {'login': REQUEST_LOGIN},
            },
            None,
        ),
        (
            {
                'type': 'device',
                'value': 'device_id_which_was_not_known',
                'reason': 'test_reason',
                'till': '2017-11-30T07:00:00.000Z',
                'support_template_reason': 'bad_bad_bad',
            },
            200,
            'device_id_which_was_not_known',
            {
                '_id': 'device_id_which_was_not_known',
                'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'block_reason': 'test_reason',
                'support_template_block_reason': 'bad_bad_bad',
                'afs_block_reason': 'support_blocking',
                'blocked_times': 1,
                'block_initiator': {'login': REQUEST_LOGIN},
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
            {
                'value': 'device_id_which_was_not_known',
                'type': 'device_id',
                'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
        ),
        (
            {
                'type': 'device',
                'value': 'test_ban_device_id',
                'reason': 'test_reason',
                'till': '2017-11-30T07:00:00.000Z',
                'ticket': TICKET,
            },
            200,
            'test_ban_device_id',
            {
                '_id': 'test_ban_device_id',
                'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'blocked_till': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'block_reason': 'test_reason',
                'afs_block_reason': 'support_blocking',
                'blocked_times': 3,
                'block_initiator': {'login': REQUEST_LOGIN, 'ticket': TICKET},
            },
            {
                'value': 'test_ban_device_id',
                'type': 'device_id',
                'until': datetime.datetime(2017, 11, 30, 7, 0, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
        ),
        (
            {
                'type': 'phone',
                'value': '+79068024832',
                'phone_type': 'all',
                'ticket': TICKET,
            },
            200,
            '582361500779cf3c0c11d081',
            {
                '_id': '582361500779cf3c0c11d081',
                'afs_block_reason': 'support_blocking',
                'block_initiator': {
                    'login': 'toropov',
                    'ticket': 'TAXIFRAUD-2254',
                },
                'block_reason': 'unknown reason',
                'block_time': datetime.datetime(2017, 9, 10, 10, 0),
                'blocked_till': datetime.datetime(2018, 12, 12, 10, 0),
                'blocked_times': 1,
                'created': datetime.datetime(2017, 9, 10, 10, 0),
                'updated': datetime.datetime(2017, 9, 10, 10, 0),
            },
            {
                'value': '582361500779cf3c0c11d081',
                'type': 'phone_id',
                'until': datetime.datetime(2018, 12, 12, 10, 0),
                'created': datetime.datetime(2017, 9, 10, 10, 0),
            },
        ),
    ],
)
@pytest.mark.now('2017-09-10 10:00:00')
async def test_ban_user(
        web_app_client,
        patch,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_user_api,  # pylint: disable=redefined-outer-name
        mock_territories,  # pylint: disable=redefined-outer-name
        db,
        ban_data,
        code,
        entity_id,
        expected,
        exp_blocked_by_id,
        whitelists_enabled,
):
    @patch('taxi_antifraud.bad_users.tickets.check_ticket')
    async def _check_ticket(*args, **kwargs):
        return True

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _mock_personal(data_type, request_value, *args, **kwargs):
        assert data_type == 'phones'
        personal_ids = {
            '+70000000000': '0000000000000000',
            '+79991112235': '1010101010101010',
            '+79996663321': '0101010101010101',
            '+79068024832': '738939302ca04e78af1c1dc3d975c5eb',
        }
        return {'id': personal_ids[request_value], 'phone': request_value}

    now = datetime.datetime.utcnow()

    response = await web_app_client.post(
        '/bad_users/v1/admin/user/ban/',
        json=ban_data,
        headers={'X-Yandex-Login': REQUEST_LOGIN},
    )
    assert response.status == code
    if expected:
        user_doc = await get_collection_from_type(
            db, ban_data['type'],
        ).find_one({'_id': entity_id})
        assert user_doc == expected

        events = await db.antifraud_block_events.find().to_list(None)
        assert len(events) == 1
        event = events[0]
        assert event['id'] == entity_id
        assert event['id_type'] == _stat_type_by_ban_type(ban_data['type'])
        assert event['event_type'] == 'block'
        assert event['created'] == now
        assert event['blocked_till'] == expected['blocked_till']
        assert event['initiator'] == expected['block_initiator']['login']
        _check_equal_field('ticket', expected['block_initiator'], event)
        _check_equal_field(
            'support_template_block_reason',
            expected,
            event,
            'template_reason',
        )
        assert event['internal_reason'] == expected['afs_block_reason']
        assert not event['is_multiorder']

    if exp_blocked_by_id is not None:
        blocked_by_id = list(
            (
                await db.antifraud_user_blocked_ids.find(
                    {}, {'_id': False, 'updated': False},
                ).to_list(None)
            ),
        )
        assert blocked_by_id == [exp_blocked_by_id]


@pytest.mark.config(
    AFS_STORE_USER_IDS_BLOCKS_SEPARATELY=True,
    SVO_PHONE='+70000000000',
    SVO_USER_ID='297d52da8caf4b5f86abf4cbd58e5a88',
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
)
@pytest.mark.parametrize(
    'whitelists_enabled',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=pytest.mark.config(AFS_USER_BAN_ENABLE_WHITELISTS=True),
        ),
    ],
)
@pytest.mark.parametrize(
    'ban_data,expected,ids,exp_blocked_by_id',
    [
        (
            {
                'type': 'all',
                'value': '+79998887766',
                'phone_type': 'yandex',
                'ticket': TICKET,
                'support_template_reason': 'bad',
            },
            {
                'updated': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'blocked_till': datetime.datetime(2018, 3, 10, 10, 0, 0),
                'block_time': datetime.datetime(2017, 9, 10, 10, 0, 0),
                'afs_block_reason': 'support_blocking',
                'block_reason': 'unknown reason',
                'block_initiator': {'login': REQUEST_LOGIN, 'ticket': TICKET},
                'support_template_block_reason': 'bad',
            },
            {
                'users': [
                    'user_shuld_be_blocked_all_ids_1',
                    'user_shuld_be_blocked_all_ids_2',
                ],
                'phones': ['ababdcfeababababab3ababa'],
                'devices': [
                    'device_shuld_be_blocked_all_ids_1',
                    'device_shuld_be_blocked_all_ids_2',
                ],
            },
            [
                {
                    'value': 'ababdcfeababababab3ababa',
                    'type': 'phone_id',
                    'until': datetime.datetime(2018, 3, 10, 10, 0),
                    'created': datetime.datetime(2017, 9, 10, 10, 0),
                },
                {
                    'value': 'device_shuld_be_blocked_all_ids_1',
                    'type': 'device_id',
                    'until': datetime.datetime(2018, 3, 10, 10, 0),
                    'created': datetime.datetime(2017, 9, 10, 10, 0),
                },
                {
                    'value': 'device_shuld_be_blocked_all_ids_2',
                    'type': 'device_id',
                    'until': datetime.datetime(2018, 3, 10, 10, 0),
                    'created': datetime.datetime(2017, 9, 10, 10, 0),
                },
            ],
        ),
    ],
)
@pytest.mark.now('2017-09-10 10:00:00')
async def test_ban_all_ids(
        web_app_client,
        patch,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_user_api,  # pylint: disable=redefined-outer-name
        mock_territories,  # pylint: disable=redefined-outer-name
        db,
        ban_data,
        ids,
        expected,
        exp_blocked_by_id,
        whitelists_enabled,
):
    @patch('taxi_antifraud.bad_users.tickets.check_ticket')
    async def _check_ticket(*args, **kwargs):
        return True

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _mock_personal(
            data_type, request_value, validate=True, log_extra=None,
    ):
        assert data_type == 'phones'
        personal_ids = {'+79998887766': '9876543210123456'}
        return {
            'id': personal_ids.get(request_value, 'personal_id'),
            'phone': request_value,
        }

    now = datetime.datetime.utcnow()
    response = await web_app_client.post(
        '/bad_users/v1/admin/user/ban/',
        json=ban_data,
        headers={'X-Yandex-Login': REQUEST_LOGIN},
    )
    assert response.status == 200

    def _check_events(event, id_type):
        assert event['id_type'] == id_type
        assert event['event_type'] == 'block'
        assert event['created'] == now
        assert event['blocked_till'] == expected['blocked_till']
        assert event['reason'] == expected['block_reason']
        _check_equal_field(
            'support_template_block_reason',
            expected,
            event,
            'template_reason',
        )
        assert event['internal_reason'] == expected['afs_block_reason']
        assert event['initiator'] == expected['block_initiator']['login']
        _check_equal_field('ticket', expected['block_initiator'], event)
        assert not event['is_multiorder']

    for _id in ids['phones']:
        phone_result = await db.antifraud_stat_phones.find_one({'_id': _id})
        assert _check_is_subdict(phone_result, expected)

        phone_events = await db.antifraud_block_events.find(
            {'id': _id},
        ).to_list(None)
        assert len(phone_events) == 1
        phone_event = phone_events[0]
        _check_events(phone_event, 'phone_id')

    for _id in ids['users']:
        user_result = await db.antifraud_stat_users.find_one({'_id': _id})
        assert _check_is_subdict(user_result, expected)

        events = await db.antifraud_block_events.find({'id': _id}).to_list(
            None,
        )
        assert len(phone_events) == 1
        event = events[0]
        _check_events(event, 'user_id')

    for _id in ids['devices']:
        device_result = await db.antifraud_stat_devices.find_one({'_id': _id})
        assert _check_is_subdict(device_result, expected)

        events = await db.antifraud_block_events.find({'id': _id}).to_list(
            None,
        )
        assert len(phone_events) == 1
        event = events[0]
        _check_events(event, 'device_id')
    if exp_blocked_by_id is not None:
        blocked_by_id = list(
            (
                await db.antifraud_user_blocked_ids.find(
                    {}, {'_id': False, 'updated': False},
                ).to_list(None)
            ),
        )
        assert sorted(
            blocked_by_id, key=lambda k: (k['value'], k['type']),
        ) == sorted(exp_blocked_by_id, key=lambda k: (k['value'], k['type']))


@pytest.mark.config(
    AFS_STORE_USER_IDS_BLOCKS_SEPARATELY=True,
    SVO_PHONE='+70000000000',
    SVO_USER_ID='297d52da8caf4b5f86abf4cbd58e5a88',
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    AFS_USER_BAN_ENABLE_WHITELISTS=True,
)
@pytest.mark.parametrize(
    'ban_data, stat_id',
    [
        (
            {
                'type': 'phone',
                'value': '+7 (999) 666-55-55',
                'phone_type': 'yandex',
                'ticket': TICKET,
            },
            '582361500779cf3c0c11d082',
        ),
        (
            {
                'type': 'phone_id',
                'value': '582361500779cf3c0c11d082',
                'reason': 'test_reason',
                'till': '2017-11-30T07:00:00.000Z',
                'ticket': TICKET,
            },
            '582361500779cf3c0c11d082',
        ),
        (
            {
                'type': 'device',
                'value': 'whitelisted_device_id_1',
                'reason': 'test_reason',
                'till': '2017-11-30T07:00:00.000Z',
                'ticket': TICKET,
            },
            'whitelisted_device_id_1',
        ),
    ],
)
@pytest.mark.now('2017-09-10 10:00:00')
async def test_not_ban_ids_in_whitelists(
        web_app_client,
        patch,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_user_api,  # pylint: disable=redefined-outer-name
        mock_territories,  # pylint: disable=redefined-outer-name
        db,
        ban_data,
        stat_id,
):
    @patch('taxi_antifraud.bad_users.tickets.check_ticket')
    async def _check_ticket(*args, **kwargs):
        return True

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _mock_personal(
            data_type, request_value, validate=True, log_extra=None,
    ):
        assert data_type == 'phones'
        personal_ids = {'+79996665555': 'whitelisted_personal_phone_id_1'}
        return {
            'id': personal_ids.get(request_value, 'personal_id'),
            'phone': request_value,
        }

    collection = get_collection_from_type(db, ban_data['type'])
    stat_before = await collection.find_one({'_id': stat_id})

    response = await web_app_client.post(
        '/bad_users/v1/admin/user/ban/',
        json=ban_data,
        headers={'X-Yandex-Login': REQUEST_LOGIN},
    )
    assert response.status == 200

    assert await collection.find_one({'_id': stat_id}) == stat_before


@pytest.mark.config(
    AFS_STORE_USER_IDS_BLOCKS_SEPARATELY=True,
    SVO_PHONE='+70000000000',
    SVO_USER_ID='297d52da8caf4b5f86abf4cbd58e5a88',
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    AFS_USER_BAN_ENABLE_WHITELISTS=True,
)
@pytest.mark.parametrize(
    'ban_data, whitelisted, not_whitelisted',
    [
        (
            {
                'type': 'all',
                'value': '+7 (333) 444-55-55',
                'phone_type': 'yandex',
                'ticket': TICKET,
                'support_template_reason': 'bad',
            },
            {
                'whitelisted_device_id_2',
                '5a0978f8e76f8e7f613ab0a6',  # phone id
            },
            {
                'not_whitelisted_device_id_2',
                'test_whitelists_user_id_1',
                'test_whitelists_user_id_2',
            },
        ),
    ],
)
@pytest.mark.now('2017-09-10 10:00:00')
async def test_ban_all_ids_filtered_by_whitelists(
        web_app_client,
        patch,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_user_api,  # pylint: disable=redefined-outer-name
        mock_territories,  # pylint: disable=redefined-outer-name
        db,
        ban_data,
        whitelisted,
        not_whitelisted,
):
    @patch('taxi_antifraud.bad_users.tickets.check_ticket')
    async def _check_ticket(*args, **kwargs):
        return True

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _mock_personal(
            data_type, request_value, validate=True, log_extra=None,
    ):
        assert data_type == 'phones'
        personal_ids = {'+73334445555': 'whitelisted_personal_phone_id_2'}
        return {
            'id': personal_ids.get(request_value, 'personal_id'),
            'phone': request_value,
        }

    response = await web_app_client.post(
        '/bad_users/v1/admin/user/ban/',
        json=ban_data,
        headers={'X-Yandex-Login': REQUEST_LOGIN},
    )
    assert response.status == 200

    for _id in whitelisted:
        assert await db.antifraud_block_events.find_one({'id': _id}) is None

    for _id in not_whitelisted:
        assert await db.antifraud_block_events.find_one({'id': _id})
