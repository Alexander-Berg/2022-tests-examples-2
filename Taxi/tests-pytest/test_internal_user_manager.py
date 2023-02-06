import pytest

from taxi.conf import settings
from taxi.core import db
from taxi.external import archive
from taxi.internal import dbh
from taxi.internal import user_manager
from taxi.internal.dbh import devicelocks
from taxi.internal.dbh import phonelocks


@pytest.mark.parametrize('uid,code,filename,answer', [
    # Uid exists, default sender, all phones are displayed
    ('123', 200, 'userphones_ok.xml', [
        {'default': True, 'phone': '+79223335555'},
        {'blocked': True, 'phone': '+79223336666'},
        {'blocked': True, 'phone': '+79223337777'},
        {'phone': '+79223338888'},
    ]),
    # Uid exists, empty answer
    ('123', 200, 'userphones_empty.xml', []),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    PASSPORT_BASE_SMS_URL='http://passport'
)
@pytest.inline_callbacks
def test_get_uid_phones(
        uid, code, filename, answer,
        mock, asyncenv, load, areq_request, monkeypatch):
    @areq_request
    def requests_request(method, url, **kwargs):
        if filename.endswith('.xml'):
            body = load(filename).replace('REPLACE', uid)
        else:
            body = filename
        return areq_request.response(code, body=body)

    response = yield user_manager.get_uid_phones(uid, 'test', log_extra=None)
    assert answer == response

    call = requests_request.call
    assert call['args'][0].upper() == 'GET'
    assert call['args'][1] == 'http://passport/userphones'
    assert call['kwargs'].get('exponential_backoff')
    assert call['kwargs'].get('timeout') == settings.PASSPORT_TIMEOUT
    assert call['kwargs'].get('params') == {
        'sender': 'Yandex.Taxi',
        'uid': uid,
        }


@pytest.mark.filldb(orders='for_stats', user_phones='for_stats')
@pytest.mark.parametrize('order_id,complete,total', [
    ('complete', 1, 1),
    ('incomplete', 1, 1),
])
@pytest.inline_callbacks
def test_update_phone_stats(order_id, complete, total):
    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    proc = dbh.order_proc.Doc(
        _id=order.pk, order=order, payment_tech=order.payment_tech
    )
    assert order is not None

    yield user_manager.update_stats(proc, log_extra=None)

    order = yield dbh.orders.Doc.find_one_by_id(order_id)
    assert 'loyalty_processed' in order


@pytest.inline_callbacks
def test_get_device_id():
    @pytest.inline_callbacks
    def _set_device_id(user_id, device_id):
        yield db.users.update(
            {'_id': user_id}, {'$set': {'device_id': device_id}}
        )

    device_id = yield user_manager.get_device_id('user1')
    assert device_id is None

    # Create device_id
    yield _set_device_id('user1', 'device_1')

    device_id = yield user_manager.get_device_id('user1')
    assert device_id == 'device_1'

    # Change the device
    yield _set_device_id('user1', 'device_2')
    device_id = yield user_manager.get_device_id('user1')
    assert device_id == 'device_2'


@pytest.mark.filldb(devicelocks='for_unmark_test', phonelocks='for_unmark_test',
                    users='for_unmark_test')
@pytest.inline_callbacks
def test_unmark_user_as_debtor_by_phone_id(patch):
    @patch('taxi.external.archive._perform_post')
    @pytest.inline_callbacks
    def _perform_post(location, payload, src_tvm_service=None, log_extra=None):
        raise archive.NotFoundError

    good_phone_id = '539e9a2be7e5b1f5397af1b0'
    bad_phone_id = '539e9a2be7e5b1f5397af1b1'
    yield user_manager.unmark_user_as_debtor_by_user_info(
        phone_id=good_phone_id
    )

    phonelock_for_good_phone = yield phonelocks.Doc.find_one_doc(
        phone_id=good_phone_id
    )
    assert phonelock_for_good_phone.unpaid_order_ids == []
    assert phonelock_for_good_phone.unfinished_order_ids == ['4', '5', '6']

    phonelock_for_bad_phone = yield phonelocks.Doc.find_one_doc(
        phone_id=bad_phone_id
    )
    assert phonelock_for_bad_phone.unpaid_order_ids == ['10', '20', '30']
    assert phonelock_for_bad_phone.unfinished_order_ids == ['40', '50', '60']

    first_user_of_good_phone = 'user1'
    second_user_of_good_phone = 'user2'
    first_user_of_bad_phone = 'user3'
    devicelock = yield devicelocks.Doc.find_one_doc(
        user_id=first_user_of_good_phone
    )
    assert devicelock.unpaid_order_ids == ['11', '12', '13']
    assert devicelock.unfinished_order_ids == ['14', '15', '16']
    devicelock = yield devicelocks.Doc.find_one_doc(
        user_id=second_user_of_good_phone
    )
    assert devicelock.unpaid_order_ids == ['17', '18', '19']
    assert devicelock.unfinished_order_ids == ['20', '21', '22']
    devicelock = yield devicelocks.Doc.find_one_doc(
        user_id=first_user_of_bad_phone
    )
    assert devicelock.unpaid_order_ids == ['23', '24', '25']
    assert devicelock.unfinished_order_ids == ['26', '27', '28']


@pytest.mark.filldb(_fill=False)
def test_class_user_position():
    point = (37.5, 55.7)
    accuracy = 150  # meters
    user_position = user_manager.UserPosition(point, accuracy)
    assert str(user_position) == 'UserPosition((37.500000, 55.700000), 150)'


@pytest.mark.filldb(static='vip_users')
@pytest.mark.parametrize(
    'city, expected',
    [
        ('Perm', 30),
        ('Moscow', 45),
    ]
)
@pytest.inline_callbacks
def test_vip_order_age_threshold(city, expected):
    result = yield user_manager._vip_order_age_threshold(city)
    assert result == expected


@pytest.mark.filldb(static='vip_users')
@pytest.mark.parametrize(
    'city, expected',
    [
        ('Perm', 10),
        ('Moscow', 20),
    ]
)
@pytest.inline_callbacks
def test_vip_order_amount_threshold(city, expected):
    result = yield user_manager._vip_order_amount_threshold(city)
    assert result == expected


@pytest.mark.config(USER_CHAT_VERSION_SUPPORTED={
    'iphone': [4, 5],
    'uber_android': [3, 2],
    'uber_iphone': [3, 3]
})
@pytest.mark.parametrize('user_id,result', [
    ('user_old_android_uber', True),
    ('user_new_android_uber', True),
    ('user_old_iphone_uber', True),
    ('user_new_iphone_uber', True),
    ('user_old_version', False),
    ('user_new_version', True),
    ('user_bad_app', False)
])
@pytest.inline_callbacks
def test_user_support_chat(user_id, result):
    user_doc = yield dbh.users.Doc.find_one_by_id(user_id)
    res = yield user_manager.user_support_chat(user_doc)

    assert res == result
