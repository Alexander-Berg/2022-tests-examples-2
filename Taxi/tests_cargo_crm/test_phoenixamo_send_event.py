import pytest

from tests_cargo_crm import const


EVENT_OK_BODY = {
    'external_event_id': 'phoenix:97ad59d2e0834e38a5c9a4e9949f6a41',
    'details': {
        'company_name': 'Camomile Ltd.',
        'contact_last_name': 'Smith',
        'ticket_state': 'card_bound',
        'contact_phone': '+790',
        'contact_first_name': 'John',
        'company_utm_source': 'tlmk',
        'lead_corp_client_id': 'corp1',
        'lead_potential': None,
        'company_city': 'Москва',
        'company_country': 'Россия',
        'company_industry': 'Аптеки',
        'contact_mail': 'odinn@walholl.as',
    },
}

EVENT_OK_RESPONSE = {'id': 'amo_object_id'}

EVENT_FAIL_RESPONSE = {'code': 'error', 'message': 'am error'}


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
                            'name': 'John',
                            'surname': 'Smith',
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


@pytest.mark.parametrize('amo_code, expected_code', ((200, 200), (400, 200)))
async def test_phoenixamo_send_event(
        taxi_cargo_crm,
        mockserver,
        amo_code,
        expected_code,
        proxy_handler_get_events,
        load_json,
        personal_ctx,
        personal_handler_bulk_retrieve,
        amo_lead_event_set_response,
        amo_lead_event_response,
):
    personal_ctx.set_phones(
        [
            {'id': '997722', 'value': '+790'},
            {'id': 'random_id_2', 'value': '+70001112233'},
        ],
    )
    personal_ctx.set_emails(
        [
            {'id': '13371337', 'value': 'odinn@walholl.as'},
            {'id': 'random_id_2', 'value': 'tor@walholl.as'},
        ],
    )

    if expected_code == 200:
        amo_lead_event_set_response.set_response(
            expected_code, EVENT_OK_BODY, EVENT_OK_RESPONSE,
        )
    else:
        amo_lead_event_set_response.set_response(
            expected_code, {}, EVENT_FAIL_RESPONSE,
        )

    response = await taxi_cargo_crm.post(
        '/internal/cargo-crm/flow/phoenixamo/'
        'ticket/notify-phoenix-ticket-updated',
        params={'ticket_id': 'phoenix:97ad59d2e0834e38a5c9a4e9949f6a41'},
        json={
            'phoenix_step_passed': 'initial_form',
            'phoenix_event_id': '97ad59d2e0834e38a5c9a4e9949f6a41',
        },
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {}
