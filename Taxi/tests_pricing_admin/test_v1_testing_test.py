# pylint: disable=too-many-lines
import copy

import pytest

from testsuite.utils import approx

from tests_pricing_admin import helpers


def fetch_test(pgsql, test_name, rule_name):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        fields = (
            'test_name',
            'backend_variables',
            'trip_details',
            'initial_price',
            'output_price',
            'output_meta',
            'last_result',
            'last_result_rule_id',
            'rule_name',
            'price_calc_version',
        )
        cursor.execute(
            f'SELECT {", ".join(fields)} '
            f'FROM price_modifications.tests '
            f'WHERE test_name=%s AND rule_name=%s',
            (test_name, rule_name),
        )
        result = cursor.fetchall()
        if not result:
            return None
        return {k: v for k, v in zip(fields, result[0])}


def does_test_exist(pgsql, rule_name, test_name):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'SELECT test_name '
            'FROM price_modifications.tests '
            'WHERE rule_name = %s AND test_name = %s',
            (rule_name, test_name),
        )
        return cursor.fetchone() is not None


ZERO_TRIP_DETAILS = {
    'total_distance': 0,
    'total_time': 0,
    'waiting_time': 0,
    'waiting_in_transit_time': 0,
    'waiting_in_destination_time': 0,
    'user_options': {},
    'user_meta': {},
}

BACKEND_VARS = {
    'surge_params': {
        'explicit_antisurge': {'value': 0.5},
        'value': 1.0,
        'value_raw': 1.0,
        'value_smooth': 1.0,
    },
    'user_tags': [],
    'requirements': {'select': {}, 'simple': []},
    'tariff': {
        'boarding_price': 129.0,
        'minimum_price': 0.0,
        'requirement_prices': {
            'animaltransport': 150.0,
            'bicycle': 150.0,
            'check': 0.0,
            'childchair_moscow': 100.0,
            'conditioner': 0.0,
            'nosmoking': 0.0,
            'waiting_in_transit': 9.0,
            'yellowcarnumber': 0.0,
        },
        'requirements_included_one_of': ['some_fake_requirement'],
        'waiting_price': {'free_waiting_time': 180, 'price_per_minute': 9.0},
    },
    'user_data': {'has_yaplus': False},
    'category_data': {'decoupling': False, 'fixed_price': True},
    'payment_type': 'SOME_PAYMENT_TYPE',
    'experiments': [],
}

INVALID_BACKEND_VARS = {'surge_params': 42}


DEFAULT_BODY = {
    'backend_variables': {},
    'trip_details': ZERO_TRIP_DETAILS,
    'initial_price': helpers.make_price(0),
}


class AnyNumber:
    def __eq__(self, other):
        return isinstance(other, int)


ANY_NUMBER = AnyNumber()

EXECUTION_STATISTICS = {
    'sizes': {
        'bytecode_fix_price': ANY_NUMBER,
        'bytecode_taximeter_price': ANY_NUMBER,
        'raw_ast': ANY_NUMBER,
        'simplified_ast_fix_price': ANY_NUMBER,
        'simplified_ast_taximeter_price': ANY_NUMBER,
    },
    'timings': {
        'ast_interpretation': ANY_NUMBER,
        'ast_parsing': ANY_NUMBER,
        'ast_serialization': ANY_NUMBER,
        'bytecode_interpretation_fix_price': ANY_NUMBER,
        'bytecode_interpretation_taximeter_price': ANY_NUMBER,
        'compilation': ANY_NUMBER,
        'source_code_parsing': ANY_NUMBER,
    },
}


@pytest.mark.config(
    PRICING_DATA_PREPARER_METADATA_MAPPING={
        'meow': {'taximeter': True, 'backend': True},
        'woof': {'taximeter': True, 'backend': True},
    },
)
@pytest.mark.parametrize(
    'body, rule_name, test_name, request_rule_id,'
    ' test_result, last_test_result_id, status_code',
    [
        (  # OK_return_0
            {
                'backend_variables': BACKEND_VARS,
                'output_price': helpers.make_price(0),
                'output_meta': {},
            },
            'return_as_is',
            'test',
            1,
            True,
            1,
            200,
        ),
        (  # OK_empty_backend_variables
            {'output_price': helpers.make_price(0), 'output_meta': {}},
            'return_as_is',
            'test',
            1,
            True,
            1,
            200,
        ),
        (  # OK_ternary
            {
                'initial_price': helpers.split_price(7),
                'output_price': helpers.split_price(10),
                'output_meta': {},
            },
            'ternary',
            'test',
            None,
            True,
            2,
            200,
        ),
        (  # OK_return_70
            {
                'initial_price': helpers.make_price(1),
                'output_price': helpers.make_price(10),
                'output_meta': {},
            },
            'return_70',
            'test',
            None,
            True,
            3,
            200,
        ),
        (  # OK_metadata_emit_epsent
            {
                'output_meta': {'meow': 42, 'woof': 24},
                'output_price': helpers.make_price(0),
                'price_calc_version': '13',
            },
            'emit_meow_woof',
            'test',
            None,
            True,
            4,
            200,
        ),
        (  # 400_invalid_backend_variables
            {
                'backend_variables': INVALID_BACKEND_VARS,
                'output_price': helpers.make_price(0),
                'output_meta': {},
            },
            'return_as_is',
            'test',
            None,
            True,
            None,
            400,
        ),
        (  # OK_update_existent_rule
            {
                'backend_variables': BACKEND_VARS,
                'trip_details': ZERO_TRIP_DETAILS,
                'initial_price': helpers.make_price(1),
                'output_meta': {'meow': 42, 'woof': 24},
                'output_price': helpers.make_price(0),
                'price_calc_version': '13',
            },
            'return_as_is',
            'existent_test',
            None,
            False,
            100,
            200,
        ),
        (  # OK_unexistent_rule
            {'output_price': helpers.make_price(0), 'output_meta': {}},
            'unexistent_rule',
            'test',
            None,
            None,
            None,
            200,
        ),
        (  # OK_mismatched_metadata
            {
                'output_meta': {'meow': 42},
                'output_price': helpers.make_price(0),
            },
            'emit_meow_woof',
            'test',
            None,
            False,
            4,
            200,
        ),
        (  # OK_mismatched_price
            {'output_price': helpers.make_price(1), 'output_meta': {}},
            'return_as_is',
            'test',
            1,
            False,
            1,
            200,
        ),
        (
            {'output_price': helpers.make_price(0), 'output_meta': {}},
            'return_as_is',
            'test',
            None,
            True,
            100,
            200,
        ),  # OK_prefer_drafts
        (
            {'output_price': helpers.make_price(0), 'output_meta': {}},
            'has_deleted',
            'test',
            None,
            True,
            5,
            200,
        ),  # OK_skip_deleted_rules
        (
            {'output_price': helpers.make_price(0), 'output_meta': {}},
            'only_draft',
            'test',
            None,
            True,
            101,
            200,
        ),  # OK_draft_wo_rule
    ],
    ids=[
        'OK_return_0',
        'OK_empty_backend_variables',
        'OK_ternary',
        'OK_return_70',
        'OK_metadata_emit_epsent',
        '400_invalid_backend_variables',
        'OK_update_existent_rule',
        'OK_unexistent_rule',
        'OK_mismatched_metadata',
        'OK_mismatched_price',
        'OK_prefer_drafts',
        'OK_skip_deleted_rules',
        'OK_draft_wo_rule',
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_v1_testing_test_put(
        taxi_pricing_admin,
        pgsql,
        body,
        rule_name,
        test_name,
        request_rule_id,
        test_result,
        last_test_result_id,
        status_code,
        mockserver,
):
    test_body = copy.deepcopy(DEFAULT_BODY)
    test_body.update(body)

    request_body = {'test': test_body}
    if request_rule_id:
        request_body['rule_id'] = request_rule_id

    @mockserver.json_handler('taxi-approvals/v2/drafts/')
    def _mock_approvals_drafts_get(request):
        data = request.args
        assert 'id' in data
        return {
            'id': int(data['id']),
            'version': 1,
            'status': 'succeeded',
            'data': {},  # empty because unused
        }

    @mockserver.json_handler('pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'ok', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    response = await taxi_pricing_admin.put(
        'v1/testing/test',
        params={'rule_name': rule_name, 'test_name': test_name},
        json=request_body,
    )

    assert response.status_code == status_code
    if status_code == 200:
        db_test = approx.wrap_json(fetch_test(pgsql, test_name, rule_name))
        assert db_test['last_result'] == test_result
        assert db_test['last_result_rule_id'] == last_test_result_id
        assert db_test['backend_variables'] == test_body['backend_variables']
        assert db_test['trip_details'] == test_body['trip_details']
        assert db_test['initial_price'] == test_body['initial_price']
        if 'output_price' in test_body:
            assert db_test['output_price'] == test_body['output_price']
        if 'output_meta' in test_body:
            assert db_test['output_meta'] == test_body['output_meta']
        if 'price_calc_version' in test_body:
            assert (
                db_test['price_calc_version']
                == test_body['price_calc_version']
            )


@pytest.mark.config(
    PRICING_DATA_PREPARER_METADATA_MAPPING={
        'meow': {'taximeter': True, 'backend': True},
        'woof': {'taximeter': True, 'backend': True},
    },
)
@pytest.mark.pgsql('pricing_data_preparer', files=['tests.sql'])
@pytest.mark.parametrize(
    'rule_name, test_name, body, code, result, result_id',
    [
        (  # from_db_pass_rule
            'return_as_is',
            'test_1_can_pass',
            {'rule_id': 1},
            200,
            {
                'result': True,
                'output_price': helpers.make_price(0),
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            1,
        ),
        (  # from_db_pass_draft
            'return_as_is',
            'test_1_can_pass',
            {},
            200,
            {
                'result': True,
                'output_price': helpers.make_price(0),
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            100,
        ),
        (  # from_db_not_pass_rule
            'return_as_is',
            'test_1_cannot_pass',
            {'rule_id': 1},
            200,
            {
                'result': False,
                'output_price': helpers.make_price(28),
                'output_price_lighting': [
                    'boarding',
                    'distance',
                    'time',
                    'waiting',
                    'requirements',
                    'transit_waiting',
                    'destination_waiting',
                ],
                'error': (
                    'Actual result Mismatches expected, check the result table'
                ),
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            1,
        ),
        (  # from_db_not_pass_draft
            'return_as_is',
            'test_1_cannot_pass',
            {},
            200,
            {
                'result': False,
                'output_price': helpers.make_price(56),
                'output_price_lighting': [
                    'boarding',
                    'distance',
                    'time',
                    'waiting',
                    'requirements',
                    'transit_waiting',
                    'destination_waiting',
                ],
                'error': (
                    'Actual result Mismatches expected, check the result table'
                ),
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            100,
        ),
        (  # from_db_almost_pass_rule
            'return_as_is',
            'test_1_almost_pass',
            {'rule_id': 1},
            200,
            {
                'result': False,
                'output_price': helpers.fill_price(
                    boarding=28,
                    waiting=28,
                    transit_waiting=28,
                    destination_waiting=28,
                ),
                'output_price_lighting': [
                    'boarding',
                    'time',
                    'waiting',
                    'transit_waiting',
                    'destination_waiting',
                ],
                'error': (
                    'Actual result Mismatches expected, check the result table'
                ),
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            1,
        ),
        (  # from_db_almost_pass_draft
            'return_as_is',
            'test_1_almost_pass',
            {},
            200,
            {
                'result': False,
                'output_price': helpers.fill_price(
                    boarding=56,
                    waiting=56,
                    transit_waiting=56,
                    destination_waiting=56,
                ),
                'output_price_lighting': ['time'],
                'error': (
                    'Actual result Mismatches expected, check the result table'
                ),
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            100,
        ),
        (  # no_db_no_expected_pass
            'has_deleted',
            'test_name_not_in_db',
            {
                'test_data': {
                    'backend_variables': {},
                    'trip_details': ZERO_TRIP_DETAILS,
                    'initial_price': helpers.make_price(70),
                    'output_price': helpers.make_price(70),
                    'output_meta': {},
                },
            },
            200,
            {
                'result': True,
                'output_price': helpers.make_price(70),
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            None,
        ),
        (  # no_db_no_expected_fail
            'has_deleted',
            'test_name_not_in_db',
            {
                'test_data': {
                    'backend_variables': INVALID_BACKEND_VARS,
                    'trip_details': ZERO_TRIP_DETAILS,
                    'initial_price': helpers.make_price(70),
                    'output_price': helpers.make_price(70),
                    'output_meta': {},
                },
            },
            200,
            {
                'error': (
                    'Incorrect test data: Invalid backend variable passed : '
                    'Field \'surge_params\' is of a wrong type. Expected: obj'
                    'ectValue, actual: intValue'
                ),
                'result': False,
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [],
            },
            None,
        ),
        (  # no_db_expected_fail
            'has_deleted',
            'test_name_not_in_db',
            {
                'test_data': {
                    'backend_variables': {},
                    'trip_details': ZERO_TRIP_DETAILS,
                    'initial_price': helpers.make_price(70),
                    'output_price': helpers.fill_price(
                        70, 70, 0, 70, 70, 70, 70,
                    ),
                    'output_meta': {},
                },
            },
            200,
            {
                'result': False,
                'output_price': helpers.make_price(70),
                'output_price_lighting': ['time'],
                'error': (
                    'Actual result Mismatches expected, check the result table'
                ),
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            None,
        ),
        (  # emit_all_ok
            'emit_meow_woof',
            'test_name_not_in_db',
            {
                'test_data': {
                    'backend_variables': BACKEND_VARS,
                    'trip_details': ZERO_TRIP_DETAILS,
                    'initial_price': helpers.make_price(70),
                    'output_price': helpers.make_price(70),
                    'output_meta': {'meow': 42, 'woof': 24},
                },
            },
            200,
            {
                'result': True,
                'output_price': helpers.make_price(70),
                'metadata_map': {'meow': 42, 'woof': 24},
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            None,
        ),
        (  # emit_miss_one
            'emit_meow_woof',
            'test_name_not_in_db',
            {
                'test_data': {
                    'backend_variables': BACKEND_VARS,
                    'trip_details': ZERO_TRIP_DETAILS,
                    'initial_price': helpers.make_price(70),
                    'output_price': helpers.make_price(70),
                    'output_meta': {
                        'meow': 42,
                        'woof': 24,
                        'how_much_is_the_fish': 11,
                    },
                },
            },
            200,
            {
                'result': False,
                'output_price': helpers.make_price(70),
                'metadata_map': {'meow': 42, 'woof': 24},
                'error': (
                    'Actual result Mismatches expected, check the result table'
                ),
                'metadata_lighting': ['how_much_is_the_fish'],
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            None,
        ),
        (  # emit_excess
            'emit_meow_woof',
            'test_name_not_in_db',
            {
                'test_data': {
                    'backend_variables': BACKEND_VARS,
                    'trip_details': ZERO_TRIP_DETAILS,
                    'initial_price': helpers.make_price(70),
                    'output_price': helpers.make_price(70),
                    'output_meta': {'meow': 42},
                },
            },
            200,
            {
                'result': False,
                'output_price': helpers.make_price(70),
                'metadata_map': {'meow': 42, 'woof': 24},
                'error': (
                    'Actual result Mismatches expected, check the result table'
                ),
                'metadata_lighting': ['woof'],
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            None,
        ),
        (  # emit_diff
            'emit_meow_woof',
            'test_name_not_in_db',
            {
                'test_data': {
                    'backend_variables': BACKEND_VARS,
                    'trip_details': ZERO_TRIP_DETAILS,
                    'initial_price': helpers.make_price(70),
                    'output_price': helpers.make_price(70),
                    'output_meta': {'how_much_is_the_fish': 11},
                },
            },
            200,
            {
                'result': False,
                'output_price': helpers.make_price(70),
                'metadata_map': {'meow': 42, 'woof': 24},
                'error': (
                    'Actual result Mismatches expected, check the result table'
                ),
                'metadata_lighting': ['how_much_is_the_fish', 'meow', 'woof'],
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            None,
        ),
        (  # no_test
            'return_as_is',
            'test_name_not_in_db',
            {},
            404,
            {'code': '404', 'message': 'Test for rule was not found'},
            None,
        ),
        (  # no_rule
            'absent_rul',
            'test_name_not_in_db',
            {},
            400,
            {'code': '404', 'message': 'Rule not found'},
            None,
        ),
        (  # name_id_mismatch
            'return_as_is',
            'test_1_can_pass',
            {'rule_id': 122},
            400,
            {'code': '400', 'message': 'rule_id and rule_name mismatch'},
            None,
        ),
        (  # no_db_currency_pass
            'has_deleted',
            'test_name_not_in_db',
            {
                'test_data': {
                    'backend_variables': {},
                    'trip_details': ZERO_TRIP_DETAILS,
                    'initial_price': helpers.make_price(70),
                    'output_price': helpers.fill_price(
                        70, 70, 70.003, 70, 69.9995, 70, 70.0005,
                    ),
                    'output_meta': {},
                },
            },
            200,
            {
                'result': True,
                'output_price': helpers.make_price(70),
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            None,
        ),
        (  # no_db_currency_fail
            'has_deleted',
            'test_name_not_in_db',
            {
                'test_data': {
                    'backend_variables': {},
                    'trip_details': ZERO_TRIP_DETAILS,
                    'initial_price': helpers.make_price(70),
                    'output_price': helpers.fill_price(
                        70, 70, 70.003, 70, 69.95, 70, 70.05,
                    ),
                    'output_meta': {},
                },
            },
            200,
            {
                'result': False,
                'output_price': helpers.make_price(70),
                'error': (
                    'Actual result Mismatches expected, check the result table'
                ),
                'output_price_lighting': [
                    'requirements',
                    'destination_waiting',
                ],
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            None,
        ),
        (  # from_db_rules_source
            'return_as_is',
            'test_1_cannot_pass',
            {'source': 'return ride.price*10;'},
            200,
            {
                'result': False,
                'output_price': helpers.make_price(280),
                'output_price_lighting': [
                    'boarding',
                    'distance',
                    'time',
                    'waiting',
                    'requirements',
                    'transit_waiting',
                    'destination_waiting',
                ],
                'error': (
                    'Actual result Mismatches expected, check the result table'
                ),
                'execution_statistic': EXECUTION_STATISTICS,
                'visited_lines': [1],
            },
            100,
        ),
    ],
    ids=[
        'from_db_pass_rule',
        'from_db_pass_draft',
        'from_db_not_pass_rule',
        'from_db_not_pass_draft',
        'from_db_almost_pass_rule',
        'from_db_almost_pass_draft',
        'no_db_no_expected_pass',
        'no_db_no_expected_fail',
        'no_db_expected_fail',
        'emit_all_ok',
        'emit_miss_one',
        'emit_excess',
        'emit_diff',
        'no_test',
        'no_rule',
        'name_id_mismatch',
        'no_db_currency_pass',
        'no_db_currency_fail',
        'from_db_rules_source',
    ],
)
async def test_v1_testing_test_post(
        taxi_pricing_admin,
        pgsql,
        body,
        code,
        result,
        rule_name,
        test_name,
        result_id,
        mockserver,
):
    @mockserver.json_handler('taxi-approvals/v2/drafts/')
    def _mock_approvals_drafts_get(request):
        data = request.args
        assert 'id' in data
        return {
            'id': int(data['id']),
            'version': 1,
            'status': 'succeeded',
            'data': {},  # empty because unused
        }

    @mockserver.json_handler('pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'ok', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    response = await taxi_pricing_admin.post(
        'v1/testing/test',
        params={'rule_name': rule_name, 'test_name': test_name},
        json=body,
    )

    assert response.status_code == code

    if response.status_code == 200:
        if result_id is not None:
            db_test = fetch_test(pgsql, test_name, rule_name)
            assert db_test['last_result'] == result['result']
            assert db_test['last_result_rule_id'] == result_id
        else:
            assert fetch_test(pgsql, test_name, rule_name) is None

        data = response.json()
        assert result == data


@pytest.mark.parametrize(
    'body,status_code,test,message',
    [
        (  # no_rule_id
            {'rule_name': 'return_as_is', 'test_name': 'test_1_can_pass'},
            200,
            {
                'backend_variables': {},
                'initial_price': {
                    'boarding': 0.0,
                    'destination_waiting': 0.0,
                    'distance': 0.0,
                    'requirements': 0.0,
                    'time': 0.0,
                    'transit_waiting': 0.0,
                    'waiting': 0.0,
                },
                'trip_details': {
                    'total_distance': 0.0,
                    'total_time': 2,
                    'waiting_in_destination_time': 0,
                    'waiting_in_transit_time': 0,
                    'waiting_time': 0,
                    'user_options': {},
                    'user_meta': {},
                },
                'output_price': {
                    'boarding': 0.0,
                    'destination_waiting': 0.0,
                    'distance': 0.0,
                    'requirements': 0.0,
                    'time': 0.0,
                    'transit_waiting': 0.0,
                    'waiting': 0.0,
                },
                'output_meta': {},
                'last_result': False,
                'price_calc_version': '13',
            },
            None,
        ),
        (  # matched_rule_id
            {
                'rule_name': 'return_as_is',
                'test_name': 'test_1_can_pass',
                'rule_id': 1815,
            },
            200,
            {
                'backend_variables': {},
                'initial_price': {
                    'boarding': 0.0,
                    'destination_waiting': 0.0,
                    'distance': 0.0,
                    'requirements': 0.0,
                    'time': 0.0,
                    'transit_waiting': 0.0,
                    'waiting': 0.0,
                },
                'trip_details': {
                    'total_distance': 0.0,
                    'total_time': 2,
                    'waiting_in_destination_time': 0,
                    'waiting_in_transit_time': 0,
                    'waiting_time': 0,
                    'user_options': {},
                    'user_meta': {},
                },
                'output_price': {
                    'boarding': 0.0,
                    'destination_waiting': 0.0,
                    'distance': 0.0,
                    'requirements': 0.0,
                    'time': 0.0,
                    'transit_waiting': 0.0,
                    'waiting': 0.0,
                },
                'last_result': False,
                'output_meta': {},
                'price_calc_version': '13',
            },
            None,
        ),
        (  # mismatched_rule_id
            {
                'rule_name': 'return_as_is',
                'test_name': 'test_1_can_pass',
                'rule_id': 1,
            },
            200,
            {
                'backend_variables': {},
                'initial_price': {
                    'boarding': 0.0,
                    'destination_waiting': 0.0,
                    'distance': 0.0,
                    'requirements': 0.0,
                    'time': 0.0,
                    'transit_waiting': 0.0,
                    'waiting': 0.0,
                },
                'trip_details': {
                    'total_distance': 0.0,
                    'total_time': 2,
                    'waiting_in_destination_time': 0,
                    'waiting_in_transit_time': 0,
                    'waiting_time': 0,
                    'user_options': {},
                    'user_meta': {},
                },
                'output_price': {
                    'boarding': 0.0,
                    'destination_waiting': 0.0,
                    'distance': 0.0,
                    'requirements': 0.0,
                    'time': 0.0,
                    'transit_waiting': 0.0,
                    'waiting': 0.0,
                },
                'output_meta': {},
                'price_calc_version': '13',
            },
            None,
        ),
        (  # have_id_no_result
            {
                'rule_name': 'return_as_is',
                'test_name': 'test_with_no_result',
                'rule_id': 1,
            },
            200,
            {
                'backend_variables': {},
                'initial_price': {
                    'boarding': 0.0,
                    'destination_waiting': 0.0,
                    'distance': 0.0,
                    'requirements': 0.0,
                    'time': 0.0,
                    'transit_waiting': 0.0,
                    'waiting': 0.0,
                },
                'trip_details': {
                    'total_distance': 0.0,
                    'total_time': 2,
                    'waiting_in_destination_time': 0,
                    'waiting_in_transit_time': 0,
                    'waiting_time': 0,
                    'user_options': {},
                    'user_meta': {},
                },
                'output_price': {
                    'boarding': 0.0,
                    'destination_waiting': 0.0,
                    'distance': 0.0,
                    'requirements': 0.0,
                    'time': 0.0,
                    'transit_waiting': 0.0,
                    'waiting': 0.0,
                },
                'output_meta': {},
            },
            None,
        ),
        (  # bad_test_bad_rule
            {'rule_name': 'kitty', 'test_name': 'doggy'},
            404,
            {},
            'Test not found.',
        ),
        (  # good_test_bad_rule
            {'rule_name': 'existent_test', 'test_name': 'doggy'},
            404,
            {},
            'Test not found.',
        ),
    ],
    ids=[
        'no_rule_id',
        'matched_rule_id',
        'mismatched_rule_id',
        'have_id_no_result',
        'bad_test_bad_rule',
        'good_test_bad_rule',
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['tests.sql'])
async def test_v1_testing_test_get(
        taxi_pricing_admin, body, status_code, test, message,
):
    if 'rule_id' in body:
        response = await taxi_pricing_admin.get(
            'v1/testing/test',
            params={
                'rule_name': body['rule_name'],
                'test_name': body['test_name'],
                'rule_id': body['rule_id'],
            },
            json=body,
        )
    else:
        response = await taxi_pricing_admin.get(
            'v1/testing/test',
            params={
                'rule_name': body['rule_name'],
                'test_name': body['test_name'],
            },
            json=body,
        )

    assert response.status_code == status_code

    resp = response.json()
    if status_code == 200:
        assert resp == test
    else:
        assert resp['message'] == message


@pytest.mark.pgsql('pricing_data_preparer', files=['tests.sql'])
@pytest.mark.parametrize(
    'rule_name, test_name, status_code, message',
    [
        ('return_as_is', 'test_1_can_pass', 200, None),
        ('mew', 'woof', 404, 'Test not found.'),
    ],
)
async def test_v1_testing_test_delete(
        taxi_pricing_admin, pgsql, rule_name, test_name, status_code, message,
):

    response = await taxi_pricing_admin.delete(
        'v1/testing/test',
        params={'rule_name': rule_name, 'test_name': test_name},
    )

    assert response.status_code == status_code

    test = does_test_exist(pgsql, rule_name, test_name)
    assert not test

    if response.status_code == 404:
        resp = response.json()
        assert resp['message'] == message
