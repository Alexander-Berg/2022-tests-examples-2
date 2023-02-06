import pytest
from bank_testing.pg_state import Arbitrary


BUID = '7948e3a9-623c-4524-a390-0e4264d27a77'
ANOTHER_BUID = '7adf6b9b-2c93-4655-a923-c836928c1b4a'
TIME = '2022-06-04T16:10:00'
PIN_TOKEN = 'd307cfff-6baf-48a8-ae58-eaeb5aa13330'

SESSION_TEMPLATE = {
    'antifraud_info': {'device_id': 'device_id', 'dict': {'key': 'value'}},
    'app_vars': None,
    'authorization_track_id': None,
    'locale': None,
    'old_session_id': None,
    'phone_id': '024e7db5-9bd6-4f45-a1cd-0a442e15bdf2',
    'updated_at': '2021-10-31T00:02:00',
    'yandex_uid': '024e7db5-9bd6-4f45-a1cd-0a442e15bde1',
}

SESSION_REISSUE_NO_PIN = SESSION_TEMPLATE | {
    'id': '976fe5ae-d0a5-4461-8ab4-00103422fe91',
    'bank_uid': BUID,
    'created_at': '2021-10-31T00:01:00',
    'deleted_at': None,
    'pin_token_id': None,
    'status': 'pin_token_reissue',
}
SESSION_OK_NO_PIN = SESSION_TEMPLATE | {
    'id': '12948d7a-4880-42cc-8127-23939015faed',
    'bank_uid': BUID,
    'created_at': '2021-10-31T00:02:00',
    'deleted_at': None,
    'pin_token_id': None,
    'status': 'ok',
}
SESSION_OK_WITH_PIN = SESSION_OK_NO_PIN | {
    'id': 'b9b19155-69fc-4cd2-a4a3-e67e473c52e6',
    'pin_token_id': PIN_TOKEN,
}
SESSION_DELETED_NO_PIN = SESSION_TEMPLATE | {
    'id': 'a91302ed-91c8-46cd-a209-9b4463581ade',
    'bank_uid': BUID,
    'created_at': '2021-10-31T00:03:00',
    'deleted_at': '2021-10-31T00:03:30',
    'pin_token_id': None,
    'status': 'ok',
}
SESSION_DELETED_WITH_PIN = SESSION_DELETED_NO_PIN | {
    'id': 'e1d255e8-9d81-487e-9f58-9304a45ce98d',
    'pin_token_id': PIN_TOKEN,
}
SESSION_ANOTHER_BUID_NO_PIN = SESSION_TEMPLATE | {
    'id': '9df97a0f-44f6-4727-873b-1f4ba6d03391',
    'bank_uid': ANOTHER_BUID,
    'created_at': '2021-10-31T00:05:00',
    'deleted_at': None,
    'pin_token_id': None,
    'status': 'ok',
}
SESSION_ANOTHER_BUID_WITH_PIN = SESSION_ANOTHER_BUID_NO_PIN | {
    'id': '87131aa0-ada7-43d0-851a-c6e3de4e0fe1',
    'pin_token_id': '7b7d2503-53b5-498e-bc97-5cd159178d64',
}


@pytest.fixture
def sample_db(db, db_sessions):
    for session in [
            SESSION_OK_NO_PIN,
            SESSION_OK_WITH_PIN,
            SESSION_REISSUE_NO_PIN,
            SESSION_DELETED_NO_PIN,
            SESSION_DELETED_WITH_PIN,
            SESSION_ANOTHER_BUID_NO_PIN,
            SESSION_ANOTHER_BUID_WITH_PIN,
    ]:
        db.do_insert('sessions', session)
    db.assert_valid()
    return db


async def stq_call_repeated(queue, runner, payload, task_id='task_id'):
    while True:
        assert queue.times_called == 0
        await runner.call(task_id=task_id, kwargs=payload)
        if queue.times_called == 0:
            break
        queue.next_call()


async def test_deletion_by_buid(db, sample_db, stq, stq_runner):
    await stq_call_repeated(
        stq.bank_userinfo_delete_sessions,
        stq_runner.bank_userinfo_delete_sessions,
        {'filter': {'buid': BUID}},
    )
    for session in [
            SESSION_OK_NO_PIN,
            SESSION_OK_WITH_PIN,
            SESSION_REISSUE_NO_PIN,
    ]:
        db.expect_update(
            'sessions',
            session['id'],
            {'deleted_at': Arbitrary(not_null=True)},
        )
    db.assert_valid()


async def test_deletion_by_pin_token(db, sample_db, stq, stq_runner):
    await stq_call_repeated(
        stq.bank_userinfo_delete_sessions,
        stq_runner.bank_userinfo_delete_sessions,
        {'filter': {'buid': BUID, 'pin_token': PIN_TOKEN}},
    )
    db.expect_update(
        'sessions',
        SESSION_OK_WITH_PIN['id'],
        {'deleted_at': Arbitrary(not_null=True)},
    )
    db.assert_valid()


async def test_deletion_by_pin_token_empty(db, sample_db, stq, stq_runner):
    await stq_call_repeated(
        stq.bank_userinfo_delete_sessions,
        stq_runner.bank_userinfo_delete_sessions,
        {'filter': {'buid': BUID, 'pin_token_empty': 'empty'}},
    )
    for session in SESSION_OK_NO_PIN, SESSION_REISSUE_NO_PIN:
        db.expect_update(
            'sessions',
            session['id'],
            {'deleted_at': Arbitrary(not_null=True)},
        )
    db.assert_valid()
