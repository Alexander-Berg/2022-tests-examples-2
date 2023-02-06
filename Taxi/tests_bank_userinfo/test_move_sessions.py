import datetime
import pytest
from bank_testing.pg_state import PgState, DateTimeAsStr, Arbitrary


class SessionData:
    def __init__(self, id, deleted_id, data):
        self.id = id
        self.deleted_id = deleted_id
        self.data = data

    def as_regular(self):
        return {'id': self.id} | self.data

    def as_deleted(self):
        return {
            'id': self.deleted_id,
            'deleted_session_id': self.id,
        } | self.data


SESSION_1 = SessionData(
    '00000000-0000-0000-0000-000000000001',
    None,
    {
        'antifraud_info': {'device_id': 'device_id', 'dict': {'key': 'value'}},
        'app_vars': None,
        'authorization_track_id': None,
        'bank_uid': '7948e3a9-623c-4524-a390-0e4264d27a77',
        'created_at': '2021-10-31T00:01:00',
        'deleted_at': None,
        'locale': None,
        'old_session_id': None,
        'phone_id': '024e7db5-9bd6-4f45-a1cd-0a442e15bdf2',
        'pin_token_id': None,
        'status': 'not_registered',
        'updated_at': '2021-10-31T00:02:00',
        'yandex_uid': '024e7db5-9bd6-4f45-a1cd-0a442e15bde1',
    },
)
SESSION_2 = SessionData(
    '00000000-0000-0000-0000-000000000002',
    None,
    {
        'antifraud_info': {'device_id': 'device_id', 'dict': {'key': 'value'}},
        'app_vars': None,
        'authorization_track_id': None,
        'bank_uid': '7948e3a9-623c-4524-a390-0e4264d27a77',
        'created_at': '2021-10-31T00:01:00',
        'deleted_at': None,
        'locale': None,
        'old_session_id': None,
        'phone_id': '024e7db5-9bd6-4f45-a1cd-0a442e15bdf2',
        'pin_token_id': None,
        'status': 'required_application_in_progress',
        'updated_at': '2021-10-31T00:02:00',
        'yandex_uid': '024e7db5-9bd6-4f45-a1cd-0a442e15bde1',
    },
)
SESSION_3 = SessionData(
    '00000000-0000-0000-1000-100000000001',
    '00000000-0000-0000-0000-100000000001',
    {
        'antifraud_info': {'device_id': 'device_id', 'dict': {'key': 'value'}},
        'app_vars': None,
        'authorization_track_id': None,
        'bank_uid': '7948e3a9-623c-4524-a390-1e4264d27a77',
        'created_at': '2021-10-31T00:11:00',
        'deleted_at': '2021-11-01T00:11:00',
        'locale': None,
        'old_session_id': None,
        'phone_id': '024e7db5-9bd6-4f45-a1cd-1a442e15bdf2',
        'pin_token_id': None,
        'status': 'not_registered',
        'updated_at': '2021-10-31T00:12:00',
        'yandex_uid': '024e7db5-9bd6-4f45-a1cd-1a442e15bde1',
    },
)
SESSION_4 = SessionData(
    '00000000-0000-0000-1000-100000000002',
    '00000000-0000-0000-0000-100000000002',
    {
        'antifraud_info': {'device_id': 'device_id', 'dict': {'key': 'value'}},
        'app_vars': None,
        'authorization_track_id': None,
        'bank_uid': '7948e3a9-623c-4524-a390-1e4264d27a77',
        'created_at': '2021-10-31T00:21:00',
        'deleted_at': '2021-11-01T00:12:00',
        'locale': None,
        'old_session_id': None,
        'phone_id': '024e7db5-9bd6-4f45-a1cd-1a442e15bdf2',
        'pin_token_id': None,
        'status': 'required_application_in_progress',
        'updated_at': '2021-10-31T00:22:00',
        'yandex_uid': '024e7db5-9bd6-4f45-a1cd-1a442e15bde1',
    },
)


@pytest.fixture
def db_deleted_sessions(db):
    db.add_table(
        'bank_userinfo.deleted_sessions',
        'id',
        [
            'id',
            'deleted_session_id',
            'yandex_uid',
            'bank_uid',
            'status',
            'old_session_id',
            'created_at',
            'updated_at',
            'phone_id',
            'antifraud_info',
            'authorization_track_id',
            'deleted_at',
            'app_vars',
            'locale',
            'pin_token_id',
            'cursor_key',
        ],
        alias='deleted_sessions',
        defaults={'cursor_key': Arbitrary()},
        converters={
            'created_at': DateTimeAsStr(),
            'updated_at': DateTimeAsStr(),
            'deleted_at': DateTimeAsStr(),
        },
    )


@pytest.fixture
def sample_db(db, db_sessions, db_deleted_sessions):
    db.expect_insert('sessions', SESSION_1.as_regular())
    db.expect_insert('sessions', SESSION_2.as_regular())
    db.expect_insert('deleted_sessions', SESSION_3.as_deleted())
    db.expect_insert('deleted_sessions', SESSION_4.as_deleted())

    db.assert_valid()
    return db


async def test_move_sessions_default(taxi_bank_userinfo, db, sample_db):
    await taxi_bank_userinfo.run_task('move_sessions')
    db.expect_delete('deleted_sessions', SESSION_3.deleted_id)
    db.expect_insert('sessions', SESSION_3.as_regular())
    db.assert_valid()

    await taxi_bank_userinfo.run_task('move_sessions')
    db.expect_delete('deleted_sessions', SESSION_4.deleted_id)
    db.expect_insert('sessions', SESSION_4.as_regular())
    db.assert_valid()

    await taxi_bank_userinfo.run_task('move_sessions')
    db.assert_valid()


@pytest.mark.config(BANK_USERINFO_MOVE_SESSIONS={'batch_size': 2})
async def test_move_sessions_chunk_size(taxi_bank_userinfo, db, sample_db):
    await taxi_bank_userinfo.run_task('move_sessions')
    db.expect_delete('deleted_sessions', SESSION_3.deleted_id)
    db.expect_insert('sessions', SESSION_3.as_regular())
    db.expect_delete('deleted_sessions', SESSION_4.deleted_id)
    db.expect_insert('sessions', SESSION_4.as_regular())
    db.assert_valid()
