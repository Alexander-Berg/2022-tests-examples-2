import datetime

import psycopg2
import pytest

from tests_billing_subventions_x import dbhelpers

MOCK_NOW = '2020-04-28T12:00:00+00:00'
RULESET_REF = '072c6866-a3a4-11eb-aaa9-13ca81d72459'
CLASHING_RULE = '70b4baf4-a85e-11eb-8c88-875959338974'
RULE_WITH_RESTRICTIONS = '9e5f48d4-b264-4804-9746-316498cddb59'


@pytest.mark.now('2021-04-30T21:31:00+00:00')
async def test_v2_single_ride_approve_fails_when_too_late(
        taxi_billing_subventions_x, draft,
):
    query = {'doc_id': RULESET_REF}
    response = await _make_request(
        taxi_billing_subventions_x, query, status=400,
    )
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            'Rules\' start \'2021-04-30T21:00:00+0000\' must be greater than '
            '\'2021-04-30T21:31:00+0000\''
        ),
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_approve_creates_budget(
        taxi_billing_subventions_x, limits, draft, load_json,
):
    query = {'doc_id': RULESET_REF}
    await _make_request(taxi_billing_subventions_x, query)
    assert limits.times_called == 1
    request = limits.next_call()['request'].json
    assert request == load_json('limits.json')


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_approve_fails_when_exists_clashing_rules(
        taxi_billing_subventions_x, draft, clashing_rule,
):
    query = {'doc_id': RULESET_REF}
    response = await _make_request(
        taxi_billing_subventions_x, query, status=400,
    )
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': 'There are conflicting rules. First: %s' % CLASHING_RULE,
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_approve_passes_when_clashing_known(
        taxi_billing_subventions_x,
        draft,
        clashing_rule,
        mark_clashing_as_known,
):
    mark_clashing_as_known(
        RULESET_REF, '2021-04-30T21:00:00+00:00', CLASHING_RULE,
    )
    query = {'doc_id': RULESET_REF}
    await _make_request(taxi_billing_subventions_x, query)


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_approve_updates_clashing_rule(
        taxi_billing_subventions_x,
        pgsql,
        draft,
        clashing_rule,
        mark_clashing_as_known,
):
    new_ends_at = '2021-04-30T21:00:00+00:00'
    mark_clashing_as_known(RULESET_REF, new_ends_at, CLASHING_RULE)
    query = {'doc_id': RULESET_REF}
    await _make_request(taxi_billing_subventions_x, query)
    rule = dbhelpers.get_rule_by_id(pgsql, CLASHING_RULE)
    assert rule['ends_at'] == datetime.datetime.fromisoformat(new_ends_at)


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_approve_returns_applying_status(
        taxi_billing_subventions_x, draft,
):
    query = {'doc_id': RULESET_REF}
    response = await _make_request(taxi_billing_subventions_x, query)
    assert response == {
        'status': 'applying',
        'change_doc_id': 'moscow:moscow_center:' + RULESET_REF,
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_approve_schedules_approving_task(
        taxi_billing_subventions_x, stq, draft,
):
    query = {'doc_id': RULESET_REF}
    await _make_request(taxi_billing_subventions_x, query)
    queue = stq.billing_subventions_x_approve_rules
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == RULESET_REF
    assert task['kwargs']['internal_draft_id'] == RULESET_REF
    expected_eta = datetime.datetime.fromisoformat(
        MOCK_NOW,
    ) + datetime.timedelta(seconds=10)
    assert task['eta'] == expected_eta.replace(tzinfo=None)


async def _make_request(bsx, query, status=200):
    url = '/v2/rules/single_ride/approve'
    headers = {
        'X-YaTaxi-Draft-Id': '1111',
        'X-YaTaxi-Draft-Author': 'you',
        'X-YaTaxi-Draft-Tickets': 'TAXITICKET1,TAXITICKET2',
        'X-YaTaxi-Draft-Approvals': 'approver1,approver2',
    }
    response = await bsx.post(url, query, headers=headers or {})
    assert response.status_code == status, response.json()
    return response.json()


@pytest.fixture(name='draft')
def _add_draft(a_draft, a_subdraft, a_single_ride, create_drafts, load_json):
    create_drafts(
        a_draft(
            internal_draft_id=RULESET_REF,
            spec=load_json('bulk_single_ride_spec.json'),
            subdrafts=[
                a_subdraft(
                    spec_ref='1',
                    spec=load_json('bulk_single_ride_subdraft_spec1.json'),
                    is_completed=True,
                ),
                a_subdraft(
                    spec_ref='2',
                    spec=load_json('bulk_single_ride_subdraft_spec1.json'),
                    is_completed=True,
                ),
            ],
            rules=[
                a_single_ride(
                    id=RULE_WITH_RESTRICTIONS,
                    start='2021-04-30T21:00:00+00:00',
                    end='2021-05-31T21:00:00+00:00',
                    tariff_class='econom',
                    tariff_zone='moscow',
                    geoarea='pol-1',
                    tag='a_tag',
                    branding='sticker',
                    points=75,
                ),
                a_single_ride(
                    start='2021-04-30T21:00:00+00:00',
                    end='2021-05-31T21:00:00+00:00',
                    tariff_class='econom',
                    tariff_zone='moscow_center',
                    geoarea='pol-1',
                    tag='a_tag',
                    branding='sticker',
                    points=75,
                ),
                a_single_ride(
                    start='2021-04-30T21:00:00+00:00',
                    end='2021-05-31T21:00:00+00:00',
                    tariff_class='comfort',
                    tariff_zone='moscow',
                    geoarea='pol-1',
                    tag='a_tag',
                    branding='sticker',
                    points=75,
                ),
                a_single_ride(
                    start='2021-04-30T21:00:00+00:00',
                    end='2021-05-31T21:00:00+00:00',
                    tariff_class='comfort',
                    tariff_zone='moscow_center',
                    geoarea='pol-1',
                    tag='a_tag',
                    branding='sticker',
                    points=75,
                ),
                a_single_ride(
                    start='2021-04-30T21:00:00+00:00',
                    end='2021-05-31T21:00:00+00:00',
                    tariff_class='econom',
                    tariff_zone='moscow',
                ),
                a_single_ride(
                    start='2021-04-30T21:00:00+00:00',
                    end='2021-05-31T21:00:00+00:00',
                    tariff_class='econom',
                    tariff_zone='moscow_center',
                ),
                a_single_ride(
                    start='2021-04-30T21:00:00+00:00',
                    end='2021-05-31T21:00:00+00:00',
                    tariff_class='comfort',
                ),
                a_single_ride(
                    start='2021-04-30T21:00:00+00:00',
                    end='2021-05-31T21:00:00+00:00',
                    tariff_class='comfort',
                    tariff_zone='moscow_center',
                ),
            ],
            schedule_spec=[
                {
                    'schedule_ref': 'schedule_ref',
                    'during': psycopg2.extras.NumericRange(720, 900, '[)'),
                    'value': '100',
                },
                {
                    'schedule_ref': 'schedule_ref',
                    'during': psycopg2.extras.NumericRange(1700, 1900, '[)'),
                    'value': '200',
                },
            ],
        ),
    )


@pytest.fixture(name='clashing_rule')
def _add_clashing_rule(a_single_ride, create_rules):
    create_rules(
        a_single_ride(
            id=CLASHING_RULE,
            tariff_zone='moscow_center',
            tariff_class='comfort',
            start='2021-03-31T21:00:00+00:00',
            end='2021-05-09T21:00:00+00:00',
            tag='a_tag',
            geoarea='pol-1',
            branding='sticker',
            points=75,
        ),
    )


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
