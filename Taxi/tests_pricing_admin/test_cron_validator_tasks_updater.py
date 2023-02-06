import json

import pytest


def get_rule_draft_status_by_name(pgsql, name):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'SELECT status '
            'FROM ONLY price_modifications.rules_drafts '
            'WHERE name = %s',
            (name,),
        )
        return cursor.fetchone()[0]


@pytest.mark.pgsql('pricing_data_preparer', files=['rules_drafts.sql'])
async def test_v1_settings_rules_get(
        taxi_pricing_admin, taxi_config, mockserver, pgsql, testpoint,
):
    @testpoint('status_check')
    def _testing_status(data):
        if 'pmv_task_id' not in data:
            assert data['status'] == 'not_started'
            return
        assert 'pmv_task_id' in data
        assert 'status' in data
        if int(data['pmv_task_id']) == 1:
            assert data['status'] == 'running'
            return
        if int(data['pmv_task_id']) == 2:
            assert data['status'] == 'to_approve'
            return
        if int(data['pmv_task_id']) == 3:
            assert data['status'] == 'to_approve'
            return
        if int(data['pmv_task_id']) == 4:
            assert data['status'] == 'failure'
            return
        if int(data['pmv_task_id']) == 5:
            assert data['status'] == 'canceled'
            return
        if int(data['pmv_task_id']) == 8:
            assert data['status'] == 'draft_create_error'
            return
        if int(data['pmv_task_id']) == 6:
            assert data['status'] == 'failure'
            return
        if int(data['pmv_task_id']) == 7:
            assert data['status'] == 'failure'
            return

    @mockserver.json_handler('/pricing-modifications-validator/v1/task_result')
    def _mock_pmv_v1_task_tesult(request):
        data = request.args
        assert 'id' in data
        task_id = int(data['id'])
        if task_id == 1:
            return {'done': 'in_progress'}
        if task_id == 2:
            return {
                'done': 'finished',
                'results': [
                    {'test_result': 'ok', 'test_name': 'nan_test'},
                    {'test_result': 'ok', 'test_name': 'map_test'},
                ],
            }
        if task_id == 3:
            return {
                'done': 'finished',
                'results': [
                    {'test_result': 'ok', 'test_name': 'nan_test'},
                    {'test_result': 'warning', 'test_name': 'map_test'},
                ],
            }
        if task_id == 4:
            return {
                'done': 'finished',
                'results': [
                    {'test_result': 'error', 'test_name': 'nan_test'},
                    {'test_result': 'ok', 'test_name': 'map_test'},
                ],
            }
        if task_id == 5:
            return {'done': 'finished'}
        if task_id == 6:
            return mockserver.make_response(status=500, json={})
        if task_id == 7:
            return mockserver.make_response(status=512, json={})
        return mockserver.make_response(status=404, json={})

    @mockserver.json_handler('taxi-approvals/drafts/create/')
    def mock_approvals_drafts_create(request):
        data = json.loads(request.get_data())
        data['id'] = mock_approvals_drafts_create.times_called
        data['version'] = 1
        data['status'] = 'need_approval'
        return data

    @mockserver.json_handler('taxi-approvals/v2/drafts/')
    def _mock_approvals_drafts_get(request):
        data = request.args
        assert 'id' in data
        if int(data['id']) in (22, 33, 44):
            return {
                'id': int(data['id']),
                'version': 1,
                'status': 'need_approval',
                'data': {},
            }
        return {
            'id': int(data['id']),
            'version': 1,
            'status': 'expired',
            'data': {},
        }

    taxi_config.set(PRICING_DATA_PREPARER_PMV_ENABLED=True)

    response = await taxi_pricing_admin.post(
        'service/cron', json={'task_name': 'validator-tasks-updater'},
    )
    assert response.status_code == 200
