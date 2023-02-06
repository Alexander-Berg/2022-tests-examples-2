import pytest

URL = '/internal/eats-proactive-support/v1/problem'


@pytest.mark.parametrize(
    'order_nr, expected_status_code',
    [
        ('100000-100000', 200),  # exist_problems_and_actions
        ('100001-100000', 200),  # not_exist_actions
        ('100011-100000', 200),  # not_exist_problems
        ('100111-100000', 404),  # not_exist_order_nr
        ({}, 400),  # empty_order_nr
    ],
    ids=[
        'exist_problems_and_actions',
        'not_exist_actions',
        'not_exist_problems',
        'not_exist_order_nr',
        'empty_order_nr',
    ],
)
@pytest.mark.pgsql(
    'eats_proactive_support', files=['fill_problems_and_actions.sql'],
)
async def test_get_problem(
        taxi_eats_proactive_support, load_json, order_nr, expected_status_code,
):
    if order_nr:
        params = {'order_nr': order_nr}
    else:
        params = {}
    response = await taxi_eats_proactive_support.get(URL, params=params)

    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        expected_response = load_json('response_problems.json')[order_nr]
        expected_problems = expected_response['problems']
        expected_problems = sorted(
            expected_problems, key=lambda x: x['problem_id'],
        )  # data received from unordered_map
        for problem in expected_problems:
            problem['actions'] = sorted(
                problem['actions'], key=lambda x: x['action_id'],
            )
        expected_response['problems'] = expected_problems
        assert response.json() == expected_response


@pytest.fixture(scope='function')
async def test_get_problem_db_lost(taxi_eats_proactive_support, pgsql):

    cursor = pgsql['eats_proactive_support'].cursor()
    query = 'DROP TABLE eats_proactive_support.problems;'

    cursor.execute(query)
    response = await taxi_eats_proactive_support.get(
        URL, params={'order_nr': '100000-100000'},
    )
    cursor.close()
    assert response.status_code == 500
