import pytest

from testsuite.utils import ordered_object


async def test_v2_rules_by_draft_returns_empty_when_drafts_not_found(
        taxi_billing_subventions_x,
):
    draft_id = 'xxxx'
    query = {'drafts': [draft_id]}
    response = await _make_request(taxi_billing_subventions_x, query)
    assert response == {
        'rules': [{'added': [], 'closed': [], 'draft_id': draft_id}],
    }


@pytest.mark.parametrize(
    'draft_id,added,closed',
    (
        # single_ride
        (
            '3',
            ['d925acbe-1db8-11eb-bc2e-53895cbfad2e'],
            ['cf730f12-c02b-11ea-acc8-ab6ac87f7711'],
        ),
        # goal
        (
            '30',
            ['26801c8e-9f6d-460e-924d-d0453f15b02a'],
            ['f450999a-cd8b-4563-ab8c-178b3788cd33'],
        ),
        # on_top
        (
            '31',
            ['26801c8e-9f6d-460e-924d-d0453f15b02b'],
            ['f450999a-cd8b-4563-ab8c-178b3788cd34'],
        ),
    ),
)
async def test_v2_rules_by_draft_returns_rules(
        taxi_billing_subventions_x, draft_id, added, closed,
):
    query = {'drafts': [draft_id]}
    response = await _make_request(taxi_billing_subventions_x, query)
    actual = response['rules'][0]
    ordered_object.assert_eq(_extract_ids(actual['added']), added, '')
    ordered_object.assert_eq(_extract_ids(actual['closed']), closed, '')


async def test_v2_rules_by_draft_returns_data_for_all_requested_drafts(
        taxi_billing_subventions_x,
):
    draft_ids = ['3', '30', '31']
    query = {'drafts': ['3', '30', '31']}
    response = await _make_request(taxi_billing_subventions_x, query)
    assert len(response['rules']) == len(draft_ids)
    ordered_object.assert_eq(
        [r['draft_id'] for r in response['rules']], draft_ids, '',
    )


def _extract_ids(data):
    return [rule['id'] for rule in data]


@pytest.fixture(autouse=True)
def _fill_db(create_rules, a_single_ride, a_goal, a_single_ontop):
    create_rules(a_single_ride(id='cf730f12-c02b-11ea-acc8-ab6ac87f7711'))
    create_rules(
        a_single_ride(id='d925acbe-1db8-11eb-bc2e-53895cbfad2e'),
        draft_id='3',
        changed=['cf730f12-c02b-11ea-acc8-ab6ac87f7711'],
    )
    create_rules(a_goal(id='f450999a-cd8b-4563-ab8c-178b3788cd33'))
    create_rules(
        a_goal(id='26801c8e-9f6d-460e-924d-d0453f15b02a'),
        draft_id='30',
        changed=['f450999a-cd8b-4563-ab8c-178b3788cd33'],
    )
    create_rules(a_single_ontop(id='f450999a-cd8b-4563-ab8c-178b3788cd34'))
    create_rules(
        a_single_ontop(id='26801c8e-9f6d-460e-924d-d0453f15b02b'),
        draft_id='31',
        changed=['f450999a-cd8b-4563-ab8c-178b3788cd34'],
    )


async def _make_request(taxi_billing_subventions_x, query):
    response = await taxi_billing_subventions_x.post(
        '/v2/rules/by_draft', query,
    )
    assert response.status_code == 200, response.json()
    return response.json()
