import pytest

from tests_cargo_crm import const

STAGES_INIT = {
    'pipedrive_account': {'deal_id': 1, 'org_id': 1, 'person_id': 1},
    'phoenix_ticket_updates': [
        {'phoenix_step': 'initial_form', 'phoenix_event_id': '0sdsdsd'},
    ],
}

STAGES_COMPANY_INFO = {
    'pipedrive_account': {'deal_id': 1, 'org_id': 1, 'person_id': 1},
    'phoenix_ticket_updates': [
        {'phoenix_step': 'company_info_form', 'phoenix_event_id': 'iddqd'},
    ],
}

STAGES_CARD_CONFIRMED = {
    'pipedrive_account': {'deal_id': 1, 'org_id': 1, 'person_id': 1},
    'phoenix_ticket_updates': [
        {'phoenix_step': 'card_bound_form', 'phoenix_event_id': 'idkfa'},
    ],
}

STAGES_MULTIPLE = {
    'pipedrive_account': {'deal_id': 1, 'org_id': 1, 'person_id': 1},
    'phoenix_ticket_updates': [
        {'phoenix_step': 'initial_form', 'phoenix_event_id': '0sdsdsd'},
        {
            'phoenix_step': 'company_created_form',
            'phoenix_event_id': '2sdsdsssddsd',
        },
        {'phoenix_step': 'company_info_form', 'phoenix_event_id': 'iddqd'},
        {'phoenix_step': 'card_bound_form', 'phoenix_event_id': 'idkfa'},
    ],
}


@pytest.fixture(name='proxy_handler_get_events')
def _proxy_handler_get_events(mockserver, procaas_ctx):
    @mockserver.json_handler('/cargo-crm/procaas/caching-proxy/events')
    def handler(request):
        scope = request.query['scope'][0]
        queue = request.query['queue'][0]
        procaas_ctx.events = [
            {
                'event_id': 'ev_1',
                'created': '2021-06-20T10:00:00+00:00',
                'payload': {
                    'kind': 'initial_form_request',
                    'data': {
                        'operation_id': 'opid_1',
                        'revision': 0,
                        'requester_uid': const.UID,
                        'requester_login': const.LOGIN,
                        'form_data': {
                            'contact_phone': '+79002222220',
                            'utm_parameters': {'utm_source': 'tlmk'},
                        },
                        'form_pd': {'contact_phone_pd_id': const.PHONE_PD_ID},
                    },
                },
            },
            {
                'event_id': 'ev_2',
                'created': '2021-06-20T10:00:01+00:00',
                'payload': {
                    'kind': 'initial_form_result',
                    'data': {'operation_id': 'opid_1'},
                },
            },
            {
                'event_id': 'ev_5',
                'created': '2021-06-20T10:02:00+00:00',
                'payload': {
                    'kind': 'company_created_notification',
                    'data': {
                        'form_data': {'corp_client_id': const.CORP_CLIENT_ID},
                        'form_pd': {},
                    },
                },
            },
            {
                'event_id': 'ev_6',
                'created': '2021-06-20T10:03:00+00:00',
                'payload': {
                    'kind': 'company_info_form_request',
                    'data': {
                        'operation_id': 'opid_6',
                        'revision': 2,
                        'requester_uid': const.UID,
                        'requester_login': const.LOGIN,
                        'form_data': {
                            'name': 'Camomile Ltd.',
                            'country': 'Россия',
                            'segment': 'Аптеки',
                            'city': 'Москва',
                            'email': '',
                            'phone': '',
                            'website': 'camomile.ru',
                            'value': 100,
                        },
                        'form_pd': {
                            'phone_pd_id': const.PHONE_PD_ID,
                            'email_pd_id': const.EMAIL_PD_ID,
                        },
                    },
                },
            },
            {
                'event_id': 'ev_7',
                'created': '2021-06-20T10:03:01+00:00',
                'payload': {
                    'kind': 'company_info_form_result',
                    'data': {'operation_id': 'opid_6'},
                },
            },
            {
                'event_id': 'ev_8',
                'created': '2021-06-20T10:04:00+00:00',
                'payload': {
                    'kind': 'card_bound_notification',
                    'data': {
                        'form_data': {
                            'corp_client_id': const.CORP_CLIENT_ID,
                            'yandex_uid': const.UID,
                            'card_id': const.CARD_ID,
                        },
                        'form_pd': {},
                    },
                },
            },
        ]
        return procaas_ctx.get_read_events_response(request, scope, queue)

    return handler


@pytest.mark.parametrize(
    'pipedrive_code, expected_code, stages',
    (
        (200, 200, STAGES_INIT),
        (200, 200, STAGES_COMPANY_INFO),
        (200, 200, STAGES_CARD_CONFIRMED),
        (200, 200, STAGES_MULTIPLE),
        (500, 500, STAGES_INIT),
        (404, 410, STAGES_INIT),
    ),
)
async def test_func_update_account(
        taxi_cargo_crm,
        mockserver,
        pipedrive_code,
        expected_code,
        stages,
        proxy_handler_get_events,
        happy_path_events,
        load_json,
):
    @mockserver.json_handler('pipedrive-api/v1/organizations/1')
    def _handler_o(request):
        body = None
        if pipedrive_code == 200:
            body = load_json('../test_phoenixpipe_create_account/org.json')
        elif pipedrive_code == 404:
            body = load_json('404.json')
        return mockserver.make_response(status=pipedrive_code, json=body)

    @mockserver.json_handler('pipedrive-api/v1/deals/1')
    def _handler_d(request):
        body = None
        if pipedrive_code == 200:
            body = load_json('../test_phoenixpipe_create_account/deal.json')
        elif pipedrive_code == 404:
            body = load_json('404.json')
        return mockserver.make_response(status=pipedrive_code, json=body)

    @mockserver.json_handler('pipedrive-api/v1/persons/1')
    def _handler_p(request):
        body = None
        assert request.json == {
            'id': 1,
            'phone': [{'label': 'work', 'primary': True, 'value': '+790'}],
            'email': [
                {
                    'label': 'work',
                    'primary': True,
                    'value': 'odinn@walholl.as',
                },
            ],
        }
        if pipedrive_code == 200:
            body = load_json('../test_phoenixpipe_create_account/person.json')
        elif pipedrive_code == 404:
            body = load_json('404.json')
        return mockserver.make_response(status=pipedrive_code, json=body)

    @mockserver.json_handler('pipedrive-api/v1/notes')
    def _handler_n(request):
        body = load_json('../test_phoenixpipe_create_account/note.json')
        return mockserver.make_response(status=201, json=body)

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _handler_ph(request):
        return mockserver.make_response(
            status=200,
            json={
                'items': [
                    {'id': '997722', 'value': '+790'},
                    {'id': 'random_id_2', 'value': '+70001112233'},
                ],
            },
        )

    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def _handler_em(request):
        return mockserver.make_response(
            status=200,
            json={
                'items': [
                    {'id': '13371337', 'value': 'odinn@walholl.as'},
                    {'id': 'random_id_2', 'value': 'tor@walholl.as'},
                ],
            },
        )

    response = await taxi_cargo_crm.post(
        '/internal/cargo-crm/flow/phoenixpipe/ticket/update-client-card',
        params={'ticket_id': const.TICKET_ID},
        json={
            'pipedrive_account': {'deal_id': 1, 'org_id': 1, 'person_id': 1},
            'phoenix_ticket_updates': [
                {
                    'phoenix_step': 'initial_form',
                    'phoenix_event_id': '0sdsdsd',
                },
                {
                    'phoenix_step': 'company_created_form',
                    'phoenix_event_id': '2sdsdsssddsd',
                },
                {
                    'phoenix_step': 'company_info_form',
                    'phoenix_event_id': 'sdfsff',
                },
            ],
        },
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {}
