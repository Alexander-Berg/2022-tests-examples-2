import pytest


def fetch_tests(pgsql, rule_name):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        fields = (
            'test_name',
            'last_result',
            'last_result_rule_id',
            'last_visited_lines',
        )
        cursor.execute(
            f'SELECT {", ".join(fields)} '
            f'FROM price_modifications.tests '
            f'WHERE rule_name=%s',
            (rule_name,),
        )
        db_result = cursor.fetchall()
        return {
            t[0]: {fields[i]: t[i] for i in range(1, 4)} for t in db_result
        }


@pytest.mark.pgsql('pricing_data_preparer', files=['tests.sql'])
@pytest.mark.parametrize(
    'rule_name, rule_id, code, test_results, source',
    [
        ('absent_rule', 666, 400, {}, None),
        (
            'return_as_is',
            1,
            200,
            {
                'test_1_can_pass': {
                    'last_result': True,
                    'last_result_rule_id': 1,
                    'last_visited_lines': [1],
                },
                'test_1_cannot_pass': {
                    'last_result': False,
                    'last_result_rule_id': 1,
                    'last_visited_lines': [1],
                },
                'test_draft_pass': {
                    'last_result': False,
                    'last_result_rule_id': 1,
                    'last_visited_lines': [1],
                },
                'test_rule_pass': {
                    'last_result': True,
                    'last_result_rule_id': 1,
                    'last_visited_lines': [1],
                },
            },
            None,
        ),
        (
            'return_as_is',
            100,
            200,
            {
                'test_1_can_pass': {
                    'last_result': True,
                    'last_result_rule_id': 100,
                    'last_visited_lines': [1],
                },
                'test_1_cannot_pass': {
                    'last_result': False,
                    'last_result_rule_id': 100,
                    'last_visited_lines': [1],
                },
                'test_draft_pass': {
                    'last_result': True,
                    'last_result_rule_id': 100,
                    'last_visited_lines': [1],
                },
                'test_rule_pass': {
                    'last_result': False,
                    'last_result_rule_id': 100,
                    'last_visited_lines': [1],
                },
            },
            None,
        ),
        ('return_as_is', 122, 400, {}, None),
        ('emit_meow_woof', 4, 200, {}, None),
        (
            'only_draft',
            101,
            200,
            {
                'test_1_can_pass': {
                    'last_result': True,
                    'last_result_rule_id': 101,
                    'last_visited_lines': [1],
                },
                'test_2_can_pass': {
                    'last_result': True,
                    'last_result_rule_id': 101,
                    'last_visited_lines': [1],
                },
                'test_1_cannot_pass': {
                    'last_result': False,
                    'last_result_rule_id': 101,
                    'last_visited_lines': [1],
                },
                'test_2_cannot_pass': {
                    'last_result': None,
                    'last_result_rule_id': None,
                    'last_visited_lines': None,
                },
                'test_3_cannot_pass': {
                    'last_result': False,
                    'last_result_rule_id': 101,
                    'last_visited_lines': [1],
                },
            },
            None,
        ),
        (
            'return_as_is',
            None,
            200,
            {
                'test_1_can_pass': {
                    'last_result': True,
                    'last_result_rule_id': 1,
                    'last_visited_lines': [1],
                },
                'test_1_cannot_pass': {
                    'last_result': False,
                    'last_result_rule_id': 1,
                    'last_visited_lines': [1],
                },
                'test_draft_pass': {
                    'last_result': False,
                    'last_result_rule_id': 1,
                    'last_visited_lines': [1],
                },
                'test_rule_pass': {
                    'last_result': False,
                    'last_result_rule_id': 1,
                    'last_visited_lines': [1],
                },
            },
            'return ride.price*10;',
        ),
    ],
    ids=[
        'absent_rule',
        'return_as_is_rule',
        'return_as_is_draft',
        'return_as_is_fake',
        'emit_meow_woof_no_test',
        'only_draft',
        'return_as_if_other_source',
    ],
)
async def test_v1_testing_rule_post(
        taxi_pricing_admin,
        pgsql,
        rule_name,
        rule_id,
        code,
        test_results,
        source,
):
    query = {'rule_name': rule_name}
    if rule_id:
        query['rule_id'] = rule_id
    body = {}
    if source:
        body['source'] = source
    response = await taxi_pricing_admin.post(
        'v1/testing/rule', params=query, json=body,
    )
    assert response.status_code == code

    if response.status_code == 200:
        db_tests = fetch_tests(pgsql, rule_name)
        assert test_results == db_tests
        resp = response.json()
        assert len(resp['tests_results']) == len(db_tests)
        for test in resp['tests_results']:
            assert test['name'] in test_results
            if 'test_result' in test:
                assert (
                    test['test_result']
                    == db_tests[test['name']]['last_result']
                )
            else:
                assert db_tests[test['name']]['last_result'] is None


@pytest.mark.parametrize(
    'body, status_code, response_body, message',
    [
        (
            {'rule_name': 'return_as_is'},
            200,
            {
                'tests': [
                    {'name': 'test1', 'test_result': True},
                    {'name': 'test2', 'test_result': True},
                ],
            },
            None,
        ),
        (
            {'rule_name': 'has_deleted'},
            200,
            {'tests': [{'name': 'test3', 'test_result': True}]},
            None,
        ),
        (
            {'rule_name': 'only_draft'},
            200,
            {'tests': [{'name': 'test4', 'test_result': True}]},
            None,
        ),
        (
            {'rule_name': 'other_deleted'},
            200,
            {
                'tests': [
                    {'name': 'test5', 'test_result': True},
                    {'name': 'test6', 'test_result': True},
                    {'name': 'test7', 'test_result': True},
                ],
            },
            None,
        ),
        (
            {'rule_name': 'other_deleted', 'rule_id': 7},
            200,
            {
                'tests': [
                    {'name': 'test5', 'test_result': True},
                    {'name': 'test6'},
                    {'name': 'test7'},
                ],
            },
            None,
        ),
        (
            {'rule_name': 'return_as_is', 'rule_id': 5},
            400,
            {},
            'Rule id doesn\'t match rule name.',
        ),
        (
            {'rule_name': 'return_as_is', 'rule_id': 100500},
            404,
            {},
            'Rule name with corresponding id not found.',
        ),
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['tests_get.sql'])
async def test_v1_testing_get_test(
        taxi_pricing_admin, body, status_code, response_body, message,
):
    if 'rule_id' in body:
        response = await taxi_pricing_admin.get(
            'v1/testing/rule',
            params={
                'rule_name': body['rule_name'],
                'rule_id': body['rule_id'],
            },
            json=body,
        )
    else:
        response = await taxi_pricing_admin.get(
            'v1/testing/rule',
            params={'rule_name': body['rule_name']},
            json=body,
        )

    assert response.status_code == status_code

    resp = response.json()
    if status_code == 200:
        assert resp == response_body
    else:
        assert resp['message'] == message
