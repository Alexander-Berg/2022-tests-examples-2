import datetime

import pytest

from tests_billing_subventions_x import dbhelpers

MOCK_NOW = '2021-04-28T19:31:00+00:00'
RULESET_REF = '072c6866-a3a4-11eb-aaa9-13ca81d72459'
CLASHING_RULE = '70b4baf4-a85e-11eb-8c88-875959338974'


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_check_fails_when_draft_does_not_exist(
        taxi_billing_subventions_x,
):
    query = _make_query()
    response = await _make_request(
        taxi_billing_subventions_x, query, status=400,
    )
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            'Specification not set for draft '
            '"072c6866-a3a4-11eb-aaa9-13ca81d72459"'
        ),
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_check_returns_data_for_approvals(
        taxi_billing_subventions_x, create_drafts, draft,
):
    for subdraft in draft['subdrafts']:
        subdraft['is_completed'] = True
    create_drafts(draft)
    query = _make_query()
    response = await _make_request(taxi_billing_subventions_x, query)
    assert response == {
        'change_doc_id': 'moscow:moscow_center:' + query['ruleset_ref'],
        'status': 'completed',
        'data': {'doc_id': query['ruleset_ref']},
    }


@pytest.mark.now('2021-04-30T19:31:00+00:00')
@pytest.mark.config(BILLING_SUBVENTIONS_RULES_START_MIN_THRESHOLD_IN_HOURS=2)
async def test_v2_single_ride_check_fails_when_too_late(
        taxi_billing_subventions_x, create_drafts, draft,
):
    create_drafts(draft)
    query = _make_query()
    response = await _make_request(
        taxi_billing_subventions_x, query, status=400,
    )
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': (
            'Rules\' start \'2021-04-30T21:00:00+0000\' must be greater than '
            '\'2021-04-30T19:31:00+0000\' + 2 hours'
        ),
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_check_fails_when_draft_has_broken_specs(
        taxi_billing_subventions_x, create_drafts, draft,
):
    for subdraft in draft['subdrafts']:
        subdraft['error'] = 'Spec is broken'
        subdraft['is_completed'] = True
    create_drafts(draft)
    query = _make_query()
    response = await _make_request(
        taxi_billing_subventions_x, query, status=400,
    )
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': 'Draft has broken specs',
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_check_passes_when_clashing_expected(
        taxi_billing_subventions_x, pgsql, create_drafts, draft, clashing_rule,
):
    create_drafts(draft)
    query = _make_query(old_rule_ids=[CLASHING_RULE])
    await _make_request(taxi_billing_subventions_x, query)
    expected = [
        {
            'rule_id': CLASHING_RULE,
            'new_ends_at': datetime.datetime.fromisoformat(
                '2021-04-30T21:00:00+00:00',
            ),
        },
    ]
    actual = dbhelpers.select_rules_to_close(pgsql, RULESET_REF)
    assert actual == expected


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_check_passes_double_post(
        taxi_billing_subventions_x, create_drafts, draft, clashing_rule,
):
    create_drafts(draft)
    query = _make_query(old_rule_ids=[CLASHING_RULE])
    await _make_request(taxi_billing_subventions_x, query)
    response = await _make_request(taxi_billing_subventions_x, query)
    assert response == {
        'change_doc_id': 'moscow:moscow_center:' + query['ruleset_ref'],
        'status': 'processing',
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_single_ride_returns_processing_for_new_draft(
        taxi_billing_subventions_x, create_drafts, draft,
):
    create_drafts(draft)
    query = _make_query()
    response = await _make_request(taxi_billing_subventions_x, query)
    assert response == {
        'status': 'processing',
        'change_doc_id': 'moscow:moscow_center:' + query['ruleset_ref'],
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_single_ride_schedules_stq_to_process_spec_for_new(
        taxi_billing_subventions_x, stq, create_drafts, draft,
):
    create_drafts(draft)
    await _make_request(taxi_billing_subventions_x, _make_query())
    queue = stq.billing_subventions_x_process_bulk_spec
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == RULESET_REF
    assert task['kwargs']['internal_draft_id'] == RULESET_REF
    expected_eta = datetime.datetime.fromisoformat(
        MOCK_NOW,
    ) + datetime.timedelta(seconds=5)
    assert task['eta'] == expected_eta.replace(tzinfo=None)


@pytest.fixture(name='draft')
def _add_draft(a_draft, a_subdraft, load_json):
    return a_draft(
        internal_draft_id=RULESET_REF,
        spec=load_json('bulk_single_ride_spec.json'),
        subdrafts=[
            a_subdraft(
                spec_ref='1',
                spec=load_json('bulk_single_ride_subdraft_spec1.json'),
            ),
            a_subdraft(
                spec_ref='2',
                spec=load_json('bulk_single_ride_subdraft_spec2.json'),
            ),
        ],
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


def _make_query(ruleset_ref=None, old_rule_ids=None):
    return {
        'ruleset_ref': ruleset_ref or RULESET_REF,
        'old_rule_ids': old_rule_ids or [],
    }


async def _make_request(bsx, query, status=200):
    url = '/v2/rules/single_ride/check'
    headers = {'X-YaTaxi-Draft-Author': 'me'}
    response = await bsx.post(url, query, headers=headers or {})
    assert response.status_code == status, response.json()
    return response.json()
