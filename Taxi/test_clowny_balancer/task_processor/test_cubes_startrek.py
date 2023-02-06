import pytest

DESC = """Надо прописать следующие домены в днс для сертификата cert1:
* fqdn1
* fqdn2
"""
DESC2 = 'Привет, нужны ip-адреса для внешнего балансера test-balancer.net.'


@pytest.mark.parametrize(
    'preparer_name, input_data, st_request, create_payload',
    [
        (
            'StartrekGenerateDutyTicketParamsForSsl',
            {'author': 'd1mbas', 'namespace_id': 'ns1', 'cert_id': 'cert1'},
            {
                'components': [74933],
                'followers': ['d1mbas'],
                'queue': {'key': 'TAXIADMIN'},
                'summary': 'Прописать домены в днс для сертификата cert1',
                'type': {'key': 'task'},
                'unique': 'StartrekCreateTicket_0_0',
                'description': DESC,
            },
            {'new_ticket': 'TAXIADMIN-1'},
        ),
        (
            'StartrekGenerateTrafficTicketParamsForExternal',
            {'author': 'd1mbas', 'skip': False, 'l3mgr_service_id': '1'},
            {
                'components': [28072],
                'followers': ['d1mbas'],
                'queue': {'key': 'TRAFFIC'},
                'summary': 'IP для внешнего балансера test-balancer.net',
                'type': {'key': 'task'},
                'unique': 'StartrekCreateTicket_0_0',
                'description': DESC2,
            },
            {'new_ticket': 'TRAFFIC-1'},
        ),
        (
            'StartrekGenerateTrafficTicketParamsForExternal',
            {'author': 'd1mbas', 'skip': True, 'l3mgr_service_id': '1'},
            None,
            {'new_ticket': ''},
        ),
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_PROJECT_QUEUES={
        '__default__': {'components': [74933], 'queue': 'TAXIADMIN'},
    },
)
async def test_prepare_and_create_ticket(
        mockserver,
        call_cube,
        preparer_name,
        input_data,
        st_request,
        create_payload,
):
    @mockserver.json_handler('/l3mgr/service/1')
    def _l3mgr_service_handler(_):
        return {'fqdn': 'test-balancer.net'}

    @mockserver.json_handler('/client-awacs/api/GetCertificate/')
    def _get_cert_handler(_):
        return {
            'certificate': {
                'meta': {'id': 'cert1'},
                'spec': {
                    'fields': {
                        'subjectCommonName': 'fqdn1',
                        'subjectAlternativeNames': ['fqdn1', 'fqdn2'],
                    },
                },
            },
        }

    @mockserver.json_handler('/startrek/issues')
    def _issues_handler(request):
        assert request.json == st_request
        return {'key': request.json['queue']['key'] + '-1'}

    response = await call_cube(preparer_name, input_data)
    assert response['status'] == 'success'

    response = await call_cube('StartrekCreateTicket', response['payload'])
    assert response['status'] == 'success'
    assert response['payload'] == create_payload
    if not st_request:
        assert _issues_handler.times_called == 0


@pytest.mark.parametrize(
    'name, input_data, payload, extras',
    [
        (
            'StartrekGenerateDutyTicketParamsForSsl',
            {'author': 'd1mbas', 'namespace_id': 'ns1', 'cert_id': 'cert1'},
            {
                'queue': 'TAXIADMIN',
                'components': [74933],
                'followers': ['d1mbas'],
                'title': 'Прописать домены в днс для сертификата cert1',
                'description': DESC,
            },
            None,
        ),
        (
            'StartrekCreateTicket',
            {
                'queue': 'TAXIADMIN',
                'title': 'Прописать домены в днс для сертификата cert1',
                'description': 'aaa',
                'components': [74933],
                'followers': ['d1mbas'],
            },
            {'new_ticket': 'TAXIADMIN-1'},
            None,
        ),
        ('StartrekWaitClosed', {'ticket': 'TAXIADMIN-1'}, None, None),
        (
            'StartrekWaitClosed',
            {'ticket': 'TAXIADMIN-2'},
            None,
            {'status': 'in_progress', 'sleep_duration': 10},
        ),
        (
            'StartrekGenerateCommentAdd443OnL3',
            {'l3mgr_service_id': '123', 'st_ticket': 'TAXIADMIN-1'},
            {
                'border_comment': (
                    'test-balancer.net: 443 added and config deployed'
                ),
            },
            None,
        ),
        (
            'StartrekWaitBorderComment',
            {
                'st_ticket': 'TAXIADMIN-1',
                'border_comment': (
                    'test-balancer.net: 443 added and config deployed'
                ),
            },
            None,
            None,
        ),
        (
            'StartrekGenerateTrafficTicketParamsForExternal',
            {'author': 'd1mbas', 'skip': False, 'l3mgr_service_id': '1'},
            {
                'components': [28072],
                'followers': ['d1mbas'],
                'queue': 'TRAFFIC',
                'title': 'IP для внешнего балансера test-balancer.net',
                'description': DESC2,
            },
            None,
        ),
        (
            'StartrekGenerateTrafficTicketParamsForExternal',
            {'author': 'd1mbas', 'skip': True, 'l3mgr_service_id': '1'},
            {
                'components': [28072],
                'followers': ['d1mbas'],
                'queue': '',
                'title': 'IP для внешнего балансера test-balancer.net',
                'description': DESC2,
            },
            None,
        ),
        (
            'StartrekCubeLinkServiceTickets',
            {'master_ticket': 'TAXIADMIN-1', 'ticket_to_link': 'SECTASK-1'},
            None,
            None,
        ),
        (
            'StartrekCubeLinkServiceTickets',
            {'master_ticket': '', 'ticket_to_link': 'SECTASK-1'},
            None,
            None,
        ),
        (
            'StartrekCubeLinkServiceTickets',
            {'master_ticket': 'TAXIADMIN-1', 'ticket_to_link': ''},
            None,
            None,
        ),
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_PROJECT_QUEUES={
        '__default__': {'components': [74933], 'queue': 'TAXIADMIN'},
    },
)
async def test_cubes(mockserver, call_cube, name, input_data, payload, extras):
    @mockserver.json_handler(r'/l3mgr/service/(?P<service_id>\d+)', regex=True)
    def _l3mgr_service_handler(_, service_id):
        return {'id': service_id, 'fqdn': 'test-balancer.net'}

    @mockserver.json_handler('/client-awacs/api/GetCertificate/')
    def _get_cert_handler(_):
        return {
            'certificate': {
                'meta': {'id': 'cert1'},
                'spec': {
                    'fields': {
                        'subjectCommonName': 'fqdn1',
                        'subjectAlternativeNames': ['fqdn1', 'fqdn2'],
                    },
                },
            },
        }

    @mockserver.json_handler('/startrek/issues')
    def _crete_issues_handler(request):
        return {'key': request.json['queue']['key'] + '-1'}

    @mockserver.json_handler(
        r'/startrek/issues/(?P<ticket>[\w-]+)', regex=True,
    )
    def _get_issue_handler(_, ticket):
        if ticket == 'TAXIADMIN-1':
            return {'status': {'key': 'closed'}}
        return {'status': {'key': 'opened'}}

    @mockserver.json_handler('/startrek/issues/TAXIADMIN-1/comments')
    def _comments_handler(request):
        if request.query.get('id'):
            return []
        return [
            {
                'id': 'id1',
                'createdBy': {'id': 'robot-taxi-clown'},
                'text': 'some robot comment',
                'createdAt': '2020-10-08T13:00:00.000+0000',
            },
            {
                'id': 'id2',
                'createdBy': {'id': 'd1mbas'},
                'text': 'test-balancer.net: 443 added and config deployed',
                'createdAt': '2020-10-08T14:00:00.000+0000',
            },
        ]

    @mockserver.json_handler('/startrek/issues/TAXIADMIN-1/links')
    def _add_link(request):
        assert request.json['issue'] == 'SECTASK-1'
        return {}

    response = await call_cube(name, input_data)
    expected = {'status': 'success'}
    if payload is not None:
        expected['payload'] = payload
    if extras:
        expected.update(extras)
    assert response == expected


@pytest.mark.parametrize(
    'input_st_ticket, payload_st_ticket, ticket_created',
    [
        ('TAXIADMIN-1', 'TAXIADMIN-1', False),
        ('', 'TAXIADMIN-2', True),
        ('TAXIADMIN-3', 'TAXIADMIN-2', True),
    ],
)
async def test_ensure_ticket_cube(
        mockserver,
        call_cube,
        input_st_ticket,
        payload_st_ticket,
        ticket_created,
):
    cube_name = 'StartrekEnsureDutyTicketExists'

    @mockserver.json_handler(
        r'/startrek/issues/(?P<ticket>[\w-]+)', regex=True,
    )
    def _get_issue_handler(_, ticket):
        if ticket == 'TAXIADMIN-1':
            return {'followers': [{'id': 'some'}]}
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/startrek/issues')
    def _create_ticket(request):
        assert request.json == {
            'components': [74933],
            'followers': ['d1mbas'],
            'queue': {'key': 'TAXIADMIN'},
            'summary': 'Добавление ssl для балансера ns1',
            'type': {'key': 'task'},
            'unique': 'StartrekEnsureDutyTicketExists_0_0',
            'description': '\n'.join(
                [
                    (
                        'Тикет для контроля добавления ssl для балансера '
                        '((https://nanny.yandex-team.ru/ui/#/'
                        'awacs/namespaces/list/ns1/show/ ns1)).'
                    ),
                    (
                        'Возможно потребуется ручное вмешательство, '
                        'но это не точно.'
                    ),
                ],
            ),
        }
        return {'key': 'TAXIADMIN-2'}

    response = await call_cube(
        cube_name,
        {
            'st_ticket': input_st_ticket,
            'author': 'd1mbas',
            'awacs_namespace_id': 'ns1',
        },
    )
    assert response == {
        'status': 'success',
        'payload': {'st_ticket': payload_st_ticket},
    }
    assert _create_ticket.times_called == bool(ticket_created)
