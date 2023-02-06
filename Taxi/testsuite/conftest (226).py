# pylint: disable=redefined-outer-name
import datetime
import json

import dateutil
import pytest
import pytz


pytest_plugins = ['eats_eaters_plugins.pytest_plugins']


TEST_DEFAULT_LIMIT = 50
DEFAULT_CLIENT_TYPE = 'common'


@pytest.fixture()
def format_datetime():
    def do_format_datetime(stamp, timezone='Europe/Moscow'):
        return (
            stamp.astimezone(pytz.timezone(timezone))
            .replace(microsecond=0)
            .isoformat()
        )

    return do_format_datetime


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_eaters'].dict_cursor()

    return create_cursor


@pytest.fixture()
def create_user(get_cursor):
    def do_create_user(
            personal_email_id='66e0c8b1-d313-40bd-a88f-cb524cefbb6a',
            uuid='5a30b72e-b7e7-4ac5-90b7-7da5cedb6748',
            personal_phone_id='a5b2e0af-170a-4ac8-8ecb-36f893013b29',
            created_at='2019-12-31T10:59:59+03:00',
            deactivated_at=None,
            updated_at='2019-12-31T10:59:59+03:00',
            banned_at=None,
            ban_reason=None,
            client_type=DEFAULT_CLIENT_TYPE,
            passport_uid='999999999999999999999999',
            passport_uid_type='portal',
            eater_type='native',
            eater_name='Василий Пупкин',
            last_login=None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_eaters.users '
            '(personal_email_id, client_id, personal_phone_id, created_at, '
            'deactivated_at, updated_at, banned_at, ban_reason, '
            'client_type, passport_uid, passport_uid_type, type, name, '
            'last_login) '
            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
            'RETURNING id',
            (
                personal_email_id,
                uuid,
                personal_phone_id,
                created_at,
                deactivated_at,
                updated_at,
                banned_at,
                ban_reason,
                client_type,
                passport_uid,
                passport_uid_type,
                eater_type,
                eater_name,
                last_login,
            ),
        )
        eater_id = cursor.fetchone()[0]
        return eater_id

    return do_create_user


@pytest.fixture()
def create_user_with_id(get_cursor):
    def do_create_user(
            _id,
            personal_email_id='66e0c8b1-d313-40bd-a88f-cb524cefbb6a',
            uuid='5a30b72e-b7e7-4ac5-90b7-7da5cedb6748',
            personal_phone_id='a5b2e0af-170a-4ac8-8ecb-36f893013b29',
            created_at='2019-12-31T10:59:59+03:00',
            deactivated_at=None,
            updated_at='2019-12-31T10:59:59+03:00',
            banned_at=None,
            ban_reason=None,
            client_type=DEFAULT_CLIENT_TYPE,
            passport_uid='999999999999999999999999',
            passport_uid_type='portal',
            eater_type='native',
            eater_name='Василий Пупкин',
            last_login=None,
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_eaters.users '
            '(id, personal_email_id, client_id, personal_phone_id, created_at,'
            ' deactivated_at, updated_at, banned_at, ban_reason,'
            ' client_type, passport_uid, passport_uid_type, type, name,'
            ' last_login) '
            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'
            ' %s) RETURNING id',
            (
                _id,
                personal_email_id,
                uuid,
                personal_phone_id,
                created_at,
                deactivated_at,
                updated_at,
                banned_at,
                ban_reason,
                client_type,
                passport_uid,
                passport_uid_type,
                eater_type,
                eater_name,
                last_login,
            ),
        )
        eater_id = cursor.fetchone()[0]
        return eater_id

    return do_create_user


@pytest.fixture()
def get_user(get_cursor):
    def do_get_user(eater_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT id,'
            '   personal_email_id,'
            '   client_id as uuid,'
            '   personal_phone_id,'
            '   created_at,'
            '   deactivated_at,'
            '   updated_at,'
            '   banned_at,'
            '   ban_reason,'
            '   client_type,'
            '   passport_uid,'
            '   passport_uid_type,'
            '   type,'
            '   name,'
            '   last_login'
            ' FROM eats_eaters.users WHERE id = %s',
            [eater_id],
        )
        return cursor.fetchone()

    return do_get_user


@pytest.fixture()
def check_users_are_equal():
    def do_check_users_are_equal(response_eater, user):
        assert str(user['id']) == response_eater['id']
        assert user['uuid'] == response_eater['uuid']
        nullable_fields = [
            'personal_email_id',
            'personal_phone_id',
            'passport_uid',
            'passport_uid_type',
            'type',
            'name',
            'client_type',
        ]
        for field in nullable_fields:
            if user[field] is None:
                assert field not in response_eater
            else:
                assert user[field] == response_eater[field]

    return do_check_users_are_equal


@pytest.fixture()
def check_response_pagination():
    def do_check_response_pagination(
            response_pagination,
            expected_has_more=False,
            expected_limit=TEST_DEFAULT_LIMIT,
            expected_after=None,
    ):
        assert response_pagination['has_more'] == expected_has_more
        assert response_pagination['limit'] == expected_limit
        if expected_after is None:
            assert 'after' not in response_pagination
        else:
            assert response_pagination['after'] == expected_after

    return do_check_response_pagination


@pytest.fixture()
def check_user_data(format_datetime):
    def do_check_user_data(user, expected_data):
        if 'eater_id' in expected_data:
            assert str(user['id']) == expected_data['eater_id']

        nullable_fields = [
            'type',
            'name',
            'passport_uid',
            'passport_uid_type',
            'personal_phone_id',
            'personal_email_id',
            'ban_reason',
        ]
        for field in nullable_fields:
            if field in expected_data:
                assert user[field] == expected_data[field]
            else:
                assert user[field] is None

        assert user['uuid']
        if 'uuid' in expected_data:
            assert user['uuid'] == expected_data['uuid']

        assert user['updated_at']
        assert user['created_at']
        if 'created_at' in expected_data:
            assert (
                format_datetime(user['created_at'])
                == expected_data['created_at']
            )

        if 'last_login' in expected_data:
            assert (
                format_datetime(user['last_login'])
                == expected_data['last_login']
            )

        if 'deactivated_at' in expected_data:
            assert (
                format_datetime(user['deactivated_at'])
                == expected_data['deactivated_at']
            )
        else:
            assert user['deactivated_at'] is None

        if 'client_type' in expected_data:
            assert user['client_type'] == expected_data['client_type']
        else:
            assert user['client_type'] == DEFAULT_CLIENT_TYPE

    return do_check_user_data


@pytest.fixture()
def create_history(get_cursor):
    def do_create_history(
            eater_id=0,
            initiator_id=0,
            initiator_type='system',
            changeset='{"name": ["", "name"]}',
            update_time='2019-12-31T10:59:59+03:00',
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_eaters.history '
            '(eater_id, initiator_id, initiator_type, changeset, update_time)'
            'VALUES(%s, %s, %s, %s, %s)'
            'RETURNING eater_id',
            (eater_id, initiator_id, initiator_type, changeset, update_time),
        )
        eater_id = cursor.fetchone()[0]
        return eater_id

    return do_create_history


@pytest.fixture()
def convert_time_in_changeset():
    def do_convert_time_in_changeset(changeset):
        if not changeset:
            return

        for key, value in changeset.items():
            if key in [
                    'created_at',
                    'deactivated_at',
                    'updated_at',
                    'banned_at',
            ]:
                old_date = (
                    dateutil.parser.isoparse(value[0]) if value[0] else ''
                )
                new_date = (
                    dateutil.parser.isoparse(value[1]) if value[1] else ''
                )
                changeset[key] = [old_date, new_date]

    return do_convert_time_in_changeset


@pytest.fixture()
def insert_history_to_db(create_history):
    def do_insert_history_to_db(history):
        eaters = set()
        for history_item in history:
            eaters.add(
                create_history(
                    eater_id=history_item['eater_id'],
                    initiator_type=history_item['initiator_type'],
                    initiator_id=history_item.get('initiator_id', None),
                    changeset=history_item['changeset'],
                    update_time=history_item['update_time'],
                ),
            )
        return eaters

    return do_insert_history_to_db


@pytest.fixture()
def append_changeset():
    def do_append_changeset(changes, old_data, new_data, field_name):
        if old_data[field_name] != new_data[field_name]:
            old_value = (
                old_data[field_name]
                if old_data[field_name] is not None
                else ''
            )
            new_value = (
                new_data[field_name]
                if new_data[field_name] is not None
                else ''
            )
            changes[field_name] = [old_value, new_value]

    return do_append_changeset


@pytest.fixture()
def make_changeset_by_user_data(append_changeset):
    def do_make_changeset_by_user_data(old_user_data, new_user_data):
        changeset = {}
        for field in [
                'type',
                'name',
                'passport_uid',
                'passport_uid_type',
                'personal_phone_id',
                'personal_email_id',
                'uuid',
                'client_type',
                'created_at',
                'deactivated_at',
                'banned_at',
                'ban_reason',
        ]:
            append_changeset(changeset, old_user_data, new_user_data, field)
        return changeset if changeset else None

    return do_make_changeset_by_user_data


@pytest.fixture()
def check_history_stq(convert_time_in_changeset, make_changeset_by_user_data):
    def do_check_history_stq(
            stq_task,
            old_user_data,
            new_user_data,
            datetime_before,
            datetime_after,
            expected_initiator_id=None,
            expected_initiator_type='system',
    ):
        history = stq_task['kwargs']
        if expected_initiator_type == 'system':
            assert 'initiator_id' not in history
        else:
            assert history['initiator_id'] == str(expected_initiator_id)

        assert history['initiator_type'] == expected_initiator_type

        expected_changeset = make_changeset_by_user_data(
            old_user_data, new_user_data,
        )
        changeset_from_history = json.loads(history['changeset'])
        convert_time_in_changeset(changeset_from_history)
        assert expected_changeset == changeset_from_history

        assert (
            datetime_before
            < dateutil.parser.isoparse(history['update_time'])
            < datetime_after
        )

    return do_check_history_stq


@pytest.fixture()
def get_initiator_data():
    def do_get_initiator_data(request, headers):
        if 'admin_id' in request:
            return int(request['admin_id']), 'admin'
        if (
                'X-Eats-User' in headers
                and '=' in headers['X-Eats-User']
                and 'user_id' in headers['X-Eats-User']
        ):
            return (
                int(
                    dict(
                        item.split('=')
                        for item in headers['X-Eats-User'].split(',')
                    )['user_id'],
                ),
                'user',
            )
        return None, 'system'

    return do_get_initiator_data


@pytest.fixture()
async def update_and_check_history(
        taxi_eats_eaters,
        taxi_config,
        create_user,
        get_user,
        get_initiator_data,
        check_history_stq,
        stq,
):
    async def do_update_and_check_history(
            path, requests, init_user_data, save_history,
    ):
        if init_user_data is None:
            init_user_data = {}
        eater_id = create_user(**init_user_data)

        taxi_config.set_values(
            {'EATS_EATERS_FEATURE_FLAGS': {'save_history': save_history}},
        )

        # update eater
        sent_requests = []
        for request in requests:
            request_json = {'eater_id': str(eater_id), **request['json']}
            header = {}
            if 'header' in request:
                header = request['header']

            datetime_before = datetime.datetime.now(tz=pytz.utc)
            sent_request = {
                'old_user_data': get_user(eater_id),
                'json': request_json,
                'header': header,
                'datetime_before': datetime_before,
            }

            response = await taxi_eats_eaters.post(
                path=path, json=request_json, headers=header,
            )
            assert response.status_code == 204

            sent_request['datetime_after'] = datetime.datetime.now(tz=pytz.utc)
            sent_request['new_user_data'] = get_user(eater_id)

            sent_requests.append(sent_request)

        if not save_history:
            assert not stq.eater_change_history.times_called
            return

        assert stq.eater_change_history.times_called == len(sent_requests)
        # check_history
        for sent_request in sent_requests:
            initiator_id, initiator_type = get_initiator_data(
                sent_request['json'], sent_request['header'],
            )
            check_history_stq(
                stq.eater_change_history.next_call(),
                sent_request['old_user_data'],
                sent_request['new_user_data'],
                sent_request['datetime_before'],
                sent_request['datetime_after'],
                expected_initiator_id=initiator_id,
                expected_initiator_type=initiator_type,
            )

    return do_update_and_check_history


@pytest.fixture()
def check_update_ret_code(taxi_eats_eaters):
    async def do_check_update_ret_code(
            path, request_json, header, expected_ret_code,
    ):
        response = await taxi_eats_eaters.post(
            path=path, json=request_json, headers=header,
        )
        assert response.status_code == expected_ret_code

    return do_check_update_ret_code


@pytest.fixture()
def rewind_period(taxi_config, mocked_time, taxi_eats_eaters):
    async def _rewind_period():
        period = taxi_config.get('EATS_DATA_MAPPINGS_UPLOAD_PARAMS')
        period = period['eats-eaters']['upload_period_ms']
        period = 1 + period / 1000

        mocked_time.sleep(period)
        await taxi_eats_eaters.invalidate_caches()

        return mocked_time.now()

    return _rewind_period
