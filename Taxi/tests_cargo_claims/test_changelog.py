import base64
import datetime
import hashlib
import hmac
import json
import time

import pytest


SETTINGS = {
    'wait_lost_event_s': 60,
    'journal_junk_size': 1000,
    'min_polling_delay_ms': 1000,
    'max_polling_delay_ms': 10000,
    'cursor_holes_max_size': 20000000,
}


def get_performer_found_events(claim_id):
    return [
        {
            'change_type': 'status_changed',
            'claim_id': claim_id,
            'new_status': 'new',
            'revision': 1,
        },
        {
            'change_type': 'status_changed',
            'claim_id': claim_id,
            'new_status': 'estimating',
            'current_point_id': 1,
            'revision': 2,
        },
        {
            'change_type': 'status_changed',
            'claim_id': claim_id,
            'new_status': 'ready_for_approval',
            'current_point_id': 1,
            'revision': 3,
        },
        {
            'change_type': 'status_changed',
            'claim_id': claim_id,
            'new_status': 'accepted',
            'current_point_id': 1,
            'revision': 4,
        },
        {
            'change_type': 'status_changed',
            'claim_id': claim_id,
            'new_status': 'performer_lookup',
            'current_point_id': 1,
            'revision': 5,
        },
        {
            'change_type': 'status_changed',
            'claim_id': claim_id,
            'new_status': 'performer_draft',
            'current_point_id': 1,
            'revision': 6,
        },
        {
            'change_type': 'status_changed',
            'claim_id': claim_id,
            'new_status': 'performer_found',
            'current_point_id': 1,
            'revision': 7,
        },
    ]


def get_create_accepted_events(claim_id):
    return [
        {
            'claim_id': claim_id,
            'change_type': 'status_changed',
            'new_status': 'performer_lookup',
            'revision': 1,
        },
        {
            'claim_id': claim_id,
            'change_type': 'status_changed',
            'new_status': 'performer_draft',
            'current_point_id': 1,
            'revision': 2,
        },
        {
            'claim_id': claim_id,
            'change_type': 'status_changed',
            'new_status': 'performer_found',
            'current_point_id': 1,
            'revision': 3,
        },
    ]


def get_c2c_create_events(claim_id):
    return [
        {
            'claim_id': claim_id,
            'change_type': 'status_changed',
            'new_status': 'accepted',
            'claim_origin': 'yandexgo',
            'revision': 1,
        },
        {
            'claim_id': claim_id,
            'change_type': 'status_changed',
            'new_status': 'performer_lookup',
            'current_point_id': 1,
            'claim_origin': 'yandexgo',
            'revision': 2,
        },
        {
            'claim_id': claim_id,
            'change_type': 'status_changed',
            'new_status': 'performer_draft',
            'current_point_id': 1,
            'claim_origin': 'yandexgo',
            'revision': 3,
        },
        {
            'claim_id': claim_id,
            'change_type': 'status_changed',
            'new_status': 'performer_found',
            'current_point_id': 1,
            'claim_origin': 'yandexgo',
            'revision': 4,
        },
    ]


def get_price_changed_event(claim_id):
    return {
        'claim_id': claim_id,
        'change_type': 'price_changed',
        'new_price': '287.4792',
        'new_currency': 'RUB',
        'revision': 8,
    }


def get_price_changed_events(claim_id):
    result = get_performer_found_events(claim_id)
    result.append(get_price_changed_event(claim_id))
    return result


def _to_datetime(timestring):
    return datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S%z')


def _load_cursor(cursor):
    payload_part = cursor.split('.')[1].encode()
    payload_part += b'=' * (-len(payload_part) % 4)
    return json.loads(base64.b64decode(payload_part))


def _build_cursor(last_known_id, holes):
    payload = _build_cursor_dict(last_known_id, holes)
    return _jwt_hs512(payload, b'secret').decode()


def _build_cursor_dict(last_known_id, holes):
    cursor = {'version': 1, 'last_known_id': last_known_id, 'holes': []}
    for event_id, delta_seconds in holes:
        timestamp = int(time.time()) + delta_seconds
        cursor['holes'].append({'id': event_id, 'timestamp': timestamp})
    return cursor


def _jwt_hs512(payload, key):
    header = {'alg': 'HS512', 'typ': 'JWT'}
    signing_input = b'.'.join([_b64_encode(header), _b64_encode(payload)])
    signature = hmac.new(key, signing_input, hashlib.sha512).digest()
    return b'.'.join(
        [signing_input, base64.urlsafe_b64encode(signature).rstrip(b'=')],
    )


def _b64_encode(dct):
    binary = json.dumps(dct, separators=(',', ':')).encode()
    return base64.urlsafe_b64encode(binary).rstrip(b'=')


def prepare_response(response):
    response_json = response.json()
    assert 'cursor' in response_json
    cursor = response_json['cursor']
    response_json.pop('cursor')
    for event in response_json['events']:
        event.pop('updated_ts')
        event.pop('operation_id')
    return cursor, response_json


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.config(CARGO_CLAIMS_CHANGELOG_JOURNAL_SETTINGS=SETTINGS)
async def test_changelog_journal(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    claim_info = await state_controller.apply(
        target_status='performer_found', transition_tags={'change_price'},
    )
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/journal',
        json={},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    cursor, response_json = prepare_response(response)
    expected_events = get_price_changed_events(claim_id)

    response_events = response_json['events']
    assert len(response_events) == len(expected_events)
    for index, _ in enumerate(response_events):
        assert (
            response_events[index] == expected_events[index]
        ), f'wrong index {index}'

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/journal',
        json={'cursor': cursor},
        headers=get_default_headers(),
    )
    cursor, response_json = prepare_response(response)
    assert not response_json['events']


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.config(CARGO_CLAIMS_CHANGELOG_JOURNAL_SETTINGS=SETTINGS)
async def test_changelog_journal_with_holes(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    claim_info = await state_controller.apply(
        target_status='performer_found', transition_tags={'change_price'},
    )
    claim_id = claim_info.claim_id

    expected_events = get_price_changed_events(claim_id)
    holes = [(i + 1, 10000000) for i, _ in enumerate(expected_events)]

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/journal',
        json={'cursor': _build_cursor(last_known_id=len(holes), holes=holes)},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    _, response_json = prepare_response(response)

    response_events = response_json['events']
    assert len(response_events) == len(expected_events)
    for index, _ in enumerate(response_events):
        assert (
            response_events[index] == expected_events[index]
        ), f'wrong index {index}'


@pytest.mark.parametrize(
    ('check_status', 'expected_resolution'),
    (
        ('delivered_finish', 'success'),
        ('returned_finish', 'failed'),
        ('failed', 'failed'),
        ('cancelled_by_taxi', 'failed'),
        ('cancelled', 'failed'),
        ('cancelled_with_payment', 'failed'),
        ('cancelled_with_items_on_hands', 'failed'),
    ),
)
@pytest.mark.config(CARGO_CLAIMS_CHANGELOG_JOURNAL_SETTINGS=SETTINGS)
async def test_changelog_resolution(
        taxi_cargo_claims,
        pgsql,
        create_default_claim,
        get_default_headers,
        get_default_corp_client_id,
        check_status: str,
        expected_resolution: str,
):
    cursor = pgsql['cargo_claims'].conn.cursor()
    claim_id = create_default_claim.claim_id
    cursor.execute(
        f"""
            SELECT client_id, client_op_id
            FROM cargo_claims.change_log
        """,
    )
    cursor.execute(
        f"""
        INSERT INTO cargo_claims.change_log(
            claim_id,
            claim_uuid,
            client_id,
            change_type,
            new_status
        )
        VALUES (
            '{claim_id}',
            '{claim_id}',
            '{get_default_corp_client_id}',
            'status_changed',
            '{check_status}'
        )
    """,
    )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/journal',
        json={},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['events'][0]['new_status'] == check_status
    assert response.json()['events'][0]['resolution'] == expected_resolution


async def test_holes_expiration(
        taxi_cargo_claims,
        create_default_claim,
        pgsql,
        get_default_corp_client_id,
        get_default_headers,
):
    cursor_revision = 1000000
    first_claim_id = create_default_claim.claim_id
    second_claim_id = create_default_claim.claim_id
    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_claims.change_log(
            client_op_id,
            updated_ts,
            claim_id,
            claim_uuid,
            client_id,
            change_type,
            new_status
        ) VALUES (
            {cursor_revision},
            '2000-07-19 16:58:44.019364+03',
            '{first_claim_id}',
            '{first_claim_id}',
            '{get_default_corp_client_id}',
            'status_changed',
            'failed'
        ), (
            {cursor_revision + 50},
            '2000-07-19 16:58:44.019364+03',
            '{second_claim_id}',
            '{second_claim_id}',
            '{get_default_corp_client_id}',
            'status_changed',
            'failed'
        );
    """,
    )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/journal',
        json={'cursor': _build_cursor(cursor_revision - 1, list())},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    j_cursor, _ = prepare_response(response)
    assert not _load_cursor(j_cursor)['holes']


async def test_too_many_holes(
        taxi_cargo_claims,
        create_default_claim,
        pgsql,
        get_default_corp_client_id,
        get_default_headers,
):
    first_claim_id = create_default_claim.claim_id
    second_claim_id = create_default_claim.claim_id
    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_claims.change_log(
            client_op_id,
            claim_id,
            claim_uuid,
            client_id,
            change_type,
            new_status
        ) VALUES (
            10,
            '{first_claim_id}',
            '{first_claim_id}',
            '{get_default_corp_client_id}',
            'status_changed',
            'failed'
        ), (
            100,
            '{second_claim_id}',
            '{second_claim_id}',
            '{get_default_corp_client_id}',
            'status_changed',
            'failed'
        );
    """,
    )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/journal',
        json={},
        headers=get_default_headers(),
    )
    assert response.status_code == 500
