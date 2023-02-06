import pytest

from testsuite.utils import ordered_object


@pytest.mark.parametrize(
    'rule_ids',
    (
        # single_ride
        ['2abf062a-b607-11ea-998e-07e60204cbcf'],
        # goal
        ['5e03538d-740b-4e0b-b5f4-1425efa59319'],
        # single_ride + goal
        [
            'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
            '5e03538d-740b-4e0b-b5f4-1425efa59319',
        ],
        # on_top
        ['5e03538d-740b-4e0b-b5f4-1425efa59329'],
    ),
)
async def test_v2_rules_by_ids(taxi_billing_subventions_x, rule_ids):
    query = {'rules': rule_ids}
    response = await _make_request(taxi_billing_subventions_x, query)
    actual = [rule['id'] for rule in response['rules']]
    ordered_object.assert_eq(actual, rule_ids, '')


async def _make_request(taxi_billing_subventions_x, query):
    response = await taxi_billing_subventions_x.post('/v2/rules/by_ids', query)
    assert response.status_code == 200, response.json()
    return response.json()


@pytest.fixture(autouse=True)
def _fill_db(a_single_ride, a_goal, a_single_ontop, create_rules):
    create_rules(
        a_single_ride(id='2abf062a-b607-11ea-998e-07e60204cbcf'),
        a_single_ride(id='cf730f12-c02b-11ea-acc8-ab6ac87f7711'),
        a_goal(id='5e03538d-740b-4e0b-b5f4-1425efa59319'),
        a_single_ontop(id='5e03538d-740b-4e0b-b5f4-1425efa59329'),
    )
