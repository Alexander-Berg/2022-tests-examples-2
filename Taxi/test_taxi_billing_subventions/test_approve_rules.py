import operator

import pytest
import pytz

from taxi_billing_subventions.common import models


@pytest.mark.now('2019-08-15T20:00:00')
@pytest.mark.parametrize(
    'request_data_path,'
    'expected_approved_doc_ids_path,'
    'expected_limits_queries_path,'
    'expected_stq_calls_path',
    [
        (
            'multiple_rules.json',
            'multiple_rules_doc_ids.json',
            'multiple_rules_limits_queries.json',
            'multiple_rules_stq_calls.json',
        ),
    ],
)
@pytest.mark.filldb(subvention_rules='for_test_ok_response')
@pytest.mark.subventions_config(TVM_ENABLED=True)
@pytest.mark.config(
    BILLING_LIMITS_CREATE_FROM_SUBVENTIONS=True,
    BILLING_SUBVENTIONS_SET_REMINDER_FOR_END_OF_RULE=True,
)
async def test_ok_response(
        db,
        billing_subventions_client,
        patched_tvm_ticket_check,
        limits_requests,
        load_py_json_dir,
        get_zone_patched,
        request_data_path,
        expected_approved_doc_ids_path,
        expected_limits_queries_path,
        expected_stq_calls_path,
        request_headers,
        stq_client_patched,
):
    request, expected_approved_doc_ids = load_py_json_dir(
        '', request_data_path, expected_approved_doc_ids_path,
    )
    headers = request_headers
    headers.update(
        {
            'X-YaTaxi-Draft-Tickets': 'RUPRICING-55, FPRICING-1',
            'X-YaTaxi-Draft-Approvals': 'me, you',
        },
    )

    response = await billing_subventions_client.post(
        '/v2/rules/approve', headers=headers, json=request,
    )
    assert bool(patched_tvm_ticket_check.calls)
    assert response.status == 200
    actual_approved_doc_ids = await _get_approved_doc_ids(db)
    assert sorted(actual_approved_doc_ids) == sorted(expected_approved_doc_ids)
    lock_count = await _count_locks(db)
    assert not lock_count
    assert sorted(
        limits_requests, key=operator.itemgetter('ref'),
    ) == load_py_json_dir('', expected_limits_queries_path)
    _assert_stq_expected_calls(
        stq_client_patched.calls,
        load_py_json_dir('', expected_stq_calls_path),
    )


def _assert_stq_expected_calls(calls, expected):
    assert [
        {
            'args': call['args'],
            'eta': call['eta'].isoformat(),
            'queue': call['queue'],
            'task_id': call['task_id'],
            'kind': call['kwargs']['kind'],
            'rule_kind': call['kwargs']['rule_kind'],
        }
        for call in calls
    ] == expected


@pytest.mark.now('2019-08-15T20:00:00')
@pytest.mark.parametrize(
    'request_data_path',
    [
        'incorrect_daily_guarantees_start_in_the_past.json',
        'incorrect_daily_guarantees_start_gt_end.json',
        'conflicting_driver_fix_rule.json',
    ],
)
@pytest.mark.filldb(subvention_rules='for_test_bad_request_response')
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_bad_request_response(
        db,
        billing_subventions_client,
        patched_tvm_ticket_check,
        load_py_json_dir,
        get_zone_patched,
        request_headers,
        request_data_path,
):
    request, expected_approved_doc_ids = load_py_json_dir(
        '', request_data_path, 'doc_ids_if_error.json',
    )
    headers = request_headers
    headers.update({'X-YaTaxi-Draft-Tickets': 'RUPRICING-55'})

    response = await billing_subventions_client.post(
        '/v2/rules/approve', headers=headers, json=request,
    )
    assert bool(patched_tvm_ticket_check.calls)
    assert response.status == 400
    actual_approved_doc_ids = await _get_approved_doc_ids(db)
    assert sorted(actual_approved_doc_ids) == sorted(expected_approved_doc_ids)
    lock_count = await _count_locks(db)
    assert not lock_count


@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_not_authorized_response(
        billing_subventions_client, request_headers,
):
    response = await billing_subventions_client.post(
        '/v2/rules/approve', headers={}, json={},
    )
    assert response.status == 403


@pytest.mark.parametrize(
    'ticket, expected_status', [(None, 400), ('TAXIRATE-44', 200)],
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_headers(
        patched_tvm_ticket_check,
        billing_subventions_client,
        request_headers,
        ticket,
        expected_status,
):
    headers = request_headers
    if ticket:
        headers.update({'X-YaTaxi-Draft-Tickets': ticket})
    request = {'rules': []}
    response = await billing_subventions_client.post(
        '/v2/rules/approve', headers=headers, json=request,
    )
    assert bool(patched_tvm_ticket_check.calls)
    assert response.status == expected_status


@pytest.mark.now('2019-08-15T20:00:00')
@pytest.mark.filldb(
    distlock='for_test_conflict_response',
    subvention_rules='for_test_conflict_response',
)
@pytest.mark.subventions_config(TVM_ENABLED=True)
async def test_conflict_response(
        db,
        billing_subventions_client,
        patched_tvm_ticket_check,
        load_py_json_dir,
        get_zone_patched,
        request_headers,
):
    request = load_py_json_dir('', 'test_conflict_response/request_data.json')
    headers = request_headers
    headers.update({'X-YaTaxi-Draft-Tickets': 'RUPRICING-55'})
    response = await billing_subventions_client.post(
        '/v2/rules/approve', headers=headers, json=request,
    )
    assert response.status == 409
    approved_doc_ids = await _get_approved_doc_ids(db)
    assert not approved_doc_ids


@pytest.fixture(name='get_zone_patched')
def get_zone_patched_fixture(patch):
    @patch('taxi_billing_subventions.caches.ZonesCache.get_zone')
    def get_zone(name):  # pylint: disable=unused-variable
        return models.Zone(
            name,
            'id',
            pytz.utc,
            'RUB',
            None,
            vat=models.Vat.make_naive(12000),
            country='rus',
        )


async def _get_approved_doc_ids(db):
    query = {'status': {'$in': ['approved', None]}}
    rules = await db.subvention_rules.find(query).to_list(None)
    return sorted([rule['_id'] for rule in rules])


async def _count_locks(db):
    return await db.distlock.count()


@pytest.fixture(name='limits_requests')
def mock_limits(mockserver):
    # pylint: disable=unused-variable

    requests = []

    @mockserver.json_handler('/billing-limits/v1/create')
    def _limits(request):
        requests.append(request.json)
        return {}

    yield requests
