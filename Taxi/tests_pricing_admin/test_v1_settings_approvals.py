import json

import pytest


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize(
    'rule_id, status_code, approvals_id',
    [
        (1, 400, None),
        (2, 400, None),
        (3, 200, 333),
        (4, 200, 444),
        (5, 200, 555),
    ],
)
async def test_v1_settings_approvals_retry(
        taxi_pricing_admin, rule_id, status_code, approvals_id, mockserver,
):
    @mockserver.json_handler('taxi-approvals/v2/drafts/')
    def _mock_approvals_drafts_get(request):
        data = request.args
        assert 'id' in data
        if int(data['id']) == 1:
            return {
                'id': int(data['id']),
                'version': 1,
                'status': 'expired',
                'data': {},
            }
        if int(data['id']) == 2:
            return {
                'id': int(data['id']),
                'version': 1,
                'status': 'succeeded',
                'data': {},
            }
        return {}

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

    @mockserver.json_handler('taxi-approvals/drafts/list/')
    def _mock_approvals_drafts_list(request):
        data = json.loads(request.get_data())
        assert 'change_doc_ids' in data
        if data['change_doc_ids'] == ['pricing-admin_3']:
            return [{'id': 333, 'version': 1, 'status': 'expired', 'data': {}}]
        if data['change_doc_ids'] == ['pricing-admin_4']:
            return [
                {'id': 444, 'version': 1, 'status': 'expired', 'data': {}},
                {'id': 4444, 'version': 1, 'status': 'expired', 'data': {}},
            ]
        return []

    @mockserver.json_handler('taxi-approvals/drafts/create/')
    def _mock_approvals_drafts_create(request):
        data = json.loads(request.get_data())
        if int(data['change_doc_id']) == 1:
            return {'id': 111, 'version': 1, 'status': 'succeeded', 'data': {}}
        if int(data['change_doc_id']) == 5:
            return {'id': 555, 'version': 1, 'status': 'succeeded', 'data': {}}
        return {}

    response = await taxi_pricing_admin.post(
        'v1/settings/approvals/retry', params={'id': [rule_id]},
    )

    assert response.status_code == status_code
    if response.status_code == 200:
        resp = response.json()
        assert resp['approvals_id'] == approvals_id
