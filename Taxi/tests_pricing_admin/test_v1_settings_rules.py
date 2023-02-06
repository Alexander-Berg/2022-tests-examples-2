# flake8: noqa F501
# pylint: disable=too-many-lines

import copy
import json

import pytest

YANDEX_LOGIN_HEADER = 'X-Yandex-Login'


def does_id_exist(pgsql, rule_id):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'SELECT rule_id '
            'FROM price_modifications.rules '
            'WHERE rule_id = %s',
            (rule_id,),
        )
        return cursor.fetchone() is not None


def get_pmv_task_id_from_pgsql(pgsql, rule_id):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'SELECT pmv_task_id '
            'FROM ONLY price_modifications.rules_drafts '
            'WHERE rule_id = %s',
            (rule_id,),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def select_named(query, pgsql):
    cursor = pgsql['pricing_data_preparer'].conn.cursor()
    cursor.execute(query)
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


async def test_v1_settings_rules_get_empty(
        taxi_pricing_admin, taxi_config, mockserver,
):
    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=True)

    @mockserver.json_handler('taxi-approvals/drafts/list/')
    def _mock_approvals_drafts_list(request):
        data = json.loads(request.get_data())
        assert 'drafts_ids' in data
        assert 'limit' in data
        result = []
        for draft_id in data['drafts_ids']:
            result.append(
                {'id': draft_id, 'status': 'need_approval', 'data': {}},
            )
        return result

    response = await taxi_pricing_admin.get('v1/settings/rules')
    assert response.status_code == 200
    resp = response.json()
    assert 'rules' in resp and not resp['rules']


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize('status', [None, 'approved', 'drafts'])
async def test_v1_settings_rules_get(
        taxi_pricing_admin, status, mockserver, taxi_config,
):
    params = {}
    if status:
        params['status'] = status

    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=True)

    @mockserver.json_handler('taxi-approvals/drafts/list/')
    def _mock_approvals_drafts_list(request):
        data = json.loads(request.get_data())
        assert 'drafts_ids' in data
        assert 'limit' in data
        result = []
        for draft_id in data['drafts_ids']:
            result.append({'id': draft_id, 'status': 'applying', 'data': {}})
        return result

    @mockserver.json_handler('/pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        task_id = int(data['id'])
        if task_id == 1:
            return {'done': 'in_progress'}
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'error', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    response = await taxi_pricing_admin.get('v1/settings/rules', params=params)
    assert response.status_code == 200
    resp = response.json()
    assert 'rules' in resp
    rules = resp['rules']

    if not status:
        assert len(rules) == 11
    elif status == 'approved':
        assert len(rules) == 5
    elif status == 'drafts':
        assert len(rules) == 6

    for rule in resp['rules']:
        assert 'author' in rule
        assert 'id' in rule

        if rule['name'] == 'two':
            assert not rule['has_passed_tests']
        elif rule['name'] == 'three':
            assert rule['has_passed_tests']
        elif rule['name'] == 'four':
            assert not rule['has_passed_tests']
        elif rule['name'] == 'five':
            assert not rule['has_passed_tests']
        else:
            assert 'has_passed_tests' not in rule

        if status == 'drafts':
            assert 'status' in rule
            assert 'pmv_task_id' in rule
            if rule['status'] == 'failure':
                assert 'error_message' in rule
            elif rule['status'] == 'to_approve':
                assert 'approvals_id' in rule
        elif status == 'approved':
            assert 'approvals_id' in rule
            assert 'status' in rule and rule['status'] == 'success'
            assert 'error_message' not in rule


@pytest.mark.pgsql('pricing_data_preparer', files=['rules_status.sql'])
async def test_v1_settings_rules_get_status(
        taxi_pricing_admin, taxi_config, mockserver,
):
    @mockserver.json_handler('taxi-approvals/v2/drafts/')
    def _mock_approvals_drafts_get(request):
        data = request.args
        assert 'id' in data
        if int(data['id']) == 555:
            return {
                'id': int(data['id']),
                'version': 1,
                'status': 'expired',
                'data': {},
            }
        if int(data['id']) == 666:
            return {
                'id': int(data['id']),
                'version': 1,
                'status': 'succeeded',
                'data': {},
            }
        if int(data['id']) == 777:
            return {
                'id': int(data['id']),
                'version': 1,
                'status': 'applying',
                'data': {},
            }
        return {}

    @mockserver.json_handler('taxi-approvals/drafts/list/')
    def _mock_approvals_drafts_list(request):
        data = json.loads(request.get_data())
        assert 'drafts_ids' in data
        assert 'limit' in data
        result = []
        for draft_id in data['drafts_ids']:
            if draft_id == 555:
                result.append(
                    {
                        'id': draft_id,
                        'status': 'expired',
                        'data': {},
                        'version': 1,
                    },
                )
            if draft_id == 666:
                result.append(
                    {
                        'id': draft_id,
                        'status': 'succeeded',
                        'data': {},
                        'version': 1,
                    },
                )
            if draft_id == 777:
                result.append(
                    {
                        'id': draft_id,
                        'status': 'applying',
                        'data': {},
                        'version': 1,
                    },
                )
        return result

    @mockserver.json_handler('/pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        if int(data['id']) == 22:
            return {'done': 'in_progress'}
        if int(data['id']) == 33:
            return {
                'done': 'finished',
                'results': [
                    {'test_result': 'error', 'test_name': 'nan_test'},
                    {'test_result': 'ok', 'test_name': 'map_test'},
                ],
            }
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'ok', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=True)

    params = {}
    params['status'] = 'drafts'
    response = await taxi_pricing_admin.get('v1/settings/rules', params=params)
    assert response.status_code == 200
    resp = response.json()
    assert 'rules' in resp
    rules = resp['rules']
    for rule in rules:
        if rule['name'] == 'without_pmv':
            assert rule['status'] == 'not_started'
        if rule['name'] == 'running_pmv':
            assert rule['status'] == 'running'
        if rule['name'] == 'failed_pmv':
            assert rule['status'] == 'failure'
        if rule['name'] == 'without_approvals_id':
            assert rule['status'] == 'draft_create_error'
        if rule['name'] == 'expired':
            assert rule['status'] == 'canceled'
        if rule['name'] == 'succeeded':
            assert rule['status'] == 'success'
        if rule['name'] == 'applying':
            assert rule['status'] == 'draft_create_error'
        if rule['name'] == 'without_approvals_and_with_errors':
            assert rule['status'] == 'failure'

    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=False)

    params = {}
    params['status'] = 'drafts'
    response = await taxi_pricing_admin.get('v1/settings/rules', params=params)
    assert response.status_code == 200
    resp = response.json()
    assert 'rules' in resp
    rules = resp['rules']
    for rule in rules:
        if rule['name'] == 'without_pmv':
            assert rule['status'] == 'not_started'
        if rule['name'] == 'running_pmv':
            assert rule['status'] == 'running'
        if rule['name'] == 'failed_pmv':
            assert rule['status'] == 'failure'
        if rule['name'] == 'without_approvals_id':
            assert rule['status'] == 'draft_create_error'
        if rule['name'] == 'expired':
            assert rule['status'] == 'canceled'
        if rule['name'] == 'succeeded':
            assert rule['status'] == 'success'
        if rule['name'] == 'applying':
            assert rule['status'] == 'draft_create_error'
        if rule['name'] == 'without_approvals_and_with_errors':
            assert rule['status'] == 'failure'


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize(
    'status, limit, offset, ret_code, ret_size',
    [
        (None, 2, 1, 200, 2),
        ('approved', 3, 2, 200, 3),
        ('drafts', 1, 6, 200, 0),
        (None, 4, 1, 200, 4),
        (None, 4, 9, 200, 2),
        (None, 101, None, 400, 0),
        (None, None, -1, 400, 0),
    ],
)
async def test_v1_settings_rules_get_limit_offset(
        taxi_pricing_admin,
        status,
        limit,
        offset,
        ret_code,
        ret_size,
        mockserver,
        taxi_config,
):
    params = {}
    if status:
        params['status'] = status
    if limit:
        params['limit'] = limit
    if offset:
        params['offset'] = offset

    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=True)

    @mockserver.json_handler('pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        task_id = int(data['id'])
        if task_id == 1:
            return {'done': 'in_progress'}
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'error', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    @mockserver.json_handler('taxi-approvals/drafts/list/')
    def _mock_approvals_drafts_list(request):
        data = json.loads(request.get_data())
        assert 'drafts_ids' in data
        assert 'limit' in data
        result = []
        for draft_id in data['drafts_ids']:
            result.append(
                {'id': draft_id, 'status': 'need_approval', 'data': {}},
            )
        return result

    response = await taxi_pricing_admin.get('v1/settings/rules', params=params)

    assert response.status_code == ret_code
    if ret_code == 200:
        resp = response.json()
        assert 'rules' in resp
        rules = resp['rules']
        assert len(rules) == ret_size
        for rule in resp['rules']:
            if rule['name'] == 'two':
                assert not rule['has_passed_tests']
            elif rule['name'] == 'three':
                assert rule['has_passed_tests']
            elif rule['name'] == 'four':
                assert not rule['has_passed_tests']
            elif rule['name'] == 'five':
                assert not rule['has_passed_tests']
            else:
                assert 'has_passed_tests' not in rule


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize(
    'name, policy, author, status, after, before, source_code, expected_size, startrek_ticket',
    [
        (None, None, None, None, None, None, None, 11, None),
        (
            None,
            None,
            None,
            None,
            None,
            None,
            'return (1 / *ride.price)',
            1,
            None,
        ),
        (None, None, None, None, None, None, '*ride.price', 11, None),
        ('one', None, None, None, None, None, None, 2, None),
        (
            'one',
            None,
            None,
            None,
            None,
            None,
            'return (1 / *ride.price)',
            1,
            None,
        ),
        ('one', None, None, None, None, None, '*ride.price', 2, None),
        ('three', None, None, None, None, None, None, 2, None),
        (None, 'both_side', None, None, None, None, None, 2, None),
        (None, 'backend_only', None, None, None, None, None, 7, None),
        (None, 'taximeter_only', None, None, None, None, None, 2, None),
        (None, 'both_side', '200ok', None, None, None, None, 2, None),
        (None, 'backend_only', None, 'failure', None, None, None, 3, None),
        (
            None,
            'backend_only',
            None,
            'failure',
            None,
            None,
            '4.4 / *ride.price',
            1,
            None,
        ),
        (
            None,
            'backend_only',
            None,
            'failure',
            None,
            None,
            '*ride.price',
            3,
            None,
        ),
        (None, 'taximeter_only', None, 'failure', None, None, None, 1, None),
        (
            'two_draft',
            'backend_only',
            '200ok draft',
            'failure',
            None,
            None,
            None,
            1,
            None,
        ),
        (
            'two_draft',
            'both_side',
            '200ok draft',
            'failure',
            None,
            None,
            None,
            0,
            None,
        ),
        (
            'two_draft',
            'taximeter_only',
            '200ok draft',
            'failure',
            None,
            None,
            None,
            0,
            None,
        ),
        (
            'five_draft',
            'taximeter_only',
            '200ok draft',
            'failure',
            None,
            None,
            None,
            1,
            None,
        ),
        (
            None,
            'backend_only',
            '200ok',
            None,
            None,
            '2014-07-05T06:00:00+00:00',
            None,
            6,
            None,
        ),
        (
            None,
            'backend_only',
            '200ok',
            None,
            '2010-04-05T06:00:00+00:00',
            '2014-07-05T06:00:00+00:00',
            None,
            5,
            None,
        ),
        (None, None, None, None, None, None, None, 1, 'EFFICIENCYDEV-17020'),
        (None, None, None, None, None, None, None, 2, 'EFFICIENCYDEV-17020-1'),
    ],
)
async def test_v1_settings_rules_get_with_filters(
        taxi_pricing_admin,
        taxi_config,
        name,
        policy,
        author,
        status,
        after,
        before,
        source_code,
        expected_size,
        startrek_ticket,
        mockserver,
):
    params = {}
    if status:
        params['draft_status'] = status
    if name:
        params['name'] = name
    if policy:
        params['policy'] = policy
    if author:
        params['author'] = author
    if after:
        params['from'] = after
    if before:
        params['to'] = before
    if source_code:
        params['source_code'] = source_code
    if startrek_ticket:
        params['startrek_ticket'] = startrek_ticket

    @mockserver.json_handler('taxi-approvals/drafts/list/')
    def _mock_approvals_drafts_list(request):
        data = json.loads(request.get_data())
        assert 'drafts_ids' in data
        assert 'limit' in data
        result = []
        for draft_id in data['drafts_ids']:
            result.append(
                {'id': draft_id, 'status': 'need_approval', 'data': {}},
            )
        return result

    @mockserver.json_handler('/pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        task_id = int(data['id'])
        if task_id == 1:
            return {'done': 'in_progress'}
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'error', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=True)

    response = await taxi_pricing_admin.get('v1/settings/rules', params=params)

    assert response.status_code == 200

    resp = response.json()
    assert 'rules' in resp
    rules = resp['rules']
    assert len(rules) == expected_size
    for rule in resp['rules']:
        if rule['name'] == 'two':
            assert not rule['has_passed_tests']
        elif rule['name'] == 'three':
            assert rule['has_passed_tests']
        elif rule['name'] == 'four':
            assert not rule['has_passed_tests']
        elif rule['name'] == 'five':
            assert not rule['has_passed_tests']
        else:
            assert 'has_passed_tests' not in rule


@pytest.mark.config(PRICING_DATA_PREPARER_REQUIRED_METADATA=['ex3'])
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.parametrize('pmv_enabled', [False, True])
async def test_v1_settings_rules_write(
        taxi_pricing_admin,
        mockserver,
        taxi_config,
        pgsql,
        load_json,
        mocked_time,
        pmv_enabled,
):
    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=pmv_enabled)

    approvals_id = 100500

    @mockserver.json_handler('pricing-modifications-validator/v1/add_task')
    def _mock_pmv_v1_add_task(request):
        assert pmv_enabled
        data = json.loads(request.get_data())
        assert 'constraints' in data
        assert 'script' in data
        return {'id': 1}

    def _do_mock_approvals(request):
        assert request.headers.get(YANDEX_LOGIN_HEADER) == '200ok'
        assert not pmv_enabled
        data = json.loads(request.get_data())
        assert (
            'service_name' in data and data['service_name'] == 'pricing-admin'
        )
        assert (
            'api_path' in data
            and data['api_path'] == 'price_modifications_rules_create'
        )
        assert 'data' in data and data['data']
        return {
            'id': approvals_id,
            'version': 1,
            'status': 'need_approval',
            'data': data['data'],
        }

    # mock functions with same behavior
    @mockserver.json_handler('taxi-approvals/drafts/create/')
    def _mock_approvals_create_draft(request):
        return _do_mock_approvals(request)

    @mockserver.json_handler(f'taxi-approvals/drafts/{approvals_id}/edit/')
    def _mock_approvals_drafts_id_edit(request):
        return _do_mock_approvals(request)

    @mockserver.json_handler('taxi-approvals/v2/drafts/')
    def _mock_approvals_drafts_get(request):
        data = request.args
        assert 'id' in data
        return {
            'id': approvals_id,
            'version': 1,
            'status': 'need_approval',
            'data': {},  # empty because unused
        }

    @mockserver.json_handler('pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        task_id = int(data['id'])
        if task_id == 1:
            return {'done': 'in_progress'}
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'error', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    @mockserver.json_handler('taxi-approvals/drafts/list/')
    def _mock_approvals_drafts_list(request):
        data = json.loads(request.get_data())
        assert 'drafts_ids' in data
        assert 'limit' in data
        result = []
        for draft_id in data['drafts_ids']:
            result.append(
                {
                    'id': draft_id,
                    'status': 'applying',
                    'data': {},
                    'version': 1,
                },
            )
        return result

    # declare
    rule_one = load_json('rule_one.json')
    rule_two = load_json('rule_two.json')
    rule_three = load_json('rule_three.json')
    rule_four_no_extra = load_json('rule_four_no_extra.json')
    code_to_ast = load_json('code_to_ast.json')

    headers = {YANDEX_LOGIN_HEADER: '200ok'}

    response = await taxi_pricing_admin.get(
        'v1/settings/rules', params={'from': '2019-12-05T06:00:00+00:00'},
    )
    resp = response.json()
    assert 'rules' in resp
    assert not resp['rules']

    def get_ast_list():
        with pgsql['pricing_data_preparer'].cursor() as cursor:
            cursor.execute(
                'SELECT source_code, ast FROM price_modifications.rules',
            )
            return cursor.fetchall()

    def check_startreck_ticket(response_json, rule_name):
        rule = [x for x in response_json['rules'] if x['name'] == rule_name]
        assert 'startrek_ticket' in rule[0]
        assert rule[0]['startrek_ticket'] == 'EFFICIENCYDEV-16339'

    # write new
    response = await taxi_pricing_admin.put(
        'v1/settings/rules', headers=headers, json=rule_two,
    )
    assert _mock_pmv_v1_add_task.has_calls == pmv_enabled
    # FIXME: this check is temporarily disabled
    # if not pmv_enabled:
    #    mocked_time.sleep(1)
    #    await taxi_pricing_admin.invalidate_caches(clean_update=False)
    #    await _mock_approvals_create_draft.wait_call()

    assert response.status_code == 200
    resp = response.json()
    assert 'id' in resp
    rule_id = resp['id']
    pmv_task_id = get_pmv_task_id_from_pgsql(pgsql, rule_id)
    if pmv_enabled:
        assert pmv_task_id == 1
    else:
        assert pmv_task_id is None
    assert code_to_ast[rule_two['source_code']] in list(
        row[1] for row in get_ast_list()
    )

    response = await taxi_pricing_admin.get(
        'v1/settings/rules', params={'from': '2019-12-05T06:00:00+00:00'},
    )

    check_startreck_ticket(response.json(), 'two')

    assert len(response.json()['rules']) == 1
    # failure extra return
    response = await taxi_pricing_admin.put(
        'v1/settings/rules', headers=headers, json=rule_three,
    )
    assert response.status_code == 422
    resp = response.json()
    assert 'code' in resp
    assert resp['code'] == 'meta_conflict'

    # failure missing extra return
    response = await taxi_pricing_admin.put(
        'v1/settings/rules', headers=headers, json=rule_four_no_extra,
    )
    assert response.status_code == 422
    resp = response.json()
    assert 'code' in resp
    assert resp['code'] == 'meta_conflict'

    # rewrite existing
    response = await taxi_pricing_admin.put(
        'v1/settings/rules', headers=headers, json=rule_one,
    )
    assert response.status_code == 200
    assert code_to_ast[rule_one['source_code']] in list(
        row[1] for row in get_ast_list()
    )

    # rewrite
    response = await taxi_pricing_admin.put(
        'v1/settings/rules', headers=headers, json=rule_one,
    )
    assert response.status_code == 422 if pmv_enabled else 200
    assert _mock_pmv_v1_add_task.has_calls == pmv_enabled
    # FIXME: this check is temporarily disabled
    #    if not pmv_enabled:
    #        mocked_time.sleep(1)
    #        await taxi_pricing_admin.invalidate_caches(clean_update=False)
    #        await _mock_approvals_drafts_id_edit.wait_call()
    #        assert _mock_approvals_drafts_get.has_calls

    response = await taxi_pricing_admin.get(
        'v1/settings/rules', params={'status': 'drafts'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'rules' in resp
    rules_names = list(x['name'] for x in resp['rules'])
    assert rule_one['name'] in rules_names
    assert rule_two['name'] in rules_names
    check_startreck_ticket(response.json(), 'one')

    # check all serialized asts in db
    for in_db in get_ast_list():
        assert code_to_ast[in_db[0]] == in_db[1]


@pytest.mark.pgsql(
    'pricing_data_preparer',
    files=['rules.sql'],
    queries=[
        """UPDATE price_modifications.rules_drafts
             SET status = 'running', errors = NULL
             WHERE name = '{}'""".format(
            'one',
        ),
    ],
)
@pytest.mark.parametrize(
    'name, status, error_message, author',
    [
        ('a_draft', 'failure', 'some error', '200ok draft'),
        ('one', 'success', None, '200ok draft'),
    ],
)
async def test_v1_settings_rules_apply_verifications(
        taxi_pricing_admin,
        taxi_config,
        mockserver,
        name,
        status,
        error_message,
        author,
        mock_pmv,
        pmv_context,
):
    # declare
    @mockserver.json_handler('taxi-approvals/v2/drafts/')
    def _mock_approvals_drafts_get(request):
        data = request.args
        assert 'id' in data
        return {
            'id': int(data['id']),
            'version': 1,
            'status': 'need_approval',
            'data': {},  # empty because unused
        }

    @mockserver.json_handler('taxi-approvals/drafts/list/')
    def _mock_approvals_drafts_list(request):
        data = json.loads(request.get_data())
        assert 'drafts_ids' in data or 'change_doc_ids' in data
        result = []
        if 'drafts_ids' in data:
            for draft_id in data['drafts_ids']:
                result.append(
                    {
                        'id': draft_id,
                        'status': 'need_approval',
                        'data': {},
                        'version': 1,
                    },
                )
        return result

    pmv_context.set_running()
    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=True)
    response = await taxi_pricing_admin.get(
        'v1/settings/rules', params={'status': 'drafts'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'rules' in resp

    rule = next((x for x in resp['rules'] if x['name'] == name), None)
    rule['status'] = status
    del rule['author']
    if error_message:
        rule['error_message'] = error_message
    elif 'error_message' in rule:
        del rule['error_message']

    @mockserver.json_handler('taxi-approvals/drafts/create/')
    def mock_approvals_drafts_create(request):
        # assertations
        assert YANDEX_LOGIN_HEADER in request.headers
        data = json.loads(request.get_data())
        assert 'mode' in data and data['mode'] == 'push'
        assert 'run_manually' in data and data['run_manually'] is False
        assert 'service_name' in data
        assert data['service_name'] == 'pricing-admin'
        assert 'api_path' in data
        assert data['api_path'] == 'price_modifications_rules_create'
        assert 'request_id' in data
        assert 'data' in data
        actual = data['data']
        expected = copy.deepcopy(rule)
        del expected['status']
        del expected['updated']
        del expected['id']
        del expected['pmv_task_id']
        del expected['evaluate_on_prestable']
        assert actual == expected

        # response
        data['id'] = mock_approvals_drafts_create.times_called
        data['status'] = 'need_approval'
        data['version'] = 1
        return data

    if status == 'failure':
        # apply as failure
        response = await taxi_pricing_admin.post(
            'v1/service/verifications/rule/apply', json=rule,
        )
        assert response.status_code == 200

        pmv_context.set_fail()

        # try duplicate apply
        response = await taxi_pricing_admin.post(
            'v1/service/verifications/rule/apply', json=rule,
        )
        assert response.status_code == 422
        resp = response.json()
        assert 'code' in resp and resp['code'] == 'bad_applying'
    elif status == 'success':
        # apply as success
        response = await taxi_pricing_admin.post(
            'v1/service/verifications/rule/apply', json=rule,
        )
        assert response.status_code == 200
        assert mock_approvals_drafts_create.has_calls
        assert mock_approvals_drafts_create.times_called == 1
        pmv_context.set_ok()

    response = await taxi_pricing_admin.get(
        'v1/settings/rules', params={'status': 'drafts'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'rules' in resp

    for each in resp['rules']:
        assert 'author' in each and each['author'] == author
        assert each['status'] != 'to_approve' or 'approvals_id' in each
        if each['name'] == rule['name']:
            if status == 'success':
                assert each['status'] == 'to_approve'
            else:
                assert each['status'] == 'failure'
            if error_message:
                assert each['error_message'] == rule['error_message']


class PmvContext:
    def __init__(self):
        self.response = {}

    def set_fail(self):
        self.response = {
            'done': 'finished',
            'results': [
                {'test_result': 'error', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    def set_ok(self):
        self.response = {
            'done': 'finished',
            'results': [
                {'test_result': 'ok', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    def set_running(self):
        self.response = {'done': 'in_progress'}


@pytest.fixture(name='pmv_context')
def fixture_pmv_context():
    return PmvContext()


@pytest.fixture(name='mock_pmv')
def fixture_mock_pmv(mockserver, pmv_context):
    @mockserver.json_handler('pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        return pmv_context.response

    return _mock_pmv_v1_task_tesult


class ApprovalsContext:
    def __init__(self):
        self.response = {}

    def set_need_approval(self, rule_id):
        self.response = {
            'id': int(rule_id),
            'version': 1,
            'status': 'need_approval',
            'data': {},  # empty because unused
        }

    def set_succeeded(self, rule_id):
        self.response = {
            'id': int(rule_id),
            'version': 1,
            'status': 'succeeded',
            'data': {},  # empty because unused
        }


@pytest.fixture(name='approvals_context')
def fixture_approvals_context():
    return ApprovalsContext()


@pytest.fixture(name='mock_approvals')
def fixture_mock_approvals(mockserver, approvals_context):
    @mockserver.json_handler('taxi-approvals/v2/drafts/')
    def _mock_approvals_drafts_get(request):
        data = request.args
        assert 'id' in data
        return approvals_context.response

    return _mock_approvals_drafts_get


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize(
    'name, author', [('one', '200ok draft'), ('a_draft', '200ok draft')],
)
async def test_v1_settings_rules_apply_approvals(
        taxi_pricing_admin,
        taxi_config,
        mockserver,
        name,
        author,
        load_json,
        mock_pmv,
        pmv_context,
        mock_approvals,
        approvals_context,
):
    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=True)

    @mockserver.json_handler('taxi-approvals/drafts/list/')
    def _mock_approvals_drafts_list(request):
        data = json.loads(request.get_data())
        assert 'drafts_ids' in data or 'change_doc_ids' in data
        result = []
        if 'drafts_ids' in data:
            for draft_id in data['drafts_ids']:
                assert draft_id in data['drafts_ids']
                approvals_response = approvals_context.response
                approvals_response['id'] = draft_id
                result.append(approvals_response)
        return result

    @mockserver.json_handler(f'/approvals/drafts/1/edit/')
    def _mock_approvals_drafts_id_edit(request):
        data = json.loads(request.get_data())
        assert 'change_doc_id' in data
        return {
            'id': int(data['change_doc_id']),
            'version': 1,
            'status': 'succeeded',
            'data': {},  # empty because unused
        }

    @mockserver.json_handler('pricing-modifications-validator/v1/add_task')
    def _mock_pmv_v1_add_task(request):
        data = json.loads(request.get_data())
        assert 'constraints' in data
        assert 'script' in data
        return {'id': 1}

    pmv_context.set_running()
    if name == 'one':
        approvals_context.set_succeeded(1007)
    elif name == 'a_draft':
        approvals_context.set_succeeded(1006)

    response = await taxi_pricing_admin.get(
        'v1/settings/rules', params={'status': 'drafts'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'rules' in resp

    rule = next((x for x in resp['rules'] if x['name'] == name), None)
    assert rule
    del rule['author']
    for member in ('error_message', 'status'):
        if member in rule:
            del rule[member]

    @mockserver.json_handler('taxi-approvals/drafts/create/')
    def mock_approvals_drafts_create(request):
        data = json.loads(request.get_data())
        data['id'] = mock_approvals_drafts_create.times_called
        data['status'] = 'need_approval'
        data['version'] = 1
        return data

    # apply as failure
    pmv_context.set_fail()

    response = await taxi_pricing_admin.post(
        'v1/service/approvals/rule/apply', json=rule,
    )
    assert response.status_code == 422
    resp = response.json()
    assert 'code' in resp and resp['code'] == 'bad_applying'

    if rule['name'] == 'one':
        # rewrite
        response = await taxi_pricing_admin.put(
            'v1/settings/rules',
            headers={YANDEX_LOGIN_HEADER: '200ok'},
            json=rule,
        )
        assert response.status_code == 200

    # set verification
    pmv_context.set_running()

    rule_success = copy.deepcopy(rule)
    rule_success['status'] = 'success'
    approvals_context.set_succeeded(rule_success['id'])
    response = await taxi_pricing_admin.post(
        'v1/service/verifications/rule/apply', json=rule_success,
    )
    assert response.status_code == 200
    assert mock_approvals_drafts_create.has_calls
    assert mock_approvals_drafts_create.times_called == 1

    pmv_context.set_ok()

    if name == 'one':
        approvals_context.set_succeeded(1007)
    elif name == 'a_draft':
        approvals_context.set_succeeded(1006)

    # apply as success
    response = await taxi_pricing_admin.post(
        'v1/service/approvals/rule/apply', json=rule,
    )
    assert response.status_code == 200

    response = await taxi_pricing_admin.get(
        'v1/settings/rules', params={'status': 'drafts'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'rules' in resp
    rules_names = list(x['name'] for x in resp['rules'])
    assert rule['name'] not in rules_names

    response = await taxi_pricing_admin.get(
        'v1/settings/rules', params={'status': 'approved'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'rules' in resp and resp['rules']

    rules_names = list(x['name'] for x in resp['rules'])
    assert rule['name'] in rules_names
    authors = load_json('authors_names.json')
    for each in resp['rules']:
        assert 'author' in each and each['author'] == authors[each['name']]
        assert 'approvals_id' in each
        assert 'status' in each and each['status'] == 'success'
        if each['name'] == rule['name']:
            if 'description' in rule:
                assert each['description'] == rule['description']
            assert each['source_code'] == rule['source_code']
            assert each['policy'] == rule['policy']


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize(
    'rule_id, status_code, error_code',
    [(1007, 422, 'forbidden_status'), (1006, 200, None)],
)
async def test_v1_settings_cancel_verifications_by_id(
        taxi_pricing_admin,
        taxi_config,
        rule_id,
        status_code,
        error_code,
        mockserver,
):
    @mockserver.json_handler('pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        task_id = int(data['id'])
        if task_id in (2, 1007):
            return {
                'done': 'finished',
                'results': [
                    {'test_result': 'error', 'test_name': 'nan_test'},
                    {'test_result': 'error', 'test_name': 'map_test'},
                ],
            }
        return {'done': 'in_progress'}

    @mockserver.json_handler('pricing-modifications-validator/v1/cancel_task')
    def _mock_pmv_v1_cancel_task(request):
        return {}

    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=True)

    # cancel long-time
    response = await taxi_pricing_admin.post(
        'v1/settings/rule/cancel',
        headers={YANDEX_LOGIN_HEADER: '200ok draft'},
        params={'id': rule_id},
        json={'comment': 'very important info'},
    )
    assert response.status_code == status_code
    if error_code:
        resp = response.json()
        assert 'code' in resp and resp['code'] == error_code


@pytest.mark.pgsql(
    'pricing_data_preparer',
    files=['rules.sql'],
    queries=[
        """UPDATE price_modifications.rules_drafts
             SET status = 'to_approve', errors = NULL, approvals_id = rule_id
             WHERE rule_id = {}""".format(
            1006,
        ),
    ],
)
@pytest.mark.parametrize(
    'rule_id, status_code, error_code',
    [(1007, 422, 'forbidden_status'), (1006, 200, None)],
)
async def test_v1_settings_cancel_approvals_by_id(
        taxi_pricing_admin, mockserver, rule_id, status_code, error_code,
):
    @mockserver.json_handler('taxi-approvals/v2/drafts/')
    def _mock_approvals_drafts_get(request):
        data = request.args
        assert 'id' in data
        return {
            'id': int(data['id']),
            'version': 1,
            'status': 'need_approval',
            'data': {},  # empty because unused
        }

    @mockserver.json_handler('pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'ok', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    @mockserver.json_handler(f'taxi-approvals/drafts/{rule_id}/reject/')
    def mock_approvals_drafts_reject(request):
        assert YANDEX_LOGIN_HEADER in request.headers
        data = json.loads(request.get_data())
        assert 'comment' in data and data['comment']
        return {'id': rule_id, 'version': 1, 'status': 'rejected', 'data': {}}

    # cancel approvals
    response = await taxi_pricing_admin.post(
        'v1/settings/rule/cancel',
        headers={YANDEX_LOGIN_HEADER: '200ok draft'},
        params={'id': rule_id},
        json={'comment': 'very important info'},
    )
    assert response.status_code == status_code
    if error_code:
        resp = response.json()
        assert 'code' in resp and resp['code'] == error_code
    else:
        assert mock_approvals_drafts_reject.has_calls
        assert mock_approvals_drafts_reject.times_called == 1


@pytest.mark.pgsql(
    'pricing_data_preparer',
    files=['rules.sql', 'workabilities.sql'],
    queries=[
        """DELETE FROM price_modifications.rules_drafts
             WHERE name = '{}'""".format(
            'one',
        ),
        """DELETE FROM price_modifications.workabilities
             WHERE rule_id = {}""".format(
            2,
        ),
    ],
)
@pytest.mark.parametrize(
    'rule_id,status_code,error_code,rule_or_draft',
    [
        (1001, 422, 'disallowed', None),
        (1003, 200, None, 'rule'),
        (1008, 200, None, 'draft'),
    ],
)
async def test_v1_settings_rules_delete_by_id(
        taxi_pricing_admin,
        pgsql,
        rule_id,
        status_code,
        error_code,
        rule_or_draft,
        mockserver,
):
    @mockserver.json_handler('taxi-approvals/v2/drafts/')
    def _mock_approvals_drafts_get(request):
        data = request.args
        assert 'id' in data
        return {
            'id': int(data['id']),
            'version': 1,
            'status': 'expired',
            'data': {},  # empty because unused
        }

    @mockserver.json_handler('pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        task_id = int(data['id'])
        if task_id == 1:
            return {'done': 'in_progress'}
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'error', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    assert does_id_exist(pgsql, rule_id)
    response = await taxi_pricing_admin.delete(
        'v1/settings/rules', params={'id': rule_id},
    )
    assert response.status_code == status_code
    if error_code:
        resp = response.json()
        assert 'code' in resp and resp['code'] == error_code
    else:
        response = await taxi_pricing_admin.get(
            'v1/settings/rules', params={'status': 'approved'},
        )
        assert response.status_code == 200
        resp = response.json()
        assert 'rules' in resp
        if rule_or_draft == 'draft':
            assert not does_id_exist(pgsql, rule_id)
            assert len(resp['rules']) == 5
        elif rule_or_draft == 'rule':
            assert len(resp['rules']) == 4


@pytest.mark.pgsql('pricing_data_preparer', files=['rules_with_history.sql'])
@pytest.mark.parametrize(
    'draft_name,expected_previous_version',
    [
        ('draft_with_base_rule', 1),
        ('draft_with_no_base_rule', 3),
        ('draft_new_rule', None),
    ],
)
async def test_apply_approvals_history(
        taxi_pricing_admin,
        taxi_config,
        draft_name,
        expected_previous_version,
        pgsql,
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
        data = request.args
        assert 'id' in data
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'ok', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=True)

    def _fetch_prev_rule(rule_name):
        with pgsql['pricing_data_preparer'].cursor() as cursor:
            cursor.execute(
                'SELECT previous_version_id'
                ' FROM price_modifications.rules '
                f'WHERE name = \'{rule_name}\' AND deleted = false',
            )
            return cursor.fetchone()[0]

    rule = {
        'name': draft_name,
        'source_code': 'return ride.price;',
        'policy': 'backend_only',
    }
    response = await taxi_pricing_admin.post(
        'v1/service/approvals/rule/apply', json=rule,
    )
    assert response.status_code == 200
    prev_rule_id = _fetch_prev_rule(draft_name)
    assert prev_rule_id == expected_previous_version


@pytest.mark.parametrize(
    'source_code, expected_ast',
    [
        (
            """using(UserMeta) {
               if ("foo" in ride.ride.user_meta) {
                 return {metadata=["foo": 1]};
               } else {
                 return {metadata=["foo": 0]};
               }
               }
               return ride.price;""",
            'FG(UserMeta,IF(SL(2,19,2,47,B("foo",in,B(B(ride,.,F(ride)),.,F(user_meta)))),CR(metadata=SL(3,34,3,44,MAP("foo"=1.000000))),CR(metadata=SL(5,34,5,44,MAP("foo"=0.000000)))));CR(boarding=B(SL(8,22,8,32,B(ride,.,F(price))),.,F(boarding)),destination_waiting=B(SL(8,22,8,32,B(ride,.,F(price))),.,F(destination_waiting)),distance=B(SL(8,22,8,32,B(ride,.,F(price))),.,F(distance)),requirements=B(SL(8,22,8,32,B(ride,.,F(price))),.,F(requirements)),time=B(SL(8,22,8,32,B(ride,.,F(price))),.,F(time)),transit_waiting=B(SL(8,22,8,32,B(ride,.,F(price))),.,F(transit_waiting)),waiting=B(SL(8,22,8,32,B(ride,.,F(price))),.,F(waiting)))',
        ),
        (
            """using(UserMeta) {let _boarding = ("foo" in ride.ride.user_meta)
                 ? ride.price.boarding * 42
                 : ride.price.boarding;
               return {boarding = _boarding};} return ride.price;""",
            'FG(UserMeta,SV(_boarding,SL(1,33,3,38,T(SL(1,34,1,62,B("foo",in,B(B(ride,.,F(ride)),.,F(user_meta)))),SL(2,19,3,17,B(B(B(ride,.,F(price)),.,F(boarding)),*,42.000000)),SL(3,19,3,38,B(B(ride,.,F(price)),.,F(boarding))))));CR(boarding=SL(4,34,4,43,VA(_boarding))));CR(boarding=B(SL(4,54,4,64,B(ride,.,F(price))),.,F(boarding)),destination_waiting=B(SL(4,54,4,64,B(ride,.,F(price))),.,F(destination_waiting)),distance=B(SL(4,54,4,64,B(ride,.,F(price))),.,F(distance)),requirements=B(SL(4,54,4,64,B(ride,.,F(price))),.,F(requirements)),time=B(SL(4,54,4,64,B(ride,.,F(price))),.,F(time)),transit_waiting=B(SL(4,54,4,64,B(ride,.,F(price))),.,F(transit_waiting)),waiting=B(SL(4,54,4,64,B(ride,.,F(price))),.,F(waiting)))',
        ),
    ],
)
async def test_v1_settings_rules_rule_with_user_meta(
        taxi_pricing_admin,
        taxi_config,
        mockserver,
        pgsql,
        source_code,
        expected_ast,
):
    @mockserver.json_handler('taxi-approvals/drafts/create/')
    def _mock_approvals_create_draft(request):
        data = json.loads(request.get_data())
        return {'id': 1, 'status': 'need_approval', 'data': data['data']}

    @mockserver.json_handler('/pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        return {'done': 'in_progress'}

    @mockserver.json_handler('/pricing-modifications-validator/v1/add_task')
    def _mock_pmv_v1_task_tesult(request):
        return {'id': 1}

    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=True)

    def _get_ast(rule_id):
        with pgsql['pricing_data_preparer'].cursor() as cursor:
            cursor.execute(
                'SELECT ast FROM price_modifications.rules_drafts '
                f'WHERE rule_id = {rule_id}',
            )
            return cursor.fetchone()[0]

    headers = {YANDEX_LOGIN_HEADER: '200ok'}
    rule = {
        'extra_returns': [],
        'name': 'rule#0',
        'policy': 'both_side',
        'source_code': source_code,
    }

    response = await taxi_pricing_admin.put(
        'v1/settings/rules', headers=headers, json=rule,
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'id' in resp
    rule_id = resp['id']
    assert _get_ast(rule_id) == expected_ast

    pg_request = 'SELECT * FROM price_modifications.rules_drafts WHERE name = \'rule#0\''
    db_draft = select_named(pg_request, pgsql)[0]
    assert db_draft is not None


@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules_with_prestable_evaluation.sql'],
)
async def test_v1_rules_reset_evaluate_on_prestable_time(
        taxi_pricing_admin, load_json, pgsql, mockserver,
):
    headers = {YANDEX_LOGIN_HEADER: '200ok'}
    rule_one = load_json('rule_one.json')

    pg_request = (
        'SELECT * FROM price_modifications.rules_drafts WHERE name = \'one\''
    )
    db_draft = select_named(pg_request, pgsql)[0]
    assert (
        db_draft['prestable_evaluation_begin_time'].strftime(
            '%Y-%m-%d %H:%M:%S',
        )
        == '2020-05-03 19:10:25'
    )

    @mockserver.json_handler('pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        task_id = int(data['id'])
        if task_id == 1:
            return {'done': 'in_progress'}
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'error', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    response = await taxi_pricing_admin.put(
        'v1/settings/rules', headers=headers, json=rule_one,
    )
    assert response.status_code == 200
    db_draft = select_named(pg_request, pgsql)[0]
    assert db_draft['prestable_evaluation_begin_time'] is None


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_v1_settings_rules_put_reset_tests_on_draft_edit(
        taxi_pricing_admin, load_json, pgsql, mockserver,
):
    headers = {YANDEX_LOGIN_HEADER: '200ok'}
    rule_one = load_json('rule_one.json')

    @mockserver.json_handler('pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        task_id = int(data['id'])
        if task_id == 1:
            return {'done': 'in_progress'}
        return {
            'done': 'finished',
            'results': [
                {'test_result': 'error', 'test_name': 'nan_test'},
                {'test_result': 'ok', 'test_name': 'map_test'},
            ],
        }

    response = await taxi_pricing_admin.put(
        'v1/settings/rules', headers=headers, json=rule_one,
    )
    assert response.status_code == 200

    pg_request = (
        'SELECT last_result, last_result_rule_id '
        'FROM price_modifications.tests WHERE rule_name = \'one\''
    )
    rows = select_named(pg_request, pgsql)
    assert rows
    for test_result in rows:
        assert test_result['last_result'] is None
        assert test_result['last_result_rule_id'] is None
