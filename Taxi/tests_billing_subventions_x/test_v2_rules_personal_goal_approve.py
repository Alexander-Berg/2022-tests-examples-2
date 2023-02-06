import datetime
import uuid

import pytest

from tests_billing_subventions_x import dbhelpers

MOCK_NOW = '2020-06-09T12:00:00+00:00'
INTERNAL_DRAFT_ID = '072c6866-a3a4-11eb-aaa9-13ca81d72459'


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_approve_returns_applying_status(
        make_request,
):
    response = await make_request()
    assert response == {
        'status': 'applying',
        'change_doc_id': INTERNAL_DRAFT_ID,
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_approve_updates_draft_spec(
        make_request, pgsql,
):
    await make_request()
    expected = {
        'approved_at': None,
        'approvers': 'approver1,approver2',
        'draft_id': '1111',
        'tickets': 'TAXITICKET1,TAXITICKET2',
        'budget_id': 'c0de',
        'state': 'APPLYING',
        'error': None,
    }
    spec = dbhelpers.get_draft_spec(pgsql, INTERNAL_DRAFT_ID)
    actual = {field: spec[field] for field in expected}
    assert actual == expected


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_approve_schedules_approving_task(
        make_request, stq,
):
    await make_request()
    queue = stq.billing_subventions_x_approve_rules
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == INTERNAL_DRAFT_ID
    assert task['kwargs']['internal_draft_id'] == INTERNAL_DRAFT_ID
    expected_eta = datetime.datetime.fromisoformat(
        MOCK_NOW,
    ) + datetime.timedelta(seconds=10)
    assert task['eta'] == expected_eta.replace(tzinfo=None)


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_approve_returns_applying_when_not_done(
        make_request, mark_as_applying, draft, approve_rules,
):
    mark_as_applying(INTERNAL_DRAFT_ID)
    approve_rules(INTERNAL_DRAFT_ID, draft['rules'][0])
    response = await make_request()
    assert response == {
        'status': 'applying',
        'change_doc_id': INTERNAL_DRAFT_ID,
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_approve_returns_empty_when_done(
        make_request, mark_as_applying, draft, approve_rules,
):
    mark_as_applying(INTERNAL_DRAFT_ID)
    approve_rules(INTERNAL_DRAFT_ID, *draft['rules'])
    response = await make_request()
    assert response == {}


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_approve_sets_approved_at_when_done(
        make_request, pgsql, mark_as_applying, draft, approve_rules,
):
    mark_as_applying(INTERNAL_DRAFT_ID)
    approve_rules(INTERNAL_DRAFT_ID, *draft['rules'])
    await make_request()
    spec = dbhelpers.get_draft_spec(pgsql, INTERNAL_DRAFT_ID)
    assert spec['approved_at'] == datetime.datetime.fromisoformat(MOCK_NOW)
    assert spec['state'] == 'APPROVED'


@pytest.mark.now('2021-07-01T00:00:01+03:00')
async def test_v2_rules_personal_goal_approve_fails_when_too_late(
        make_request, pgsql,
):
    response = await make_request(status=400)
    error = (
        'Rules\' start \'2021-06-30T21:00:00+0000\' must be greater than '
        '\'2021-06-30T21:00:01+0000\''
    )
    assert response == {'code': 'INCORRECT_PARAMETERS', 'message': error}
    spec = dbhelpers.get_draft_spec(pgsql, INTERNAL_DRAFT_ID)
    assert spec['state'] == 'INVALID'
    assert spec['error'] == error


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_approve_creates_budget(
        make_request, limits, load_json,
):
    await make_request()
    assert limits.times_called == 1
    request = limits.next_call()['request'].json
    assert request == load_json('limits.json')


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_approve_fails_when_exists_clashing_rules(
        make_request, pgsql, create_rules, goal_with,
):
    rule = goal_with(
        start='2021-06-24T00:00:00+03:00', end='2021-07-02T00:00:00+03:00',
    )
    create_rules(rule, draft_id='1234567')
    response = await make_request(status=400)
    error = 'New rules conflict with rules for drafts: 1234567'
    assert response == {'code': 'INCORRECT_PARAMETERS', 'message': error}
    spec = dbhelpers.get_draft_spec(pgsql, INTERNAL_DRAFT_ID)
    assert spec['state'] == 'INVALID'
    assert spec['error'] == error


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_approve_ok_when_parallel_not_clashing(
        make_request, goal_with, with_applying_draft,
):
    with_applying_draft(
        goal_with(
            start='2021-06-23T00:00:00+03:00', end='2021-07-01T00:00:00+03:00',
        ),
        draft_id='not_clashing',
    )
    response = await make_request()
    assert response == {
        'status': 'applying',
        'change_doc_id': INTERNAL_DRAFT_ID,
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_approve_fails_when_exists_clashing_draft(
        make_request, goal_with, with_applying_draft,
):
    with_applying_draft(
        goal_with(
            start='2021-06-24T00:00:00+03:00', end='2021-07-08T00:00:00+03:00',
        ),
        draft_id='7654321',
    )
    response = await make_request(status=400)
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': 'New rules conflict with parallel draft: 7654321',
    }


@pytest.fixture(name='make_request')
def _make_request(taxi_billing_subventions_x):
    async def _runner(status=200):
        url = '/v2/rules/personal_goal/approve'
        headers = {
            'X-YaTaxi-Draft-Id': '1111',
            'X-YaTaxi-Draft-Author': 'you',
            'X-YaTaxi-Draft-Tickets': 'TAXITICKET1,TAXITICKET2',
            'X-YaTaxi-Draft-Approvals': 'approver1,approver2',
        }
        response = await taxi_billing_subventions_x.post(
            url, _make_query(), headers=headers,
        )
        assert response.status_code == status, response.json()
        return response.json()

    return _runner


def _make_query():
    return {
        'doc_id': INTERNAL_DRAFT_ID,
        'request': {
            'budget': {'weekly': '1000', 'rolling': True, 'threshold': 120},
            'currency': 'RUB',
            'start': '2021-07-01T00:00:00+00:00',
            'end': '2021-07-08T00:00:00+00:00',
            'path': '//path/to/yt/table',
        },
        'info': {
            'geonodes': {},
            'total': 1,
            'failed': 0,
            'errors': [],
            'clashes_with_drafts': [],
        },
    }


@pytest.fixture(name='goal_with')
def _make_goal_builder(a_goal):
    def _builder(start=None, end=None, schedule_ref=None):
        return a_goal(
            start=start or '2021-07-01T00:00:00+03:00',
            end=end or '2021-07-08T00:00:00+03:00',
            tariff_class='econom',
            geonode='br_root/br_moscow',
            geoarea='pol-1',
            tag='a_tag',
            branding='sticker',
            points=75,
            unique_driver_id='0abbd5af-bb97-48cc-ae0f-511fde3f6824',
            schedule_ref=schedule_ref or str(uuid.uuid4()),
        )

    return _builder


@pytest.fixture(name='draft', autouse=True)
def _add_draft(a_draft, a_subdraft, goal_with, create_drafts):
    draft = a_draft(
        internal_draft_id=INTERNAL_DRAFT_ID,
        spec={
            'budget': {'weekly': '1000', 'rolling': True, 'threshold': 120},
            'currency': 'RUB',
            'start': '2021-07-01T00:00:00+03:00',
            'end': '2021-07-08T00:00:00+03:00',
            'path': '//path/to/yt/table',
        },
        subdrafts=[a_subdraft(spec_ref='1', spec={}, is_completed=True)],
        rules=[goal_with(schedule_ref='schedule_ref'), goal_with()],
    )
    create_drafts(draft)
    return draft


@pytest.fixture(name='with_applying_draft')
def _add_applying_draft(create_drafts, a_draft, mark_as_applying):
    def _builder(rule, draft_id):
        draft = a_draft(rules=[rule])
        create_drafts(draft)
        mark_as_applying(draft['internal_draft_id'], draft_id=draft_id)

    return _builder


@pytest.fixture(name='limits', autouse=True)
def mock_limits(mockserver):
    @mockserver.json_handler('/billing-limits/v1/create')
    def _limits(request):
        limits_response = request.json
        limits_response['ref'] = 'c0de'
        limits_response['account_id'] = 'budget/c0de'
        limits_response['tags'] = []
        return limits_response

    return _limits
