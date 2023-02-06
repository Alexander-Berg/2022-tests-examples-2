import datetime

import pytest

from testsuite.utils import ordered_object

from tests_billing_subventions_x import dbhelpers

MOCK_NOW = '2021-05-28T11:31:00+00:00'

INTERNAL_DRAFT_ID = 'e12d920f0a0839f3743b38ffe28747cd'
UNIQUE_DRIVER_ID = 'cf40da71-7a66-405f-811b-96432d8a56a2'


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_returns_processing_for_new_draft(
        taxi_billing_subventions_x,
):
    response = await _make_request(taxi_billing_subventions_x, _make_query())
    assert response == {
        'status': 'processing',
        'change_doc_id': INTERNAL_DRAFT_ID,
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_schedules_stq_to_process_spec_for_new(
        taxi_billing_subventions_x, stq,
):
    await _make_request(taxi_billing_subventions_x, _make_query())
    queue = stq.billing_subventions_x_process_bulk_spec
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == INTERNAL_DRAFT_ID
    assert task['kwargs']['internal_draft_id'] == INTERNAL_DRAFT_ID
    expected_eta = datetime.datetime.fromisoformat(
        MOCK_NOW,
    ) + datetime.timedelta(seconds=5)
    assert task['eta'] == expected_eta.replace(tzinfo=None)


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_creates_draft_spec(
        taxi_billing_subventions_x, pgsql,
):
    await _make_request(taxi_billing_subventions_x, _make_query())
    spec = dbhelpers.get_draft_spec(pgsql, INTERNAL_DRAFT_ID)
    assert spec['creator'] == 'me'
    assert spec['spec'] == {
        'budget': {
            'weekly': '1000',
            'rolling': False,
            'threshold': 100,
            'weekly_validation': False,
            'daily_validation': False,
        },
        'currency': 'RUB',
        'end': '2021-06-07T21:00:00+00:00',
        'start': '2021-05-31T21:00:00+00:00',
        'path': '//path/to/yt/table',
    }
    assert spec['state'] == 'GENERATING'
    assert spec['error'] is None


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_returns_processing_when_empty_yet(
        taxi_billing_subventions_x, create_drafts, draft,
):
    create_drafts(draft)
    response = await _make_request(taxi_billing_subventions_x, _make_query())
    assert response == {
        'status': 'processing',
        'change_doc_id': INTERNAL_DRAFT_ID,
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_returns_processing_when_not_completed(
        taxi_billing_subventions_x, create_drafts, draft, a_subdraft,
):
    draft['subdrafts'] = [
        a_subdraft(spec_ref='1', spec={}, is_completed=True),
        a_subdraft(spec_ref='2', spec={}, is_completed=False),
    ]
    create_drafts(draft)
    response = await _make_request(taxi_billing_subventions_x, _make_query())
    assert response == {
        'status': 'processing',
        'change_doc_id': INTERNAL_DRAFT_ID,
    }


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_returns_results_of_processing(
        taxi_billing_subventions_x, completed, create_drafts, pgsql,
):
    create_drafts(completed)
    response = await _make_request(taxi_billing_subventions_x, _make_query())
    assert response == {
        'change_doc_id': INTERNAL_DRAFT_ID,
        'data': {
            'doc_id': INTERNAL_DRAFT_ID,
            'request': {
                'budget': {
                    'weekly': '1000',
                    'rolling': False,
                    'threshold': 100,
                    'weekly_validation': False,
                    'daily_validation': False,
                },
                'currency': 'RUB',
                'end': '2021-06-07T21:00:00+00:00',
                'start': '2021-05-31T21:00:00+00:00',
                'path': '//path/to/yt/table',
            },
            'info': {
                'geonodes': {'z1/z11': 1, 'z1/z12': 2},
                'total': 2,
                'failed': 0,
                'errors': [],
                'clashes_with_drafts': [],
            },
        },
        'status': 'completed',
    }
    spec = dbhelpers.get_draft_spec(pgsql, INTERNAL_DRAFT_ID)
    assert spec['state'] == 'GENERATED'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    BILLING_SUBVENTIONS_BULK_PERSONAL_MAX_ALLOWED_ERROR_RATE=10,
)
async def test_v2_rules_personal_goal_returns_errors_for_specs(
        taxi_billing_subventions_x, draft, create_drafts, a_subdraft,
):
    broken = a_subdraft(
        spec_ref='1',
        spec={},
        error='This spec is broken somehow',
        is_completed=True,
    )
    correct = [
        a_subdraft(spec_ref=str(i), spec={}, is_completed=True)
        for i in range(2, 11)
    ]
    draft['subdrafts'] = [broken] + correct
    create_drafts(draft)
    response = await _make_request(taxi_billing_subventions_x, _make_query())
    assert response['data']['info']['errors'] == [
        '1: This spec is broken somehow',
    ]


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_returns_clashing_drafts(
        taxi_billing_subventions_x, completed, create_drafts, clashing_rules,
):
    create_drafts(completed)
    response = await _make_request(taxi_billing_subventions_x, _make_query())
    ordered_object.assert_eq(
        response['data']['info']['clashes_with_drafts'],
        ['12345', '54321'],
        '',
    )


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_fails_when_too_many_errors(
        taxi_billing_subventions_x, draft, create_drafts, a_subdraft, pgsql,
):
    broken = a_subdraft(
        spec_ref='1',
        spec={},
        error='This spec is broken somehow',
        is_completed=True,
    )
    correct = a_subdraft(spec_ref='2', spec={}, is_completed=True)
    draft['subdrafts'] = [broken, correct]
    create_drafts(draft)
    response = await _make_request(
        taxi_billing_subventions_x, _make_query(), 400,
    )
    error = 'Broken specs rate too high: 50.00%. Must be <= 5%'
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': error,
        'details': {'errors': ['1: This spec is broken somehow']},
    }
    spec = dbhelpers.get_draft_spec(pgsql, INTERNAL_DRAFT_ID)
    assert spec['state'] == 'INVALID'
    assert spec['error'] == error


@pytest.mark.now(MOCK_NOW)
async def test_v2_rules_personal_goal_fails_when_yt_table_not_available(
        yt_apply, taxi_billing_subventions_x, stq_runner, pgsql,
):
    query = _make_query()
    query['path'] = '//path/to/nonexistent/table'
    response = await _make_request(taxi_billing_subventions_x, query)
    internal_draft_id = response['change_doc_id']
    await stq_runner.billing_subventions_x_process_bulk_spec.call(
        task_id='id', kwargs={'internal_draft_id': internal_draft_id},
    )
    response = await _make_request(taxi_billing_subventions_x, query, 400)
    assert response['code'] == 'INCORRECT_PARAMETERS'
    expected = 'Error resolving path {}'.format(query['path'])
    assert expected in response['message']
    spec = dbhelpers.get_draft_spec(pgsql, internal_draft_id)
    assert spec['state'] == 'INVALID'
    assert expected in spec['error']


@pytest.mark.now(MOCK_NOW)
@pytest.mark.yt(
    schemas=['yt_bulk_goals_schema.yaml'],
    static_table_data=['yt_bulk_goals_empty.yaml'],
)
async def test_v2_rules_personal_goal_fails_when_yt_table_is_empty(
        taxi_billing_subventions_x, yt_apply, stq_runner, pgsql,
):
    query = _make_query()
    response = await _make_request(taxi_billing_subventions_x, query)
    internal_draft_id = response['change_doc_id']
    await stq_runner.billing_subventions_x_process_bulk_spec.call(
        task_id='id', kwargs={'internal_draft_id': internal_draft_id},
    )
    response = await _make_request(taxi_billing_subventions_x, query, 400)
    error = 'Bulk draft has no specs'
    assert response == {
        'code': 'INCORRECT_PARAMETERS',
        'message': error,
        'details': {'errors': [f'e12d920f0a0839f3743b38ffe28747cd: {error}']},
    }
    spec = dbhelpers.get_draft_spec(pgsql, internal_draft_id)
    assert spec['state'] == 'INVALID'
    assert spec['error'] == error


@pytest.fixture(name='draft')
def _make_empty_draft(a_draft):
    return a_draft(
        internal_draft_id=INTERNAL_DRAFT_ID,
        spec={
            'budget': {'weekly': '1000'},
            'currency': 'RUB',
            'end': '2021-06-08T00:00:00+03:00',
            'start': '2021-06-01T00:00:00+03:00',
            'path': '//path/to/yt/table',
        },
    )


@pytest.fixture(name='completed')
def _make_completed_draft(draft, a_subdraft, a_goal):
    draft['subdrafts'] = [
        a_subdraft(spec_ref='1', spec={}, is_completed=True),
        a_subdraft(spec_ref='2', spec={}, is_completed=True),
    ]
    draft['rules'] = [
        a_goal(
            geonode='z1/z11',
            end='2021-06-07T21:00:00+00:00',
            start='2021-05-31T21:00:00+00:00',
            unique_driver_id=UNIQUE_DRIVER_ID,
        ),
        a_goal(
            geonode='z1/z12',
            end='2021-06-07T21:00:00+00:00',
            start='2021-05-31T21:00:00+00:00',
            unique_driver_id=UNIQUE_DRIVER_ID,
        ),
        a_goal(
            geonode='z1/z12',
            tag='a_tag',
            end='2021-06-07T21:00:00+00:00',
            start='2021-05-31T21:00:00+00:00',
            unique_driver_id=UNIQUE_DRIVER_ID,
        ),
    ]
    return draft


@pytest.fixture(name='clashing_rules')
def _make_clashing_rules(create_rules, a_goal):
    create_rules(
        a_goal(
            geonode='z1/z11',
            end='2021-06-03T21:00:00+00:00',
            start='2021-05-21T21:00:00+00:00',
            unique_driver_id=UNIQUE_DRIVER_ID,
        ),
        a_goal(
            geonode='z1/z12',
            end='2021-06-03T21:00:00+00:00',
            start='2021-05-21T21:00:00+00:00',
            unique_driver_id=UNIQUE_DRIVER_ID,
        ),
        draft_id='12345',
    )
    create_rules(
        a_goal(
            geonode='z1/z12',
            tag='a_tag',
            end='2021-06-07T21:00:00+00:00',
            start='2021-05-31T21:00:00+00:00',
            unique_driver_id=UNIQUE_DRIVER_ID,
        ),
        draft_id='54321',
    )
    create_rules(
        a_goal(
            geonode='z2/z21',
            end='2021-06-07T21:00:00+00:00',
            start='2021-05-31T21:00:00+00:00',
            unique_driver_id=UNIQUE_DRIVER_ID,
        ),
        draft_id='22222',
    )


def _make_query():
    return {
        'budget': {'weekly': '1000'},
        'currency': 'RUB',
        'end': '2021-06-08T00:00:00+03:00',
        'start': '2021-06-01T00:00:00+03:00',
        'path': '//path/to/yt/table',
    }


async def _make_request(bsx, query, status=200):
    url = '/v2/rules/personal_goal/create'
    headers = {'X-YaTaxi-Draft-Author': 'me'}
    response = await bsx.post(url, query, headers=headers or {})
    assert response.status_code == status, response.json()
    return response.json()
