import bson
import datetime
import operator

import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import userapi

from taxi.internal import user_antifraud_engine


@pytest.fixture
def mock_user_phones_factory(patch, inject_user_api_token):
    def impl(phone, type='yandex', phone_id=str(bson.ObjectId()),
             personal_id='personal_id'):
        @patch('taxi.external.userapi.create_user_phone')
        @async.inline_callbacks
        def mock_user_phones(req_phone, *args, **kwargs):
            assert req_phone == phone
            response = {
                'id': phone_id,
                'phone': phone,
                'type': type,
                'personal_phone_id': personal_id,
                'created': '2019-02-01T13:00:00+0000',
                'updated': '2019-02-01T13:00:00+0000',
                'stat': {
                    'big_first_discounts': 0,
                    'complete': 0,
                    'complete_card': 0,
                    'complete_apple': 0,
                    'complete_google': 0
                },
                'is_loyal': False,
                'is_yandex_staff': False,
                'is_taxi_staff': False,
            }

            yield
            async.return_value(response)

        return mock_user_phones

    return impl


@pytest.mark.config(USER_API_USE_USER_PHONES_CREATION_PY2=True)
@pytest.inline_callbacks
def test_create_user_api(mock_user_phones_factory):
    phone_number = '+72222222222'
    phone_type = 'yandex'
    phone_id = bson.ObjectId('1d239d76132553e6899b21ff')
    mock_user_phones_factory(phone_number, phone_type, str(phone_id))

    new_phone = yield userapi.create_user_phone(phone_number,
                                                phone_type)

    assert new_phone == {
            '_id': phone_id,
            'phone': phone_number,
            'type': phone_type,
            'personal_phone_id': 'personal_id',
            'created': datetime.datetime(2019, 2, 1, 13, 0, 0),
            'updated': datetime.datetime(2019, 2, 1, 13, 0, 0),
            'stat': {
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0
            },
            'loyal': False,
            'yandex_staff': False,
            'taxi_staff': False,
        }


@pytest.mark.now('2020-01-10 10:00:00')
@pytest.mark.config(AFS_STORE_USER_IDS_BLOCKS_SEPARATELY=True)
@pytest.inline_callbacks
def test_antifraud_block_phone(patch_user_factory):
    personal_phone_id = "1010101010101010"
    phone = '+79991234567'
    phone_type = 'yandex'
    phone_id = '1d239d76132553e6899b21ea'
    time_ref = datetime.datetime(2019, 2, 2, 13, 0, 0)
    till = datetime.datetime(2020, 2, 1, 3, 0, 0)

    result = yield user_antifraud_engine.block_phone(
        phone, phone_type, time_ref, till, reason='some reason',
        support_template_reason='reason', login='stalin', ticket='T123',
        personal_phone_id=personal_phone_id)
    assert result
    blocked = yield db.antifraud_stat_phones.find_one({'_id': phone_id})

    assert blocked['updated'] == time_ref
    assert blocked['created'] == time_ref
    assert blocked['block_time'] == time_ref
    assert blocked['blocked_till'] == till
    assert blocked['block_reason'] == 'some reason'
    assert blocked['afs_block_reason'] == 'support_blocking'
    assert blocked['blocked_times'] == 1
    assert blocked['block_initiator'] == {
        'login': 'stalin',
        'ticket': 'T123',
    }
    assert blocked['support_template_block_reason']

    blocked_by_id = yield db.antifraud_user_blocked_ids.find_one(
        {'value': '1d239d76132553e6899b21ea'},
        {'_id': False},
    )
    assert blocked_by_id == {
        'value': '1d239d76132553e6899b21ea',
        'type': 'phone_id',
        'until': datetime.datetime(2020, 2, 1, 3, 0),
        'created': datetime.datetime(2020, 1, 10, 10, 0),
        'updated': datetime.datetime(2020, 1, 10, 10, 0),
    }


@pytest.mark.parametrize('require_latest', [True, False])
@pytest.mark.parametrize('getter_name', ['get_user_bson', 'get_user_dbh'])
@pytest.inline_callbacks
def test_get_user_wrapper(require_latest, getter_name):
    getter_method = getattr(userapi, getter_name)
    user_doc = yield getter_method(
        'user-id-1',
        fields=['phone_id', 'created', 'device_id', 'authorized'],
        require_latest=require_latest,
    )
    assert user_doc == {
        '_id': 'user-id-1',
        'phone_id': bson.ObjectId('111111111111111111111111'),
        'device_id': 'device-id-1',
        'created': datetime.datetime(2022, 2, 2, 22, 22, 22),
        'authorized': True,
    }


@pytest.mark.parametrize('require_latest', [True, False])
@pytest.inline_callbacks
def test_get_many_users(require_latest):
    user_docs = yield userapi.get_many_users_dbh(
        {'phone_id': bson.ObjectId('111111111111111111111111')},
        fields=['phone_id', 'device_id'],
        require_latest=require_latest,
    )
    assert sorted(user_docs, key=operator.itemgetter('_id')) == [
        {
            '_id': 'user-id-1',
            'phone_id': bson.ObjectId('111111111111111111111111'),
            'device_id': 'device-id-1',
        },
        {
            '_id': 'user-id-2',
            'phone_id': bson.ObjectId('111111111111111111111111'),
            'device_id': 'device-id-2',
        }
    ]
