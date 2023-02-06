import datetime
import pytest

from taxi.core import async
from taxi.core import db

from taxi_maintenance.stuff import update_user_phones


@pytest.mark.config(USER_PHONES_UPDATE_OUTSTAFF_FLAG_ENABLED=True)
@pytest.mark.filldb(user_phones='staff')
@pytest.inline_callbacks
def test_do_stuff(patch):
    @patch(
        'taxi_maintenance.stuff.update_user_phones._fetch_phones_from_staff',
    )
    @async.inline_callbacks
    def mock_fetch_phones_from_staff(staff_group, special_logins, log_extra):
        yield
        phones = []
        if staff_group == 'yandex_staff':
            phones = ['+79111111111', '+79222222222', '+79333333333']
        elif staff_group == 'taxi_staff':
            phones = ['+79222222222']
        elif staff_group == 'taxi_outstaff':
            phones = ['+79333333333']

        async.return_value(phones)

    yield update_user_phones.do_stuff(datetime.datetime.utcnow())
    phone_doc1 = yield db.user_phones.find_one({'phone': '+79111111111'})
    assert phone_doc1['yandex_staff'] is not None
    assert 'taxi_staff' not in phone_doc1
    assert 'taxi_outstaff' not in phone_doc1

    phone_doc2 = yield db.user_phones.find_one({'phone': '+79222222222'})
    assert phone_doc2['yandex_staff'] is not None
    assert phone_doc2['taxi_staff'] is not None
    assert 'taxi_outstaff' not in phone_doc2

    phone_doc3 = yield db.user_phones.find_one({'phone': '+79333333333'})
    assert phone_doc3['yandex_staff'] is not None
    assert phone_doc3['taxi_outstaff'] is not None
    assert 'taxi_staff' not in phone_doc3
