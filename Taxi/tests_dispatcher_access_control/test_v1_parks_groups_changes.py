import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'fleet/dac/v1/parks/groups/changes/list'


def build_headers(
        park_id,
        service_ticket=utils.MOCK_SERVICE_TICKET,
        user_ticket=utils.MOCK_SERVICE_TICKET,
        user_ticket_provider='yandex',
        yandex_uid='100',
        accept_language='ru',
):
    headers = {
        'X-Park-ID': park_id,
        'X-Ya-Service-Ticket': service_ticket,
        'X-Ya-User-Ticket': user_ticket,
        'X-Ya-User-Ticket-Provider': user_ticket_provider,
        'X-Yandex-UID': yandex_uid,
        'Accept-Language': accept_language,
    }
    return headers


def build_payload(group_id, limit, cursor=None):
    payload = {'query': {'group': {'id': group_id}}, 'limit': limit}
    if cursor is not None:
        payload['cursor'] = cursor
    return payload


def build_author(user_id, user_name, user_ip):
    return {'id': user_id, 'ip': user_ip, 'name': user_name}


def build_change_value(old, current):
    return {'object_type': 'name', 'name': {'current': current, 'old': old}}


def build_grant_change_value(name, section, old, current, prefix=None):
    value = {
        'object_type': 'grant',
        'grant': {
            'name': name,
            'section_name': section,
            'value': {'current': current, 'old': old},
        },
    }
    if prefix is not None:
        value['grant']['prefix'] = prefix
    return value


def build_change(created_at, created_by, values):
    return {
        'created_at': created_at,
        'created_by': created_by,
        'values': values,
    }


def build_response(changes, cursor=None):
    response = {'changes': changes}
    if cursor is not None:
        response['cursor'] = cursor
    return response


OK_PARAMS = [
    (
        'park_valid1',
        build_payload(group_id='group_valid1', limit=10),
        build_response(
            [
                build_change(
                    created_at='2020-08-05T11:05:04.879623+00:00',
                    created_by=build_author(
                        user_id='author_valid2',
                        user_name='Author 2',
                        user_ip='2a02:6b8:0:40c:140e:7467:16d2:36',
                    ),
                    values=[
                        build_change_value('"OldGroupName"', '"NewGroupName"'),
                    ],
                ),
                build_change(
                    created_at='2020-08-04T11:05:04.879623+00:00',
                    created_by=build_author(
                        user_id='author_valid1',
                        user_name='Author 1',
                        user_ip='2a02:6b8:0:40c:140e:7467:16d2:36',
                    ),
                    values=[build_change_value('', '"Group"')],
                ),
            ],
        ),
    ),
    (
        'park_valid1',
        build_payload(group_id='group_valid1', limit=1),
        build_response(
            [
                build_change(
                    created_at='2020-08-05T11:05:04.879623+00:00',
                    created_by=build_author(
                        user_id='author_valid2',
                        user_name='Author 2',
                        user_ip='2a02:6b8:0:40c:140e:7467:16d2:36',
                    ),
                    values=[
                        build_change_value('"OldGroupName"', '"NewGroupName"'),
                    ],
                ),
            ],
            cursor='{"date":"2020-08-04T11:05:04.879623+00:00","id":"id1"}',
        ),
    ),
    (
        'park_valid1',
        build_payload(
            group_id='group_valid1',
            limit=1,
            cursor='{"date":"2020-08-04T11:05:04.879623+00:00","id":"id1"}',
        ),
        build_response(
            [
                build_change(
                    created_at='2020-08-04T11:05:04.879623+00:00',
                    created_by=build_author(
                        user_id='author_valid1',
                        user_name='Author 1',
                        user_ip='2a02:6b8:0:40c:140e:7467:16d2:36',
                    ),
                    values=[build_change_value('', '"Group"')],
                ),
            ],
        ),
    ),
    (
        'park_valid2',
        build_payload(group_id='group_valid2', limit=10),
        build_response(
            [
                build_change(
                    created_at='2020-08-06T11:05:04.879623+00:00',
                    created_by=build_author(
                        user_id='author_valid3',
                        user_name='Author 3',
                        user_ip='2a02:6b8:0:40c:140e:7467:16d2:36',
                    ),
                    values=[
                        build_grant_change_value(
                            'Покупка истории водителя',
                            'Персонал',
                            False,
                            True,
                            prefix='Водители - Проверка водителя',
                        ),
                    ],
                ),
                build_change(
                    created_at='2020-08-06T11:05:04.879623+00:00',
                    created_by=build_author(
                        user_id='author_valid3',
                        user_name='Author 3',
                        user_ip='2a02:6b8:0:40c:140e:7467:16d2:36',
                    ),
                    values=[build_change_value('"OldName"', '"NewName"')],
                ),
            ],
        ),
    ),
    (
        'park_valid3',
        build_payload(group_id='group_valid3', limit=10),
        build_response([]),
    ),
]


@pytest.mark.parametrize('park_id, payload, expected_response', OK_PARAMS)
async def test_ok(
        taxi_dispatcher_access_control,
        fleet_parks_shard,
        park_id,
        payload,
        expected_response,
):
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, headers=build_headers(park_id=park_id), json=payload,
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response


BAD_PARAMS = [
    (
        'park_valid1',
        build_payload(
            group_id='group_valid1', limit=10, cursor='cursor_invalid',
        ),
        400,
        {'code': 'invalid_cursor', 'message': 'Invalid cursor'},
    ),
]


@pytest.mark.parametrize(
    'park_id, payload, expected_code, expected_error', BAD_PARAMS,
)
async def test_fail(
        taxi_dispatcher_access_control,
        fleet_parks_shard,
        park_id,
        payload,
        expected_code,
        expected_error,
):
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, headers=build_headers(park_id=park_id), json=payload,
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_error
