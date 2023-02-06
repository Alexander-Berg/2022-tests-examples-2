import copy
import datetime

import pytest

import tests_bank_notifications.common as common
import tests_bank_notifications.db_helpers as db_helpers
import tests_bank_notifications.defaults as defaults
import tests_bank_notifications.models as models


def check_db_response_and_req(db_response, req):
    assert db_response == [req]
    result_req = db_response[0]
    assert len(result_req.req_id) > 1
    return result_req


def select_and_check_req_in_db(pgsql, req):
    db_response = db_helpers.select_send_events_requests(pgsql)
    return check_db_response_and_req(db_response, req)


def insert_and_check_req_in_db(pgsql, req):
    db_response = db_helpers.insert_send_events_requests(pgsql, req)
    return check_db_response_and_req(db_response, req)


@pytest.mark.parametrize(
    'field_name', [defaults.CONSUMER_KEY, defaults.EVENTS_KEY],
)
async def test_no_required_field(
        taxi_bank_notifications, mockserver, pgsql, field_name,
):
    message = f'Field \'{field_name}\' is missing'
    req = models.SendEventsRequest.default(
        status_code=400, code='400', message=message,
    )
    req_json = req.to_json()
    req_json.pop(field_name)
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req_json,
        headers=req.headers(),
    )
    common.check_failed_response(response, req, False)

    db_response = db_helpers.select_send_events_requests(pgsql)
    # requests are not saved because they failed api validation
    assert db_response == []


async def test_mutually_exclusive_all_and_buid(
        taxi_bank_notifications, mockserver, pgsql,
):
    message = 'buid and all are mutually exclusive'
    req = models.SendEventsRequest.default(
        status_code=400, code='BadRequest', message=message,
    )
    req_json = req.to_json()
    req_json['all'] = True
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req_json,
        headers=req.headers(),
    )
    common.check_failed_response(response, req, False)

    db_response = db_helpers.select_send_events_requests(pgsql)
    # requests are not saved because they failed api validation
    assert db_response == []


async def test_none_of_mutually_exclusive_fields(
        taxi_bank_notifications, mockserver, pgsql,
):
    message = 'one of buid and all is required'
    req = models.SendEventsRequest.default(
        status_code=400, code='BadRequest', message=message,
    )
    req_json = req.to_json()
    req_json.pop(defaults.BUID_KEY)
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req_json,
        headers=req.headers(),
    )
    common.check_failed_response(response, req, False)

    db_response = db_helpers.select_send_events_requests(pgsql)
    # requests are not saved because they failed api validation
    assert db_response == []


@pytest.mark.parametrize(
    'field_name',
    [defaults.BUID_KEY, defaults.CONSUMER_KEY, defaults.EVENTS_KEY],
)
async def test_empty_required_field(
        taxi_bank_notifications, mockserver, pgsql, field_name,
):
    message = f'Value of \'{field_name}\': incorrect size'
    req = models.SendEventsRequest.default(
        status_code=400, code='400', message=message,
    )
    req_json = req.to_json()
    req_json[field_name] = (
        '' if field_name in [defaults.BUID_KEY, defaults.CONSUMER_KEY] else []
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req_json,
        headers=req.headers(),
    )
    common.check_failed_response(response, req, False)

    db_response = db_helpers.select_send_events_requests(pgsql)
    # requests are not saved because they failed api validation
    assert db_response == []


async def test_buid_not_found(
        taxi_bank_notifications, mockserver, pgsql, bank_userinfo_mock,
):
    req = models.SendEventsRequest.default(
        status_code=404, code='NotFound', message='buid not found',
    )
    bank_userinfo_mock.set_http_status_code(404)
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    common.check_failed_response(response, req)
    select_and_check_req_in_db(pgsql, req)


async def test_ok(taxi_bank_notifications, mockserver, pgsql):
    req = models.SendEventsRequest.default(
        events=[
            models.Event.default(title='one'),
            models.Event.default(
                title=None, description=None, action=None, experiment='exp',
            ),
        ],
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 200
    response_event_ids = response.json()['event_ids']
    assert len(response_event_ids) == 2
    for event_id in response_event_ids:
        assert len(event_id) > 1

    result_req = select_and_check_req_in_db(pgsql, req)

    db_events = db_helpers.select_events(pgsql, defaults.BUID)
    assert len(db_events) == len(response_event_ids)
    for i, db_event in enumerate(db_events):
        assert response_event_ids[i] == db_event.event_id
        assert req.events[i].to_json() == db_event.to_json()
        assert (
            db_event.created_at - result_req.created_at
            < datetime.timedelta(milliseconds=100)
        )
    assert db_events[0].title == 'one'
    assert db_events[1].experiment == 'exp'


@pytest.mark.parametrize(
    'title_args,description_args',
    [
        (None, None),
        ({'key': 'value'}, {}),
        ({}, {'key': 'value'}),
        ({'key': 'value'}, {'key': 'value'}),
    ],
)
async def test_ok_tanker_args(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        title_args,
        description_args,
):
    req = models.SendEventsRequest.default(
        events=[
            models.Event.default(
                title='one',
                title_tanker_args=title_args,
                description_tanker_args=description_args,
            ),
        ],
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 200
    response_event_ids = response.json()['event_ids']
    assert len(response_event_ids) == 1
    for event_id in response_event_ids:
        assert len(event_id) > 1

    result_req = select_and_check_req_in_db(pgsql, req)

    db_events = db_helpers.select_events(pgsql, defaults.BUID)
    assert len(db_events) == len(response_event_ids)
    for i, db_event in enumerate(db_events):
        assert response_event_ids[i] == db_event.event_id
        assert req.events[i].to_json() == db_event.to_json()
        assert (
            db_event.created_at - result_req.created_at
            < datetime.timedelta(milliseconds=100)
        )
    assert db_events[0].title == 'one'
    assert db_events[0].title_tanker_args == title_args
    assert db_events[0].description_tanker_args == description_args


@pytest.mark.parametrize(
    'title_args,description_args',
    [
        ({'key': 1}, {}),
        ({}, {'key': 1}),
        ({'key': {'key': 'value'}}, {'key': 'value'}),
    ],
)
async def test_invalid_tanker_args(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        title_args,
        description_args,
):
    req = models.SendEventsRequest.default(
        events=[
            models.Event.default(
                title='one',
                title_tanker_args=title_args,
                description_tanker_args=description_args,
            ),
        ],
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 400


async def test_all_ok(taxi_bank_notifications, mockserver, pgsql):
    req = models.SendEventsRequest.default(
        bank_uid=defaults.ALL_KEY, events=[models.Event.default(title='one')],
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 200
    response_event_ids = response.json()['event_ids']
    assert len(response_event_ids) == 1
    for event_id in response_event_ids:
        assert len(event_id) > 1

    result_req = select_and_check_req_in_db(pgsql, req)

    db_events = db_helpers.select_events(pgsql, defaults.ALL_KEY)
    assert len(db_events) == len(response_event_ids)
    for i, db_event in enumerate(db_events):
        assert response_event_ids[i] == db_event.event_id
        assert req.events[i].to_json() == db_event.to_json()
        assert (
            db_event.created_at - result_req.created_at
            < datetime.timedelta(milliseconds=100)
        )
    assert db_events[0].title == 'one'


@pytest.mark.parametrize(
    'first_buid,first_events,first_status_code,first_code,first_message,'
    'second_buid,second_events,has_conflict',
    [
        (
            defaults.BUID,
            [models.Event.default()],
            200,
            '200',
            '',
            defaults.BUID,
            [models.Event.default()],
            False,
        ),
        (
            defaults.BUID,
            [models.Event.default()],
            200,
            '200',
            '',
            defaults.BUID2,
            [models.Event.default()],
            True,
        ),
        (
            defaults.BUID,
            [models.Event.default()],
            200,
            '200',
            '',
            defaults.BUID,
            [models.Event.default(defaults_group='abc')],
            True,
        ),
        (
            defaults.BUID,
            [models.Event.default()],
            400,
            '400',
            'some_error',
            defaults.BUID,
            [models.Event.default()],
            False,
        ),
        (
            defaults.BUID,
            [models.Event.default()],
            200,
            '400',
            'some_error',
            defaults.BUID2,
            [models.Event.default()],
            True,
        ),
        (
            defaults.BUID,
            [models.Event.default()],
            400,
            '400',
            'some_error',
            defaults.BUID,
            [models.Event.default(defaults_group='abc')],
            True,
        ),
        (
            defaults.BUID,
            [models.Event.default()],
            404,
            '404',
            'NotFound',
            defaults.BUID,
            [models.Event.default()],
            False,
        ),
        (
            defaults.BUID,
            [models.Event.default()],
            404,
            '404',
            'NotFound',
            defaults.BUID2,
            [models.Event.default()],
            True,
        ),
        (
            defaults.BUID,
            [models.Event.default()],
            404,
            '404',
            'NotFound',
            defaults.BUID,
            [models.Event.default(defaults_group='abc')],
            True,
        ),
    ],
)
async def test_idempotency(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        first_buid,
        first_events,
        first_status_code,
        first_code,
        first_message,
        second_buid,
        second_events,
        has_conflict,
):
    first_req = models.SendEventsRequest.default(
        bank_uid=first_buid,
        events=first_events,
        status_code=first_status_code,
        code=first_code,
        message=first_message,
    )
    insert_and_check_req_in_db(pgsql, first_req)
    select_and_check_req_in_db(pgsql, first_req)

    second_req = copy.copy(first_req)
    second_req.events = second_events
    second_req.bank_uid = second_buid

    second_req.status_code = 409 if has_conflict else first_status_code
    second_req.code = 'Conflict' if has_conflict else first_code
    second_req.message = (
        'idempotency conflict' if has_conflict else first_message
    )

    second_response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=second_req.to_json(),
        headers=second_req.headers(),
    )
    assert second_response.status_code == second_req.status_code
    if second_req.status_code != 200:
        common.check_failed_response(second_response, second_req)
    select_and_check_req_in_db(pgsql, first_req)


async def test_same_idempotency_token_diff_consumers(
        taxi_bank_notifications, mockserver, pgsql,
):
    req = models.SendEventsRequest.default()
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 200

    select_and_check_req_in_db(pgsql, req)

    second_req = copy.copy(req)
    second_req.consumer = 'second_consumer'
    second_response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=second_req.to_json(),
        headers=second_req.headers(),
    )
    assert second_response.status_code == 200

    db_response = db_helpers.select_send_events_requests(pgsql)
    assert len(db_response) == 2


@pytest.mark.parametrize(
    'defaults_group,code,message,rec_in_db',
    [
        ('', '400', 'empty', False),
        (
            'invalid',
            'BadRequest',
            'invalid defaults_group \'invalid\' at pos 0',
            True,
        ),
    ],
)
async def test_invalid_defaults_group(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        defaults_group,
        code,
        message,
        rec_in_db,
):
    req = models.SendEventsRequest.default(
        events=[models.Event.default(defaults_group=defaults_group)],
        status_code=400,
        code=code,
        message=message,
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    common.check_failed_response(response, req, rec_in_db)
    if rec_in_db:
        select_and_check_req_in_db(pgsql, req)


@pytest.mark.parametrize(
    'event_type,code,message,rec_in_db',
    [
        ('', '400', 'empty', False),
        (
            'invalid',
            'BadRequest',
            'invalid event_type \'invalid\' at pos 0',
            True,
        ),
    ],
)
async def test_invalid_event_type(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        event_type,
        code,
        message,
        rec_in_db,
):
    req = models.SendEventsRequest.default(
        events=[models.Event.default(event_type=event_type)],
        status_code=400,
        code=code,
        message=message,
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    common.check_failed_response(response, req, rec_in_db)
    if rec_in_db:
        select_and_check_req_in_db(pgsql, req)


@pytest.mark.parametrize(
    'first_status_code, drop_event_ids,drop_code, drop_message,'
    'second_status_code, second_events, second_code, second_message,',
    [
        (200, False, False, False, 200, [models.Event.default()], None, None),
        (
            200,
            True,
            False,
            False,
            500,
            [models.Event.default()],
            '500',
            'Internal Server Error',
        ),
        (
            400,
            False,
            True,
            False,
            500,
            [models.Event.default()],
            '500',
            'Internal Server Error',
        ),
        (
            404,
            False,
            True,
            True,
            500,
            [models.Event.default()],
            '500',
            'Internal Server Error',
        ),
    ],
)
async def test_absence_of_event_ids_code_message_in_db(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        first_status_code,
        drop_event_ids,
        drop_code,
        drop_message,
        second_status_code,
        second_events,
        second_code,
        second_message,
):
    first_req = models.SendEventsRequest.default(status_code=first_status_code)
    if drop_event_ids:
        first_req.event_ids = None
    if drop_code:
        first_req.code = None
    if drop_message:
        first_req.message = None
    db_response = db_helpers.insert_send_events_requests(
        pgsql=pgsql, req=first_req,
    )
    assert len(db_response) == 1

    second_req = copy.copy(first_req)
    second_req.events = second_events

    second_req.status_code = second_status_code
    second_req.code = second_code
    second_req.message = second_message

    second_response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=second_req.to_json(),
        headers=second_req.headers(),
    )
    assert second_response.status_code == second_req.status_code
    resp = second_response.json()
    if second_req.status_code == 200:
        assert len(resp) == 1
        assert 'event_ids' in resp
        assert len(resp['event_ids']) == 1
    else:
        common.check_failed_response(second_response, second_req)


async def test_merge_keys(taxi_bank_notifications, mockserver, pgsql):
    events = [
        models.Event.default(
            event_id=defaults.gen_uuid(),
            merge_key='abc',
            merge_status='CURRENT',
        ),
        models.Event.default(event_id=defaults.gen_uuid()),
        models.Event.default(
            event_id=defaults.gen_uuid(),
            event_type=defaults.EVENT_TYPE2,
            merge_key='abc',
            merge_status='CURRENT',
        ),
    ]
    for event in events:
        db_helpers.insert_event(pgsql, event)
    db_events = db_helpers.select_events(pgsql, defaults.BUID)
    assert len(db_events) == 3

    new_event = models.Event.default(
        event_id=defaults.gen_uuid(), merge_key='abc', merge_status='CURRENT',
    )
    req = models.SendEventsRequest.default(events=[new_event], status_code=200)
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 200

    expected_events = events + [new_event]
    expected_events[0].merge_status = 'MERGED'

    db_events = db_helpers.select_events(pgsql, defaults.BUID)
    assert db_events == expected_events


async def test_payload(taxi_bank_notifications, mockserver, pgsql):
    req = models.SendEventsRequest.default(
        bank_uid=defaults.ALL_KEY,
        events=[models.Event.default(title='one', payload=defaults.PAYLOAD)],
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/send_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 200
    response_event_ids = response.json()['event_ids']
    assert len(response_event_ids) == 1
    for event_id in response_event_ids:
        assert len(event_id) > 1

    db_events = db_helpers.select_events(pgsql, defaults.ALL_KEY)
    assert len(db_events) == len(response_event_ids)
    for i, db_event in enumerate(db_events):
        assert response_event_ids[i] == db_event.event_id
        assert req.events[i].to_json() == db_event.to_json()
        assert db_event.payload == defaults.PAYLOAD
    assert db_events[0].title == 'one'
