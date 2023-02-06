import pytest

from taxi_approvals.internal import headers as headers_module
from test_taxi_approvals import models


def _create_summoned_users(logins):
    return [
        {'login': login, 'summoned': '2017-11-01T01:10:00+0300'}
        for login in logins
    ]


def _create_comments(
        *, not_found_logins=None, existed_tickets=None, new_ticket=None,
):
    comments = []
    if not_found_logins:
        not_found_text = ', '.join(not_found_logins)
        comments.append(
            {
                'login': 'test_login',
                'comment': (
                    f'Следующих пользователей не удалось найти '
                    f'или у них нет прав на подтверждение черновика: '
                    f'{not_found_text}. Они не будут призваны'
                ),
            },
        )

    if existed_tickets:
        tickets = ', '.join(existed_tickets)
        if len(existed_tickets) == 1:
            comment = f'test_login прикрепил тикет {tickets}'
        else:
            comment = f'test_login прикрепил тикеты {tickets}'
        comments.append({'login': 'test_login', 'comment': comment})

    if new_ticket:
        comments.append(
            {
                'login': 'test_login',
                'comment': f'test_login создал и прикрепил тикет {new_ticket}',
            },
        )
    return comments


@pytest.mark.parametrize(
    'case,response_case',
    [
        pytest.param(
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_no_default_allowed',
                summon_users=['test_manager', 'test_developer'],
                data=dict(developers=True),
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_no_default_allowed',
                comments=_create_comments(not_found_logins=['test_developer']),
                summoned_users=_create_summoned_users(['test_manager']),
                data={'developers': True},
                attached_tickets=[],
            ),
            id='test disable_approval, allowed is True, item_name is True',
        ),
        pytest.param(
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_no_default_allowed',
                summon_users=['test_manager', 'test_developer'],
                data=dict(developers=False),
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_no_default_allowed',
                comments=[],
                summoned_users=_create_summoned_users(
                    ['test_developer', 'test_manager'],
                ),
                data={'developers': False},
                attached_tickets=[],
            ),
            id='test disable_approval, allowed is True, item_name is False',
        ),
        pytest.param(
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_no_default_allowed',
                summon_users=['test_manager', 'test_developer'],
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_no_default_allowed',
                comments=[],
                summoned_users=_create_summoned_users(
                    ['test_developer', 'test_manager'],
                ),
                data={'test_data_key': 'test_data_value'},
                attached_tickets=[],
            ),
            id='test disable_approval, allowed is True, item_name is None',
        ),
        pytest.param(
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_no_default_forbidden',
                summon_users=['test_manager', 'test_developer'],
                data=dict(developers=True),
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_no_default_forbidden',
                comments=[],
                summoned_users=_create_summoned_users(
                    ['test_developer', 'test_manager'],
                ),
                data={'developers': True},
                attached_tickets=[],
            ),
            id='test disable_approval, forbidden is True, item_name is True',
        ),
        pytest.param(
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_no_default_forbidden',
                summon_users=['test_manager', 'test_developer'],
                data=dict(developers=False),
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_no_default_forbidden',
                comments=_create_comments(not_found_logins=['test_developer']),
                summoned_users=_create_summoned_users(['test_manager']),
                data={'developers': False},
                attached_tickets=[],
            ),
            id='test disable_approval, forbidden is True, item_name is False',
        ),
        pytest.param(
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_no_default_forbidden',
                summon_users=['test_manager', 'test_developer'],
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_no_default_forbidden',
                comments=[],
                summoned_users=_create_summoned_users(
                    ['test_developer', 'test_manager'],
                ),
                data={'test_data_key': 'test_data_value'},
                attached_tickets=[],
            ),
            id='test disable_approval, forbidden is True, item_name is None',
        ),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_disable_approval(
        case,
        response_case,
        patch,
        taxi_approvals_client,
        check_route_mock,
        create_reports_mock,
):
    params = {}
    if case.route_params:
        params.update(case.route_params)
    if case.is_platform:
        params['tplatform_namespace'] = 'market'

    check_route_mock(
        change_doc_id=case.change_doc_id,
        lock_ids=case.lock_ids_from_check,
        route_method=case.route_method,
        route_headers=case.route_headers,
        route_params=params,
        tickets=case.ticket_data_from_check,
        summon_users=case.summon_users_from_check,
        mode=case.check_mode,
        data=case.data,
        description='description from service answer',
    )
    summary = {}
    create_reports_mock(
        21,
        summary,
        response_case.service_name,
        response_case.api_path,
        response_case.attached_tickets,
    )

    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    @patch('taxi_approvals.internal.check_draft._render_summary')
    def _render_summary(diff):
        return {}

    headers = {headers_module.X_YANDEX_LOGIN: 'test_login'}
    if case.route_headers:
        headers.update(case.route_headers)
    if case.is_platform:
        headers[headers_module.X_MULTISERVICES_PLATFORM] = 'true'

    request_data = None
    if case.data and isinstance(case.data, dict):
        request_data = case.data

    response = await taxi_approvals_client.post(
        '/drafts/create/',
        json=case.request_data(request_data),
        headers=headers,
        params=params,
    )
    content = await response.json()
    assert response.status == response_case.status, content

    if response_case.headers:
        assert content['headers'] == response_case.headers

    if response_case.status == 200:
        content.pop('id')
        assert content == response_case.response_data
    else:
        assert content['code'] == response_case.error_code
