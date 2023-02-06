import json

import pytest

YANDEX_LOGIN_HEADER = 'X-Yandex-Login'


def _get_pmv_task_id_and_approvals_id(pgsql, rule_id):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'SELECT pmv_task_id, approvals_id '
            'FROM ONLY price_modifications.rules_drafts '
            'WHERE rule_id = %s',
            (rule_id,),
        )
        row = cursor.fetchone()
        return row


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize(
    'rule_id, name, is_draft, status_code,'
    'is_deleted, previous_version_id,'
    'startrek_ticket',
    [
        (100500, 'not_exist', None, 404, None, None, None),
        (1, 'one', False, 200, False, 0, 'EFFICIENCYDEV-16339'),
        (7, 'one', True, 200, False, None, 'EFFICIENCYDEV-16339'),
        (0, 'one', False, 200, True, None, None),
    ],
)
async def test_v1_settings_rule_get(
        taxi_pricing_admin,
        rule_id,
        name,
        is_draft,
        status_code,
        is_deleted,
        previous_version_id,
        startrek_ticket,
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

    response = await taxi_pricing_admin.get(
        'v1/settings/rule', params={'id': rule_id},
    )
    assert response.status_code == status_code

    if response.status_code == 200:
        resp = response.json()
        assert 'rule' in resp
        rule = resp['rule']
        assert 'name' in rule and rule['name'] == name
        assert rule['is_deleted'] == is_deleted
        if previous_version_id is not None:
            assert rule['previous_version_id'] == previous_version_id
        if is_draft:
            assert 'status' in rule
            assert 'pmv_task_id' in rule
            assert 'evaluate_on_prestable' in rule
            if startrek_ticket is not None:
                assert startrek_ticket == rule['startrek_ticket']


@pytest.mark.pgsql('pricing_data_preparer', files=['rules_status.sql'])
@pytest.mark.parametrize('rule_id', [1, 2, 3, 4, 5, 6, 7])
async def test_v1_settings_rule_get_status(
        taxi_pricing_admin, taxi_config, mockserver, rule_id,
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

    @mockserver.json_handler('pricing-modifications-validator/v1/task_result')
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

    response = await taxi_pricing_admin.get(
        'v1/settings/rule', params={'id': rule_id},
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'rule' in resp
    rule = resp['rule']
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
    'rule_id, expected_eval_begin_time',
    [(6, '2020-05-03T16:10:25+00:00'), (7, None)],
)
async def test_v1_settings_rule_get_prestable_eval_begin_time(
        taxi_pricing_admin, rule_id, expected_eval_begin_time, mockserver,
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

    response = await taxi_pricing_admin.get(
        'v1/settings/rule', params={'id': rule_id},
    )
    assert response.status_code == 200
    resp = response.json()['rule']
    if expected_eval_begin_time:
        assert (
            resp['prestable_evaluation_begin_time'] == expected_eval_begin_time
        )
    else:
        assert 'prestable_evaluation_begin_time' not in resp


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize('pmv_enabled', [True, False])
@pytest.mark.parametrize('rule_id', [6, 8])
async def test_v1_settings_rule_cancel(
        taxi_pricing_admin,
        taxi_config,
        pgsql,
        mockserver,
        pmv_enabled,
        rule_id,
):
    pmv_task_id, approvals_id = _get_pmv_task_id_and_approvals_id(
        pgsql, rule_id,
    )

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

    @mockserver.json_handler(f'taxi-approvals/drafts/{approvals_id}/reject/')
    def _mock_approvals_drafts_reject(request):
        return {
            'id': approvals_id,
            'version': 1,
            'status': 'rejected',
            'data': {},
        }

    @mockserver.json_handler('pricing-modifications-validator/v1/cancel_task')
    def _mock_pmv_v1_cancel_task(request):
        data = json.loads(request.get_data())
        assert 'id' in data
        assert data['id'] == pmv_task_id
        return {}

    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=pmv_enabled)
    response = await taxi_pricing_admin.post(
        'v1/settings/rule/cancel',
        params={'id': rule_id},
        json={'comment': 'need terminate'},
        headers={YANDEX_LOGIN_HEADER: '200ok'},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'target_value, rule_id, expected_code, expected_time',
    [
        (True, 10, 200, None),
        (False, 10, 400, None),
        (True, 6, 400, '2020-05-03T19:10:25+03:00'),
        (False, 6, 200, None),
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_v1_settings_prestable_check(
        taxi_pricing_admin,
        target_value,
        rule_id,
        expected_code,
        expected_time,
        pgsql,
):
    response = await taxi_pricing_admin.post(
        'v1/settings/rule/prestable_check',
        params={'id': rule_id},
        json={'evaluate_on_prestable': target_value},
    )
    assert response.status_code == expected_code

    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'SELECT prestable_evaluation_begin_time '
            'FROM price_modifications.rules_drafts '
            f'WHERE rule_id = {rule_id}',
        )
        begin_time = cursor.fetchone()[0]
        if begin_time:
            begin_time = begin_time.isoformat()
        assert begin_time == expected_time


AST_STRING = (
    'CR(boarding=TX(1,0),destination_waiting=TX(1,6)'
    ',distance=TX(1,1),metadata=NT(),requirements=51.000000,'
    'time=TX(1,2),transit_waiting=TX(1,5),waiting=TX(1,3))'
)

DRAFT_REQUEST_LONG_STORY = {
    'api_path': 'price_modifications_rules_create',
    'change_doc_id': '1',
    'mode': 'push',
    'run_manually': False,
    'service_name': 'pricing-admin',
    'data': {
        'description': 'description',
        'extra_returns': [],
        'name': 'rule_with_long_story',
        'policy': 'both_side',
        'source_code': 'return ride.price;',
    },
}
DRAFT_REQUEST_LINE_STORY = {
    'api_path': 'price_modifications_rules_create',
    'change_doc_id': '3',
    'mode': 'push',
    'run_manually': False,
    'service_name': 'pricing-admin',
    'data': {
        'description': 'description3',
        'extra_returns': [],
        'name': 'rule_with_line_story',
        'policy': 'both_side',
        'source_code': 'return ride.price*3;',
        'startrek_ticket': 'EFFICIENCYDEV-16339',
    },
    'tickets': {'existed': ['EFFICIENCYDEV-16339']},
}


@pytest.mark.parametrize(
    (
        'rule_id,expected_response,'
        'expected_draft_request,drafts_fail,expected_draft'
    ),
    [
        (2, 400, None, False, None),
        (6, 400, None, False, None),
        (5, 400, DRAFT_REQUEST_LONG_STORY, True, None),
        (
            5,
            200,
            DRAFT_REQUEST_LONG_STORY,
            False,
            {
                'approvals_id': 42,
                'ast': AST_STRING,
                'author': 'gordon_freeman',
                'description': 'description',
                'source_code': 'return ride.price;',
                'extra_return': [],
                'name': 'rule_with_long_story',
                'policy': 'both_side',
                'previous_version_id': None,
                'startrek_ticket': None,
            },
        ),
        (
            4,
            200,
            DRAFT_REQUEST_LINE_STORY,
            False,
            {
                'approvals_id': 42,
                'ast': AST_STRING,
                'author': 'gordon_freeman',
                'description': 'description3',
                'source_code': 'return ride.price*3;',
                'extra_return': [],
                'name': 'rule_with_line_story',
                'policy': 'both_side',
                'previous_version_id': 2,
                'startrek_ticket': 'EFFICIENCYDEV-16339',
            },
        ),
    ],
    ids=[
        'deleted_rule',
        'empty_history_rule',
        'drafts_failed',
        'successfull_rollback_no_history',
        'successfull_rollback_with_history',
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules_with_history.sql'])
async def test_v1_settings_rollback(
        taxi_pricing_admin,
        rule_id,
        expected_response,
        expected_draft,
        drafts_fail,
        expected_draft_request,
        mockserver,
        pgsql,
):
    def _fetch_total_drafts_count():
        with pgsql['pricing_data_preparer'].cursor() as cursor:
            cursor.execute(
                f'SELECT COUNT(*) FROM ONLY price_modifications.rules_drafts',
            )
            return cursor.fetchone()[0]

    def _fetch_draft_by_id(draft_id):
        draft_fields = [
            'name',
            'description',
            'source_code',
            'policy',
            'author',
            'ast',
            'extra_return',
            'approvals_id',
            'previous_version_id',
            'startrek_ticket',
        ]
        with pgsql['pricing_data_preparer'].cursor() as cursor:
            cursor.execute(
                f'SELECT {", ".join(draft_fields)}'
                ' FROM ONLY price_modifications.rules_drafts '
                f'WHERE rule_id={draft_id}',
            )
            return {
                draft_fields[i]: value
                for i, value in enumerate(cursor.fetchone())
            }

    # pylint: disable=unused-variable
    @mockserver.json_handler('taxi-approvals/drafts/create/')
    def mock_approvals_drafts_create(request):
        if drafts_fail:
            return mockserver.make_response('Failed data', 500)
        data = json.loads(request.get_data())
        data.pop('request_id')
        assert data == expected_draft_request
        data['id'] = 42
        data['status'] = 'need_approval'
        data['version'] = 1
        if 'tickets' in data:
            data['tickets'] = data['tickets']['existed']
        return data

    @mockserver.json_handler('pricing-modifications-validator/v1/add_task')
    def _mock_pmv_v1_add_task(request):
        data = json.loads(request.get_data())
        assert 'constraints' in data
        assert 'script' in data
        return {'id': 1}

    @mockserver.json_handler('taxi-approvals/drafts/list/')
    def _mock_approvals_drafts_list(request):
        data = json.loads(request.get_data())
        assert 'drafts_ids' in data or 'change_doc_ids' in data
        return []

    drafts_before_rollback = _fetch_total_drafts_count()

    response = await taxi_pricing_admin.post(
        'v1/settings/rule/rollback',
        params={'id': rule_id},
        headers={'X-Yandex-Login': 'gordon_freeman'},
        json={},
    )
    assert response.status_code == expected_response

    if expected_response != 200:
        assert _fetch_total_drafts_count() == drafts_before_rollback

    if expected_draft is not None:
        draft_id = response.json()['draft_id']
        assert _fetch_draft_by_id(draft_id) == expected_draft
