import pytest


@pytest.mark.parametrize(
    'status_code, response_body, message',
    [
        # that test checks all cases: when rule has tests, rule draft has
        # tests, rule has tests but deleted (see in rules.sql)
        (
            200,
            {
                'has_deleted': {'rule_id': 5, 'tests': ['test3']},
                'return_as_is': {'rule_id': 100, 'tests': ['test1', 'test2']},
                'only_draft': {'rule_id': 101, 'tests': ['test4']},
                'ternary': {'rule_id': 2, 'tests': ['test5']},
                'emit_meow_woof': {'rule_id': 4},
                'return_70': {'rule_id': 3},
            },
            None,
        ),
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['tests.sql'])
async def test_v1_testing_get_test(
        taxi_pricing_admin, status_code, response_body, message,
):
    response = await taxi_pricing_admin.get('v1/testing/rules', json={})

    assert response.status_code == status_code

    resp = response.json()
    if status_code == 200:
        assert resp == response_body
    else:
        assert resp['message'] == message


def rule_name_by_id(pgsql, rule_id):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        fields = ('name',)
        cursor.execute(
            f'SELECT {", ".join(fields)} '
            f'FROM price_modifications.rules '
            f'WHERE rule_id=%s',
            (rule_id,),
        )
        db_result = cursor.fetchall()
        tmp = db_result
        if tmp:
            return tmp[0]
        return None


def fetch_tests(pgsql, rule_ids, tests_by_rule_name):
    for rule_id in rule_ids:
        rule_name = rule_name_by_id(pgsql, rule_id)
        if rule_name is not None:
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
                tests_by_rule_name[rule_id] = {
                    t[0]: {fields[i]: t[i] for i in range(1, 4)}
                    for t in db_result
                }
    return tests_by_rule_name


@pytest.mark.pgsql('pricing_data_preparer', files=['tests_post.sql'])
@pytest.mark.parametrize(
    'body, code, test_results',
    [
        ({'rule_ids': [666]}, 404, {}),
        ({'rule_ids': [666, 555]}, 404, {}),
        ({'rule_ids': [666, 1]}, 404, {}),
        ({'rule_ids': [1, 666]}, 404, {}),
        (
            {'rule_ids': [1]},
            200,
            {
                1: {
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
            },
        ),
        (
            {'rule_ids': [1, 7]},
            200,
            {
                1: {
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
                7: {
                    'test3': {
                        'last_result': True,
                        'last_result_rule_id': 7,
                        'last_visited_lines': [1],
                    },
                    'test4': {
                        'last_result': True,
                        'last_result_rule_id': 7,
                        'last_visited_lines': [1],
                    },
                },
            },
        ),
        (
            {'rule_ids': [1, 2]},
            200,
            {
                1: {
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
                2: {
                    'test5': {
                        'last_result': False,
                        'last_result_rule_id': 2,
                        'last_visited_lines': [1],
                    },
                },
            },
        ),
        (
            {'rule_ids': [1, 7, 2]},
            200,
            {
                1: {
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
                2: {
                    'test5': {
                        'last_result': False,
                        'last_result_rule_id': 2,
                        'last_visited_lines': [1],
                    },
                },
                7: {
                    'test3': {
                        'last_result': True,
                        'last_result_rule_id': 7,
                        'last_visited_lines': [1],
                    },
                    'test4': {
                        'last_result': True,
                        'last_result_rule_id': 7,
                        'last_visited_lines': [1],
                    },
                },
            },
        ),
        ({'rule_ids': []}, 400, {}),
        (
            {'rule_ids': [100]},
            200,
            {
                100: {
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
                        'last_result': False,
                        'last_result_rule_id': 100,
                        'last_visited_lines': [1],
                    },
                    'test_rule_pass': {
                        'last_result': True,
                        'last_result_rule_id': 100,
                        'last_visited_lines': [1],
                    },
                },
            },
        ),
        (
            {'rule_ids': [101]},
            200,
            {
                101: {
                    'test6': {
                        'last_result': True,
                        'last_result_rule_id': 101,
                        'last_visited_lines': [1],
                    },
                    'test_1_can_pass': {
                        'last_result': True,
                        'last_result_rule_id': 101,
                        'last_visited_lines': [1],
                    },
                },
            },
        ),
        (
            {'rule_ids': [1, 100]},
            200,
            {
                1: {
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
                        'last_result': False,
                        'last_result_rule_id': 100,
                        'last_visited_lines': [1],
                    },
                    'test_rule_pass': {
                        'last_result': True,
                        'last_result_rule_id': 100,
                        'last_visited_lines': [1],
                    },
                },
                100: {
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
                        'last_result': False,
                        'last_result_rule_id': 100,
                        'last_visited_lines': [1],
                    },
                    'test_rule_pass': {
                        'last_result': True,
                        'last_result_rule_id': 100,
                        'last_visited_lines': [1],
                    },
                },
            },
        ),
    ],
    ids=[
        'absent_rule',
        'absent_rules',
        'absent_and_return_as_is_rules',
        'return_as_is_and_absent_rules',
        'return_as_is',
        'return_as_is_two',
        'return_as_is_and_ternary',
        'three_rules',
        'no_rule_ids',
        'draft_rule',
        'only_draft_rule',
        'return_as_is_normal_and_draft',
    ],
)
async def test_v1_testing_rules_post(
        taxi_pricing_admin, pgsql, body, code, test_results, testpoint,
):
    @testpoint('testing_finished')
    def testing_finished(data):
        pass

    @testpoint('before_testing')
    def before_testing(data):
        rule_ids = body['rule_ids']
        db_tests_before = {}
        fetch_tests(pgsql, body['rule_ids'], db_tests_before)
        for rule_id in rule_ids:
            if db_tests_before.get(rule_id) is None:
                continue
            for test in db_tests_before[rule_id].values():
                assert test['last_result'] is None
                assert test['last_result_rule_id'] is None

    response = await taxi_pricing_admin.post('v1/testing/rules', json=body)
    assert response.status_code == code

    if response.status_code == 200:
        await before_testing.wait_call()
        await testing_finished.wait_call()
        db_tests = {}
        fetch_tests(pgsql, body['rule_ids'], db_tests)
        assert test_results == db_tests
