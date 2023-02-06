import pytest

from taxi_approvals.internal import headers as headers_module
from test_taxi_approvals import models


@pytest.mark.parametrize(
    'case, manager_login',
    [
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api',
                description='test default managers summon',
            ),
            None,
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_draft_summon_managers',
                description='test enable managers summon',
            ),
            'test_manager',
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_draft_not_summon_managers',
                description='test disable managers summon',
            ),
            None,
        ),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_create_draft(
        case,
        patch,
        taxi_approvals_client,
        check_route_mock,
        create_reports_mock,
        mockserver,
        manager_login,
):
    ticket_data_from_check = {
        'create_data': {
            'summary': 'test_summary',
            'description': 'test_description',
            'relationships': {'relates': ['TESTTICKET-1', 'TESTTICKET-2']},
        },
    }
    check_route_mock(
        change_doc_id=case.change_doc_id,
        lock_ids=case.lock_ids_from_check,
        route_method=case.route_method,
        route_headers=case.route_headers,
        route_params=case.route_params,
        tickets=ticket_data_from_check,
        summon_users=case.summon_users_from_check,
        mode=case.check_mode,
        data=case.data,
        description='description from service answer',
    )

    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    @patch('taxi_approvals.internal.check_draft._render_summary')
    def _render_summary(diff):
        return {}

    @mockserver.json_handler('/startrack_reports/v2/create_comments/')
    def _mock_create_comments(request):
        if manager_login:
            assert manager_login in request.json['tickets'][0]['summonees']
        return {}

    headers = {headers_module.X_YANDEX_LOGIN: 'test_login'}
    response = await taxi_approvals_client.post(
        '/drafts/create/',
        json=case.request_data(None),
        headers=headers,
        params=case.route_params,
    )
    assert response.status == 200
