import copy

import pytest

import tests_bank_notifications.common as common
import tests_bank_notifications.db_helpers as db_helpers
import tests_bank_notifications.defaults as defaults
import tests_bank_notifications.models as models


@pytest.mark.parametrize(
    'field_name',
    [defaults.BUID_KEY, defaults.CONSUMER_KEY, defaults.MARK_TYPE_KEY],
)
async def test_no_required_field(
        taxi_bank_notifications, mockserver, pgsql, field_name,
):
    message = f'Field \'{field_name}\' is missing'
    req = models.S2SMarkEventsRequest.default(
        status_code=400, code='400', message=message,
    )
    req_json = req.to_json()
    req_json.pop(field_name)
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req_json,
        headers=req.headers(),
    )
    common.check_failed_response(response, req, False)

    db_response = db_helpers.select_mark_events_requests(pgsql)
    # requests are not saved because they failed api validation
    assert db_response == []


@pytest.mark.parametrize(
    'field_name',
    [defaults.BUID_KEY, defaults.CONSUMER_KEY, defaults.MARK_TYPE_KEY],
)
async def test_empty_required_field(
        taxi_bank_notifications, mockserver, pgsql, field_name,
):
    message = f'Value of \'{field_name}\': incorrect size'
    req = models.S2SMarkEventsRequest.default(
        status_code=400, code='400', message=message,
    )
    req_json = req.to_json()
    req_json[field_name] = [] if field_name == defaults.EVENT_IDS_KEY else ''
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req_json,
        headers=req.headers(),
    )
    common.check_failed_response(response, req, False)

    db_response = db_helpers.select_mark_events_requests(pgsql)
    # requests are not saved because they failed api validation
    assert db_response == []


async def test_buid_not_found(
        taxi_bank_notifications, mockserver, pgsql, bank_userinfo_mock,
):
    req = models.S2SMarkEventsRequest.default(
        status_code=404, code='NotFound', message='buid not found',
    )
    bank_userinfo_mock.set_http_status_code(404)
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    common.check_failed_response(response, req)
    common.select_and_check_req_in_db(pgsql, req)


async def test_event_not_found(taxi_bank_notifications, mockserver, pgsql):
    req = models.S2SMarkEventsRequest.default(
        status_code=404, code='NotFound', message='event id not found',
    )
    event = models.Event.default()
    while event.event_id == req.event_ids[0]:
        event.event_id = defaults.gen_uuid()
    db_response = db_helpers.insert_event(pgsql, event)
    assert len(db_response) == 1

    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    common.check_failed_response(response, req)
    common.select_and_check_req_in_db(pgsql, req)


async def test_ok_event_ids(taxi_bank_notifications, mockserver, pgsql):
    events = [
        models.Event.default(),
        models.Event.default(event_id=defaults.gen_uuid()),
    ]
    for event in events:
        db_response = db_helpers.insert_event(pgsql, event)
        assert len(db_response) == 1

    req = models.S2SMarkEventsRequest.default(
        event_ids=[event.event_id for event in events], status_code=200,
    )

    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 200

    result_req = common.select_and_check_req_in_db(pgsql, req)

    db_marks = db_helpers.select_marks(pgsql, defaults.BUID)
    assert len(db_marks) == len(events)
    for i, db_mark in enumerate(db_marks):
        assert len(db_mark.mark_id) > 1
        assert db_mark.event_id == events[i].event_id
        assert db_mark.req_id == result_req.req_id


async def test_ok_event_type(taxi_bank_notifications, mockserver, pgsql):
    event_type = defaults.EVENT_TYPE
    events = [
        models.Event.default(
            event_type=event_type, event_id=defaults.gen_uuid(),
        ),
        models.Event.default(
            event_type=event_type, event_id=defaults.gen_uuid(),
        ),
    ]
    for event in events:
        db_response = db_helpers.insert_event(pgsql, event)
        assert len(db_response) == 1

    req = models.S2SMarkEventsRequest.default(
        event_type=event_type, event_ids=None, status_code=200,
    )

    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 200

    result_req = common.select_and_check_req_in_db(pgsql, req)

    db_marks = db_helpers.select_marks(pgsql, defaults.BUID)
    assert len(db_marks) == len(events)
    for i, db_mark in enumerate(db_marks):
        assert len(db_mark.mark_id) > 1
        assert db_mark.event_id == events[i].event_id
        assert db_mark.req_id == result_req.req_id


@pytest.mark.parametrize(
    'first_buid,first_event_type,first_event_ids,first_mark_type,'
    'first_status_code,first_code,first_message,'
    'second_buid,second_event_type,second_event_ids,second_mark_type,'
    'has_conflict',
    [
        (  # same requests
            defaults.BUID,
            None,
            [defaults.DEFAULT_UUID],
            'READ',
            200,
            '200',
            '',
            defaults.BUID,
            None,
            [defaults.DEFAULT_UUID],
            'READ',
            False,
        ),
        (  # diff event_type
            defaults.BUID,
            defaults.EVENT_TYPE,
            None,
            'READ',
            200,
            '200',
            '',
            defaults.BUID,
            defaults.EVENT_TYPE2,
            None,
            'READ',
            True,
        ),
        (  # diff event_ids
            defaults.BUID,
            None,
            [defaults.DEFAULT_UUID],
            'READ',
            200,
            '200',
            '',
            defaults.BUID,
            None,
            [defaults.gen_uuid()],
            'READ',
            True,
        ),
        (  # diff buid
            defaults.BUID,
            None,
            [defaults.DEFAULT_UUID],
            'READ',
            200,
            '200',
            '',
            defaults.BUID2,
            None,
            [defaults.DEFAULT_UUID],
            'READ',
            True,
        ),
    ],
)
async def test_idempotency(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        first_buid,
        first_event_type,
        first_event_ids,
        first_mark_type,
        first_status_code,
        first_code,
        first_message,
        second_buid,
        second_event_type,
        second_event_ids,
        second_mark_type,
        has_conflict,
):
    if first_event_ids:
        events = [
            models.Event.default(event_id) for event_id in first_event_ids
        ]
    elif first_event_type:
        events = [models.Event.default(event_type=first_event_type)]
    for event in events:
        db_response = db_helpers.insert_event(pgsql, event)
        assert len(db_response) == 1

    first_req = models.S2SMarkEventsRequest.default(
        bank_uid=first_buid,
        event_type=first_event_type,
        event_ids=first_event_ids,
        mark_type=first_mark_type,
        status_code=first_status_code,
        code=first_code,
        message=first_message,
    )
    common.insert_and_check_req_in_db(pgsql, first_req)
    common.select_and_check_req_in_db(pgsql, first_req)

    second_req = copy.copy(first_req)
    second_req.bank_uid = second_buid
    second_req.event_type = second_event_type
    second_req.event_ids = second_event_ids
    second_req.mark_type = second_mark_type

    second_req.status_code = 409 if has_conflict else first_status_code
    second_req.code = 'Conflict' if has_conflict else first_code
    second_req.message = (
        'idempotency conflict' if has_conflict else first_message
    )

    second_response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=second_req.to_json(),
        headers=second_req.headers(),
    )
    assert second_response.status_code == second_req.status_code
    if second_req.status_code != 200:
        common.check_failed_response(second_response, second_req)
    common.select_and_check_req_in_db(pgsql, first_req)


async def test_same_idempotency_token_diff_consumers(
        taxi_bank_notifications, mockserver, pgsql,
):
    event = models.Event.default()
    db_response = db_helpers.insert_event(pgsql, event)
    assert len(db_response) == 1

    req = models.S2SMarkEventsRequest.default(event_ids=[event.event_id])
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 200

    common.select_and_check_req_in_db(pgsql, req)

    second_req = copy.copy(req)
    second_req.initiator_id = 'second_consumer'
    second_response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=second_req.to_json(),
        headers=second_req.headers(),
    )
    assert second_response.status_code == 200

    db_response = db_helpers.select_mark_events_requests(pgsql)
    assert len(db_response) == 2


async def test_invalid_mark_type(taxi_bank_notifications, mockserver, pgsql):
    req = models.S2SMarkEventsRequest.default(
        mark_type='abc', status_code=400, code='400', message='Parse error',
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    common.check_failed_response(response, req, False)

    db_response = db_helpers.select_mark_events_requests(pgsql)
    # requests are not saved because they failed api validation
    assert db_response == []


@pytest.mark.parametrize(
    'first_status_code,drop_code,drop_message,'
    'second_status_code,second_code,second_message,',
    [
        (200, False, False, 200, None, None),
        (400, True, False, 500, '500', 'Internal Server Error'),
        (400, False, True, 500, '500', 'Internal Server Error'),
        (404, True, True, 500, '500', 'Internal Server Error'),
    ],
)
async def test_absence_of_code_message_in_db(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        first_status_code,
        drop_code,
        drop_message,
        second_status_code,
        second_code,
        second_message,
):
    first_req = models.S2SMarkEventsRequest.default(
        status_code=first_status_code,
    )
    if drop_code:
        first_req.code = None
    if drop_message:
        first_req.message = None
    db_response = db_helpers.insert_mark_events_requests(
        pgsql=pgsql, req=first_req,
    )
    assert len(db_response) == 1

    second_req = copy.copy(first_req)
    second_req.status_code = second_status_code
    second_req.code = second_code
    second_req.message = second_message

    second_response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=second_req.to_json(),
        headers=second_req.headers(),
    )
    assert second_response.status_code == second_req.status_code
    if second_req.status_code != 200:
        common.check_failed_response(second_response, second_req)


async def test_no_events(taxi_bank_notifications, mockserver, pgsql):
    req = models.S2SMarkEventsRequest.default(
        status_code=400,
        code='BadRequest',
        message='all of event_ids, merge_key and event_type are absent',
        event_ids=None,
        event_type=None,
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    common.check_failed_response(response, req)
    common.select_and_check_req_in_db(pgsql, req)


async def test_both_event_ids_and_type(
        taxi_bank_notifications, mockserver, pgsql,
):
    req = models.S2SMarkEventsRequest.default(
        status_code=400,
        code='BadRequest',
        message=(
            'only one of event_ids, merge_key and event_type must be present'
        ),
        event_type=defaults.EVENT_TYPE,
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    common.check_failed_response(response, req)
    common.select_and_check_req_in_db(pgsql, req)


async def test_invalid_event_type(taxi_bank_notifications, mockserver, pgsql):
    req = models.S2SMarkEventsRequest.default(
        status_code=400,
        code='BadRequest',
        message='invalid event_type \'invalid\'',
        event_ids=None,
        event_type='invalid',
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    common.check_failed_response(response, req)
    common.select_and_check_req_in_db(pgsql, req)


@pytest.mark.parametrize(
    'first_use_event_ids,second_use_event_ids,',
    [(True, True), (True, False), (False, True), (False, False)],
)
async def test_ok_nothing_to_mark(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        first_use_event_ids,
        second_use_event_ids,
):
    event_type = defaults.EVENT_TYPE
    events = [
        models.Event.default(
            event_type=event_type, event_id=defaults.gen_uuid(),
        ),
        models.Event.default(
            event_type=event_type, event_id=defaults.gen_uuid(),
        ),
    ]
    for event in events:
        db_response = db_helpers.insert_event(pgsql, event)
        assert len(db_response) == 1

    req = models.S2SMarkEventsRequest.default(
        event_ids=[event.event_id for event in events]
        if first_use_event_ids
        else None,
        event_type=None if first_use_event_ids else event_type,
        status_code=200,
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 200

    result_req = common.select_and_check_req_in_db(pgsql, req)

    db_marks = db_helpers.select_marks(pgsql, defaults.BUID)
    assert len(db_marks) == len(events)
    for i, db_mark in enumerate(db_marks):
        assert len(db_mark.mark_id) > 1
        assert db_mark.event_id == events[i].event_id
        assert db_mark.req_id == result_req.req_id

    second_req = copy.copy(req)
    second_req.consumer = 'another consumer'
    second_req.idempotency_token = defaults.gen_uuid()
    second_req.event_ids = (
        [event.event_id for event in events] if second_use_event_ids else None
    )
    second_req.event_type = None if second_use_event_ids else event_type
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=second_req.to_json(),
        headers=second_req.headers(),
    )
    assert response.status_code == 200
    db_reqs = db_helpers.select_mark_events_requests(pgsql)
    assert len(db_reqs) == 2

    db_marks2 = db_helpers.select_marks(pgsql, defaults.BUID)
    assert db_marks == db_marks2


@pytest.mark.parametrize('second_use_event_ids,', [True, False])
async def test_ok_partial_insert(
        taxi_bank_notifications, mockserver, pgsql, second_use_event_ids,
):
    event_type = defaults.EVENT_TYPE
    events = [
        models.Event.default(
            event_type=event_type, event_id=defaults.gen_uuid(),
        ),
        models.Event.default(
            event_type=event_type, event_id=defaults.gen_uuid(),
        ),
    ]
    for event in events:
        db_response = db_helpers.insert_event(pgsql, event)
        assert len(db_response) == 1

    req = models.S2SMarkEventsRequest.default(
        event_ids=[events[0].event_id], status_code=200,
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == 200
    common.select_and_check_req_in_db(pgsql, req)

    db_marks = db_helpers.select_marks(pgsql, defaults.BUID)
    assert len(db_marks) == 1

    second_req = copy.copy(req)
    second_req.consumer = 'another consumer'
    second_req.idempotency_token = defaults.gen_uuid()
    second_req.event_ids = (
        [event.event_id for event in events] if second_use_event_ids else None
    )
    second_req.event_type = None if second_use_event_ids else event_type
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=second_req.to_json(),
        headers=second_req.headers(),
    )
    assert response.status_code == 200
    db_reqs = db_helpers.select_mark_events_requests(pgsql)
    assert len(db_reqs) == 2

    db_marks2 = db_helpers.select_marks(pgsql, defaults.BUID)
    assert len(db_marks2) == 2


@pytest.mark.parametrize(
    'merge_key, event_type, event_ids, status_code ',
    [
        (defaults.MERGE_KEY, defaults.EVENT_TYPE, [defaults.gen_uuid()], 400),
        (None, defaults.EVENT_TYPE, [defaults.gen_uuid()], 400),
        (defaults.MERGE_KEY, None, [defaults.gen_uuid()], 400),
        (defaults.MERGE_KEY, defaults.EVENT_TYPE, None, 400),
        (None, None, [defaults.gen_uuid()], 404),
        (None, defaults.EVENT_TYPE, None, 200),
        (defaults.MERGE_KEY, None, None, 200),
        (None, None, None, 400),
    ],
)
async def test_internal_input(
        taxi_bank_notifications, merge_key, event_ids, event_type, status_code,
):

    req = models.S2SMarkEventsRequest.default(
        initiator_type=defaults.CONSUMER_TYPE,
        status_code=status_code,
        bank_uid=defaults.BUID,
        merge_key=merge_key,
        mark_type=defaults.MARK_TYPE,
        event_ids=event_ids,
        event_type=event_type,
    )
    response = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert response.status_code == req.status_code


@pytest.mark.parametrize('mark_type', ['READ', 'CANCELED'])
async def test_internal_ok(taxi_bank_notifications, pgsql, mark_type):
    events = [
        models.Event.default(
            event_type=defaults.EVENT_TYPE,
            event_id=defaults.gen_uuid(),
            merge_key=defaults.MERGE_KEY,
        ),
        models.Event.default(
            event_type=defaults.EVENT_TYPE,
            event_id=defaults.gen_uuid(),
            merge_key=defaults.MERGE_KEY,
        ),
        models.Event.default(
            event_type=defaults.EVENT_TYPE,
            event_id=defaults.gen_uuid(),
            merge_key=defaults.OTHER_MERGE_KEY,
        ),
        models.Event.default(
            event_type=defaults.EVENT_TYPE,
            event_id=defaults.gen_uuid(),
            merge_key=None,
        ),
        models.Event.default(
            event_type=defaults.EVENT_TYPE,
            event_id=defaults.gen_uuid(),
            merge_key=defaults.MERGE_KEY,
            bank_uid=defaults.BUID2,
        ),
    ]
    for event in events:
        db_response = db_helpers.insert_event(pgsql, event)
        assert len(db_response) == 1

    req = models.S2SMarkEventsRequest.default(
        event_type=None,
        merge_key=defaults.MERGE_KEY,
        event_ids=None,
        status_code=200,
        mark_type=mark_type,
    )

    resp1 = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert resp1.status_code == 200

    resp2 = await taxi_bank_notifications.post(
        '/notifications-internal/v1/mark_events',
        json=req.to_json(),
        headers=req.headers(),
    )
    assert resp2.status_code == 200

    result_req = common.select_and_check_req_in_db(pgsql, req)

    db_marks = db_helpers.select_marks(pgsql, defaults.BUID)
    assert len(db_marks) == 2
    for i, db_mark in enumerate(db_marks):
        assert len(db_mark.mark_id) > 1
        assert db_mark.event_id == events[i].event_id
        assert db_mark.req_id == result_req.req_id
        assert db_mark.mark_type == result_req.mark_type == mark_type
