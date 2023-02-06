import pytest

from tests_cargo_crm import const


DEFAULT_403_BODY = {
    'success': False,
    'error': 'Insufficient visibility to the associated deal',
    'error_info': (
        'Please check developers.pipedrive.com '
        'for more information about Pipedrive API.'
    ),
    'data': None,
    'additional_data': None,
}

FULL_HAPPY_PATH = [
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
                'form_data': {'contact_phone': '+79002222220'},
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


async def test_func_create_trigger_activity_bad_stage(
        taxi_cargo_crm, mockserver, load_json,
):
    @mockserver.json_handler('pipedrive-api/v1/activities')
    def _handler(request):
        body = load_json('activity.json')
        return mockserver.make_response(status=201, json=body)

    @mockserver.json_handler('cargo-crm/procaas/caching-proxy/events')
    def _handler2(request):
        body = {'events': FULL_HAPPY_PATH}
        return mockserver.make_response(status=200, json=body)

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _handler3(request):
        return mockserver.make_response(status=200, json={'items': []})

    response = await taxi_cargo_crm.post(
        '/internal/cargo-crm/flow/phoenixpipe/'
        'ticket/set-task-on-call-to-client',
        params={'ticket_id': const.TICKET_ID},
        json={
            'pipedrive_account': {'deal_id': 1, 'org_id': 1, 'person_id': 1},
        },
    )
    assert response.status_code == 410


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
                        'form_data': {'contact_phone': ''},
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
        ]
        return procaas_ctx.get_read_events_response(request, scope, queue)

    return handler


@pytest.mark.parametrize(
    'pipedrive_code, expected_code', ((201, 200), (500, 500), (403, 410)),
)
async def test_func_create_trigger_activity(
        taxi_cargo_crm,
        mockserver,
        pipedrive_code,
        expected_code,
        proxy_handler_get_events,
        happy_path_events,
        load_json,
):
    @mockserver.json_handler('pipedrive-api/v1/activities')
    def _handler(request):
        body = None
        if pipedrive_code == 201:
            body = load_json('activity.json')
        elif pipedrive_code == 403:
            body = DEFAULT_403_BODY
        return mockserver.make_response(status=pipedrive_code, json=body)

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _handler2(request):
        return mockserver.make_response(status=200, json={'items': []})

    response = await taxi_cargo_crm.post(
        '/internal/cargo-crm/flow/phoenixpipe/'
        'ticket/set-task-on-call-to-client',
        params={'ticket_id': const.TICKET_ID},
        json={
            'pipedrive_account': {'deal_id': 1, 'org_id': 1, 'person_id': 1},
        },
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {'pipedrive_activity_id': 1}
