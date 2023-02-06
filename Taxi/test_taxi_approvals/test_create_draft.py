import pytest

from taxi_approvals.internal import headers as headers_module
from taxi_approvals.internal import models as taxi_models
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
        (
            models.CreateTestCase(route_headers={'X-Yandex-Uid': 'test_uid'}),
            models.CreateResponse(
                status=200,
                headers={'X-Yandex-Uid': 'test_uid'},
                attached_tickets=[],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api',
                change_doc_id='test_doc_id',
                lock_ids_from_check=[],
                deferred_apply='2018-01-01T12:00:00+02:00',
                run_manually=False,
                summon_users=['test_login'],
                route_headers={
                    'X-YaTaxi-Draft-Author': 'test_login',
                    'X-YaTaxi-Draft-DeferredApply': '2018-01-01T13:00:00+0300',
                    'X-YaTaxi-Draft-RunType': 'automatically',
                    'X-YaTaxi-Draft-Service-Name': 'test_service',
                    'X-YaTaxi-Draft-Api-Path': 'test_api',
                },
                ticket_data_from_check={
                    'create_data': {
                        'summary': 'test_summary',
                        'description': 'test_description',
                        'components': [45167],
                        'tags': ['test_tag'],
                        'relationships': {
                            'relates': ['TESTTICKET-1', 'TESTTICKET-2'],
                        },
                    },
                },
                summon_users_from_check=['test_login_2'],
                description='test1 description',
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_api',
                expected_change_doc_id='test_doc_id',
                deferred_apply='2018-01-01T13:00:00+0300',
                run_manually=False,
                attached_tickets=['RUPRICING-100'],
                headers={},
                summoned_users=[
                    {
                        'login': 'test_login_2',
                        'summoned': '2017-11-01T01:10:00+0300',
                    },
                ],
                version=2,
                comments=[
                    {
                        'comment': (
                            'Следующих пользователей не удалось найти '
                            'или у них нет прав на подтверждение черновика: '
                            'test_login. Они не будут призваны'
                        ),
                        'login': 'test_login',
                    },
                    {
                        'comment': (
                            'test_login создал и прикрепил тикет RUPRICING-100'
                        ),
                        'login': 'test_login',
                    },
                ],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api',
                change_doc_id='test_doc_id',
                attach_tickets={'existed': ['TAXIRATE-35']},
                lock_ids_from_check=[],
                deferred_apply='2018-01-01T12:00:00+02:00',
                run_manually=False,
                summon_users=['test_login'],
                route_headers={
                    'X-YaTaxi-Draft-Author': 'test_login',
                    'X-YaTaxi-Draft-DeferredApply': '2018-01-01T13:00:00+0300',
                    'X-YaTaxi-Draft-RunType': 'automatically',
                    'X-YaTaxi-Draft-Tickets': 'TAXIRATE-35',
                    'X-YaTaxi-Ticket': 'TAXIRATE-35',
                    'X-YaTaxi-Draft-Service-Name': 'test_service',
                    'X-YaTaxi-Draft-Api-Path': 'test_api',
                },
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_api',
                expected_change_doc_id='test_doc_id',
                deferred_apply='2018-01-01T13:00:00+0300',
                run_manually=False,
                attached_tickets=['TAXIRATE-35'],
                headers={},
                summoned_users=[],
                version=2,
                comments=[
                    {
                        'comment': (
                            'Следующих пользователей не удалось найти '
                            'или у них нет прав на подтверждение черновика: '
                            'test_login. Они не будут призваны'
                        ),
                        'login': 'test_login',
                    },
                    {
                        'comment': 'test_login прикрепил тикет TAXIRATE-35',
                        'login': 'test_login',
                    },
                ],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api',
                change_doc_id='test_doc_id',
                attach_tickets={
                    'existed': ['https://st.test.yandex-team.ru/TAXIRATE-35'],
                },
                lock_ids_from_check=[],
                deferred_apply='2018-01-01T12:00:00+02:00',
                run_manually=False,
                summon_users=['test_login'],
                route_headers={
                    'X-YaTaxi-Draft-Author': 'test_login',
                    'X-YaTaxi-Draft-DeferredApply': '2018-01-01T13:00:00+0300',
                    'X-YaTaxi-Draft-RunType': 'automatically',
                    'X-YaTaxi-Draft-Tickets': 'TAXIRATE-35',
                    'X-YaTaxi-Ticket': 'TAXIRATE-35',
                    'X-YaTaxi-Draft-Service-Name': 'test_service',
                    'X-YaTaxi-Draft-Api-Path': 'test_api',
                },
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_api',
                expected_change_doc_id='test_doc_id',
                deferred_apply='2018-01-01T13:00:00+0300',
                run_manually=False,
                attached_tickets=['TAXIRATE-35'],
                headers={},
                summoned_users=[],
                version=2,
                comments=[
                    {
                        'comment': (
                            'Следующих пользователей не удалось найти '
                            'или у них нет прав на подтверждение черновика: '
                            'test_login. Они не будут призваны'
                        ),
                        'login': 'test_login',
                    },
                    {
                        'comment': 'test_login прикрепил тикет TAXIRATE-35',
                        'login': 'test_login',
                    },
                ],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api',
                change_doc_id='test_doc_id',
                lock_ids_from_check=[],
                deferred_apply='2018-01-01T12:00:00+02:00',
                run_manually=False,
                summon_users=['test_login'],
                route_headers={
                    'X-YaTaxi-Draft-Author': 'test_login',
                    'X-YaTaxi-Draft-DeferredApply': '2018-01-01T13:00:00+0300',
                    'X-YaTaxi-Draft-RunType': 'automatically',
                    'X-YaTaxi-Draft-Tickets': 'TAXIRATE-35',
                    'X-YaTaxi-Ticket': 'TAXIRATE-35',
                    'X-YaTaxi-Draft-Service-Name': 'test_service',
                    'X-YaTaxi-Draft-Api-Path': 'test_api',
                },
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_api',
                expected_change_doc_id='test_doc_id',
                deferred_apply='2018-01-01T13:00:00+0300',
                run_manually=False,
                attached_tickets=['TAXIRATE-35'],
                headers={},
                summoned_users=[],
                version=2,
                comments=[
                    {
                        'comment': (
                            'Следующих пользователей не удалось найти '
                            'или у них нет прав на подтверждение черновика: '
                            'test_login. Они не будут призваны'
                        ),
                        'login': 'test_login',
                    },
                    {
                        'comment': 'test_login прикрепил тикет TAXIRATE-35',
                        'login': 'test_login',
                    },
                ],
            ),
        ),
        (
            models.CreateTestCase(
                deferred_apply='2016-01-01T12:00:00+02:00', run_manually=False,
            ),
            models.CreateResponse(
                status=400, error_code='DEFERRED_APPLY_TIME_ERROR',
            ),
        ),
        (
            models.CreateTestCase(
                deferred_apply='2018-01-01T12:00:00+02:00', run_manually=True,
            ),
            models.CreateResponse(
                status=400, error_code='DEFERRED_APPLY_MANUALLY_ERROR',
            ),
        ),
        (
            models.CreateTestCase(
                deferred_apply='2018-01-01T12:00:00+02:00',
                run_manually=False,
                mode='poll',
            ),
            models.CreateResponse(
                status=400, error_code='DEFERRED_APPLY_MODE_ERROR',
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api',
                change_doc_id='235',
            ),
            models.CreateResponse(status=409, error_code='EXISTED_DRAFT'),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api',
                change_doc_id='230',
            ),
            models.CreateResponse(status=409, error_code='EXISTED_DRAFT'),
        ),
        (
            models.CreateTestCase(
                summon_users=['test_login', 'not_expected'],
                lock_ids_from_check=[
                    {'custom': False, 'id': 'lock_id_3'},
                    {'custom': True, 'id': 'test_service:test_api:lock_id_4'},
                ],
                route_headers={
                    'X-YaTaxi-Draft-Author': 'test_login',
                    'X-YaTaxi-Draft-RunType': 'manually',
                    'X-YaTaxi-Draft-Service-Name': 'test_service',
                    'X-YaTaxi-Draft-Api-Path': 'test_api',
                },
            ),
            models.CreateResponse(
                status=200,
                comments=_create_comments(
                    not_found_logins=['not_expected', 'test_login'],
                ),
                summoned_users=[],
                headers={},
                attached_tickets=[],
            ),
        ),
        (
            models.CreateTestCase(
                summon_users=['test_login', 'not_expected'],
                lock_ids_from_check=[
                    {'custom': False, 'id': 'lock_id_2'},
                    {'custom': False, 'id': 'lock_id_3'},
                ],
            ),
            models.CreateResponse(status=409, error_code='EXISTED_LOCK'),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api2',
                route_params={'tplatform_namespace': 'market'},
                change_doc_id='doc_id',
                attach_tickets={
                    'existed': ['TAXIRATE-35', 'TAXIRATE-36', 'TAXIRATE-38'],
                    'create_data': {
                        'summary': 'test_summary',
                        'description': 'test_description',
                    },
                },
                route_headers={
                    'X-YaTaxi-Draft-Author': 'test_login',
                    'X-YaTaxi-Draft-RunType': 'manually',
                    'X-YaTaxi-Draft-Tickets': (
                        'TAXIRATE-35,TAXIRATE-36,TAXIRATE-38'
                    ),
                    'X-YaTaxi-Ticket': 'TAXIRATE-35',
                    'X-YaTaxi-Draft-Service-Name': 'test_service',
                    'X-YaTaxi-Draft-Api-Path': 'test_api2',
                },
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_api2',
                tplatform_namespace='market',
                expected_change_doc_id='test_service_doc_id',
                attached_tickets=[
                    'TAXIRATE-35',
                    'TAXIRATE-36',
                    'TAXIRATE-38',
                    'RUPRICING-100',
                ],
                comments=_create_comments(
                    existed_tickets=[
                        'TAXIRATE-35',
                        'TAXIRATE-36',
                        'TAXIRATE-38',
                    ],
                    new_ticket='RUPRICING-100',
                ),
                headers={},
                version=3,
                query_params={'tplatform_namespace': 'market'},
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api_route_options',
                change_doc_id='doc_id',
                attach_tickets={
                    'existed': ['TAXIRATE-35', 'TAXIRATE-36', 'TAXIRATE-38'],
                    'create_data': {
                        'summary': 'test_summary',
                        'description': 'test_description',
                    },
                },
                route_method='GET',
                route_headers={
                    'x-test-header': 'value',
                    'X-YaTaxi-Draft-Author': 'test_login',
                    'X-YaTaxi-Draft-RunType': 'manually',
                    'X-YaTaxi-Draft-Tickets': (
                        'TAXIRATE-35,TAXIRATE-36,TAXIRATE-38'
                    ),
                    'X-YaTaxi-Draft-Service-Name': 'test_service',
                    'X-YaTaxi-Draft-Api-Path': 'test_api_route_options',
                },
                route_params={'zone': 'moscow', 'mode': 'create'},
            ),
            models.CreateResponse(
                status=200,
                version=3,
                service_name='test_service',
                api_path='test_api_route_options',
                expected_change_doc_id='test_service_doc_id',
                attached_tickets=[
                    'TAXIRATE-35',
                    'TAXIRATE-36',
                    'TAXIRATE-38',
                    'RUPRICING-100',
                ],
                comments=_create_comments(
                    existed_tickets=[
                        'TAXIRATE-35',
                        'TAXIRATE-36',
                        'TAXIRATE-38',
                    ],
                    new_ticket='RUPRICING-100',
                ),
                headers={'x-test-header': 'value'},
                query_params={'mode': 'create', 'zone': 'moscow'},
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api',
                change_doc_id='test_doc_id',
                check_mode='poll',
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_api',
                expected_change_doc_id='test_doc_id',
                attached_tickets=[],
                mode='poll',
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api',
                change_doc_id='test_doc_id',
                check_mode='poll',
                deferred_apply='2018-01-01T12:00:00+02:00',
            ),
            models.CreateResponse(
                status=400, error_code='DEFERRED_APPLY_MANUALLY_ERROR',
            ),
        ),
        (
            models.CreateTestCase(
                summon_users=['test_login', 'not_expected'],
                lock_ids_from_check=[
                    {'custom': False, 'id': 'lock_id_3'},
                    {'custom': True, 'id': 'test_service:test_api:lock_id_4'},
                ],
                route_headers={
                    'X-YaTaxi-Draft-Author': 'test_login',
                    'X-YaTaxi-Draft-RunType': 'manually',
                    'X-YaTaxi-Draft-Service-Name': 'test_service',
                    'X-YaTaxi-Draft-Api-Path': 'test_api',
                },
                data=' is not dict ',  # type: ignore
            ),
            models.CreateResponse(status=400, error_code='CHECK_TYPE_ERROR'),
        ),
        (
            models.CreateTestCase(
                change_doc_id='custom_filter1:custom_filter2:test_doc_id',
            ),
            models.CreateResponse(
                status=200,
                expected_change_doc_id=(
                    'custom_filter1:custom_filter2:test_doc_id'
                ),
                attached_tickets=[],
            ),
        ),
        (
            models.CreateTestCase(
                date_expired='2021-01-01T12:00:00+02:00',
                service_name='test_service',
                api_path='test_api',
                change_doc_id='test_doc_id',
                mode='poll',
            ),
            models.CreateResponse(
                status=200,
                expected_change_doc_id='test_doc_id',
                attached_tickets=[],
                date_expired='2021-01-01T13:00:00+0300',
                mode='poll',
            ),
        ),
        (
            models.CreateTestCase(
                date_expired='2000-01-01T12:00:00+02:00',
                service_name='test_service',
                api_path='test_api',
                change_doc_id='test_doc_id',
            ),
            models.CreateResponse(
                status=400, error_code='DATE_EXPIRED_TIME_ERROR',
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_no_default',
                api_path='test_api',
                summon_users=['test_manager', 'test_developer'],
                data=dict(managers=True, developers=True),
            ),
            models.CreateResponse(status=409, error_code='SCHEME_ERROR'),
        ),
        (
            models.CreateTestCase(
                service_name='test_all_default',
                api_path='test_api',
                summon_users=['test_manager', 'test_developer'],
                data=dict(managers=True, developers=True),
            ),
            models.CreateResponse(status=409, error_code='SCHEME_ERROR'),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_audit_as_default',
                summon_users=['test_manager', 'test_developer'],
                data=dict(developers=True),
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_audit_as_default',
                comments=_create_comments(not_found_logins=['test_developer']),
                summoned_users=_create_summoned_users(['test_manager']),
                data={'developers': True},
                attached_tickets=[],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_audit_as_default',
                summon_users=['test_manager', 'test_developer'],
                data=dict(managers=True),
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_audit_as_default',
                comments=[],
                summoned_users=_create_summoned_users(
                    ['test_developer', 'test_manager'],
                ),
                data={'managers': True},
                attached_tickets=[],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_all_audit',
                summon_users=['test_manager', 'test_developer'],
                data=dict(managers=True),
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_all_audit',
                comments=[],
                summoned_users=_create_summoned_users(
                    ['test_developer', 'test_manager'],
                ),
                data={'managers': True},
                attached_tickets=[],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_several_groups',
                summon_users=['test_manager', 'test_developer'],
                data=dict(managers=True, developers=True),
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_several_groups',
                comments=_create_comments(not_found_logins=['test_manager']),
                summoned_users=_create_summoned_users(['test_developer']),
                data={'developers': True, 'managers': True},
                attached_tickets=[],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_several_groups',
                summon_users=['test_manager', 'test_developer'],
                data=dict(managers=True),
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_several_groups',
                comments=_create_comments(not_found_logins=['test_manager']),
                summoned_users=_create_summoned_users(['test_developer']),
                data={'managers': True},
                attached_tickets=[],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_route_several_groups',
                summon_users=['test_manager', 'test_developer'],
                data=dict(unknown_group=True),
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_route_several_groups',
                comments=_create_comments(),
                summoned_users=_create_summoned_users(
                    ['test_developer', 'test_manager'],
                ),
                data={'unknown_group': True},
                attached_tickets=[],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='good_service',
                api_path='test_api',
                is_platform=True,
            ),
            models.CreateResponse(
                status=200,
                service_name='good_service',
                api_path='test_api',
                scheme_type=taxi_models.SchemeType.PLATFORM,
                attached_tickets=[],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='bank_service',
                api_path='bank_test_api',
                is_bank=True,
            ),
            models.CreateResponse(
                status=200,
                service_name='bank_service',
                api_path='bank_test_api',
                scheme_type=taxi_models.SchemeType.BANK,
                attached_tickets=[],
            ),
        ),
        (
            models.CreateTestCase(
                service_name='bank_service_configs',
                api_path='bank_test_api_configs',
                is_bank=True,
                route_params={'name': 'BANK_CONFIG'},
            ),
            models.CreateResponse(
                status=200,
                service_name='bank_service_configs',
                api_path='bank_test_api_configs',
                scheme_type=taxi_models.SchemeType.BANK,
                attached_tickets=[],
                query_params={'name': 'BANK_CONFIG'},
            ),
        ),
        (
            models.CreateTestCase(
                service_name='wfm_service',
                api_path='test_api',
                is_wfm_effrat=True,
                extra_headers={'X-Yandex-Uid': 'test_login'},
            ),
            models.CreateResponse(
                status=200,
                service_name='wfm_service',
                api_path='test_api',
                scheme_type=taxi_models.SchemeType.WFM_EFFRAT,
                attached_tickets=[],
                headers={'X-Yandex-Uid': 'test_login'},
            ),
        ),
        (
            models.CreateTestCase(
                service_name='bad_permissions',
                api_path='test_api',
                is_platform=True,
            ),
            models.CreateResponse(status=409, error_code='SCHEME_ERROR'),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api',
                check_tplatform_namespace='market',
            ),
            models.CreateResponse(
                status=200,
                service_name='test_service',
                api_path='test_api',
                attached_tickets=[],
                tplatform_namespace='market',
            ),
        ),
        (
            models.CreateTestCase(
                service_name='test_service',
                api_path='test_api',
                route_params={'tplatform_namespace': 'eda'},
                check_tplatform_namespace='market',
            ),
            models.CreateResponse(
                status=400, error_code='TPLATFORM_NAMESPACE_BAD_OVERRIDE',
            ),
        ),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_create_draft(
        case,
        response_case,
        patch,
        taxi_approvals_client,
        check_route_mock,
        create_reports_mock,
):
    check_route_mock(
        change_doc_id=case.change_doc_id,
        lock_ids=case.lock_ids_from_check,
        route_method=case.route_method,
        route_headers=case.route_headers,
        route_params=case.route_params,
        tickets=case.ticket_data_from_check,
        summon_users=case.summon_users_from_check,
        mode=case.check_mode,
        data=case.data,
        description='description from service answer',
        tplatform_namespace=case.check_tplatform_namespace,
    )
    summary = {}
    create_reports_mock(
        25,
        summary,
        response_case.service_name,
        response_case.api_path,
        response_case.attached_tickets,
        tplatform_namespace=response_case.tplatform_namespace,
    )

    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    @patch('taxi_approvals.internal.check_draft._render_summary')
    def _render_summary(diff):
        return {}

    headers = {headers_module.X_YANDEX_LOGIN: 'test_login'}
    if case.extra_headers:
        headers.update(case.extra_headers)
    if case.route_headers:
        headers.update(case.route_headers)
    if case.is_platform:
        headers[headers_module.X_MULTISERVICES_PLATFORM] = 'true'
    if case.is_bank:
        headers[headers_module.X_DRAFT_SCHEME_TYPE] = 'bank'
    if case.is_wfm_effrat:
        headers[headers_module.X_DRAFT_SCHEME_TYPE] = 'wfm_effrat'

    request_data = None
    if case.data and isinstance(case.data, dict):
        request_data = case.data

    response = await taxi_approvals_client.post(
        '/drafts/create/',
        json=case.request_data(request_data),
        headers=headers,
        params=case.route_params,
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


@pytest.mark.parametrize(
    'err_status,err_msg,err_json',
    [
        pytest.param(
            400,
            'So Long, and Thanks for all the Fish!',
            {'details': 'DON\'T PANIC!', 'code': 'DONT_PANIC'},
            id='invalid syntax error',
        ),
        pytest.param(
            400,
            'Смотря какой fabric, смотря сколько details',
            {
                'details': {'key': 'value', 'one_more_key': 2},
                'code': 'OBJECT_DETAILS',
            },
            id='test details as an object',
        ),
        pytest.param(
            500,
            'This text won\'t be changed',
            {'details': 'service have same problems', 'code': 'SOME_PROBLEM'},
            id='internal server error',
        ),
        pytest.param(
            502, 'Bad Gateway', {'details': 'details'}, id='bad gateway error',
        ),
    ],
)
@pytest.mark.config(EXTERNAL_RETRY_INTERVAL=0)
@pytest.mark.pgsql('approvals', files=['data.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_create_draft_ext_err(
        err_status,
        err_msg,
        err_json,
        taxi_approvals_client,
        check_route_err_mock,
):
    check_route_err_mock(
        err_status=err_status, err_msg=err_msg, err_json=err_json,
    )

    case = models.CreateTestCase(
        service_name='test_service',
        api_path='test_api',
        change_doc_id='test_doc_id',
        attach_tickets={'existed': ['TAXIRATE-35']},
        lock_ids_from_check=[],
        deferred_apply='2018-01-01T12:00:00+02:00',
        run_manually=False,
    )
    response = await taxi_approvals_client.post(
        '/drafts/create/',
        json=case.request_data(),
        headers={
            'X-Yandex-Login': 'test_login',
            'X-YaTaxi-Ticket': 'TAXIRATE-35',
        },
    )
    assert err_status == response.status
    content = await response.json()
    assert err_msg == content['message']
    assert err_json.get('details') == content.get('details')
    assert err_json.get('code', 'CHECK_FAILED') == content.get('code')


async def test_create_draft_403_response(taxi_approvals_client):
    case = models.CreateTestCase(attach_tickets={'existed': ['TAXIREL-1']})
    response = await taxi_approvals_client.post(
        '/drafts/create/',
        json=case.request_data(),
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 403
    content = await response.json()
    assert content['status'] == 'error'
    assert content['message'] == (
        'Cannot get ticket. StarTrack permission error: '
        'Access to issues/TAXIREL-1 is forbidden. '
        'Add robot-taxi@ to the queue administrators.'
    )
    assert content['code'] == 'PERMISSIONS_ERROR'


async def test_create_draft_with_empty_check_result(
        taxi_approvals_client, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session('http://unstable-host/check/route', 'post')
    def patch_admin(url, method, *args, **kwargs):
        return response_mock()

    case = models.CreateTestCase()
    response = await taxi_approvals_client.post(
        '/drafts/create/',
        json=case.request_data(),
        headers={
            'X-Yandex-Login': 'test_login',
            'X-YaTaxi-Ticket': 'TAXIRATE-35',
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content.get('message') == 'Check result is empty'
    assert content.get('code') == 'CHECK_FORMAT_ERROR'
    assert len(patch_admin.calls) == 1
