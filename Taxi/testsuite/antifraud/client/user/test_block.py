import datetime

import pytest


def _make_input(input):
    ret = {
        'phone_id': input['phone_id'],
        'block_duration': input['block_duration'],
    }
    if 'user_id' in input:
        ret['user_id'] = input['user_id']
    if 'device_id' in input:
        ret['device_id'] = input['device_id']
    if 'reason' in input:
        ret['reason'] = input['reason']
    if 'initiator_service' in input:
        ret['initiator_service'] = input['initiator_service']

    return ret


@pytest.mark.parametrize(
    'input',
    [
        ({'phone_id': 'id_from_custom_db', 'block_duration': 1000}),
        ({'phone_id': 'id_not_from_custom_db', 'block_duration': 15}),
        (
            {
                'phone_id': 'id_from_custom_db',
                'device_id': 'device_id_from_custom_db',
                'block_duration': 2,
            }
        ),
        (
            {
                'phone_id': 'id_from_custom_db',
                'block_duration': 10000000,
                'reason': 'bad_man',
            }
        ),
    ],
)
@pytest.mark.config(AFS_CUSTOM_USERS_STATISTICS=True)
@pytest.mark.now('2018-10-01T09:00:00+0000')
def test_block_user(taxi_antifraud, db, testpoint, input, now):
    def check(raw):
        duration = input['block_duration']
        reason = input['reason'] if 'reason' in input else 'request_to_service'

        assert raw['blocked_till'] == now + datetime.timedelta(
            seconds=duration,
        )
        assert 'created' in raw
        assert raw['afs_block_reason'] == 'block_by_request'
        assert raw['block_reason'] == reason

    @testpoint('dbanti_fraud.stat_users')
    def after_mongo_recording_users(_):
        pass

    @testpoint('dbanti_fraud.stat_phones')
    def after_mongo_recording_user_phones(_):
        pass

    @testpoint('dbanti_fraud.stat_devices')
    def after_mongo_recording_user_devices(_):
        pass

    response = taxi_antifraud.post(
        'v1/client/user/block', json=_make_input(input),
    )
    assert response.status_code == 200

    after_mongo_recording_user_phones.wait_call()
    phone_raw = db.antifraud_stat_phones.find_one(input['phone_id'])
    check(phone_raw)

    if 'user_id' in input:
        after_mongo_recording_users.wait_call()
        user_raw = db.antifraud_stat_users.find_one(input['user_id'])
        check(user_raw)

    if 'device_id' in input:
        after_mongo_recording_user_devices.wait_call()
        device_raw = db.antifraud_stat_devices.find_one(input['device_id'])
        check(device_raw)
