import json

import pytest

NOTIFICATION_RESOLUTION_CURATOR_FAIL = {
    'resolution': {
        'caused_by': 'manager:event_id:db94820f42bb473d8f239bde3f73b7a1',
        'fail_reason': {
            'code': 'curator_reject',
            'details': {
                'curator_action': {
                    'is_approved': False,
                    'login': 'dipterix',
                    'reason': 'Не понял про что речь. В личку!',
                    'uid': '1120000000187371',
                },
            },
            'message': 'Ticket have been rejected by curator',
        },
    },
}

NOTIFICATION_RESOLUTION_AUTOCHECK_FAIL = {
    'resolution': {
        'caused_by': 'manager:event_id:c7713377f68f4741afedec0a3e29eb9f',
        'fail_reason': {
            'code': 'invalid_data',
            'details': {'invalid_email': 'Invalid email'},
            'message': 'Some data is invalid.',
        },
    },
}

CURATOR_FAIL = (
    'Ticket have been rejected by curator: Не понял про что речь. В личку!'
)


def expected_sf_request(event_message=None, event_code='resolution'):
    result = {
        'event_code': event_code,
        'ticket_id': 'ticket_id',
        'manager_request_data': {'manager': {'login': 'voytekh'}},
        'company_info_form': {'name': 'Beloved Client'},
        'offer_info_form': {'name': 'Beloved Offered Client'},
    }

    if event_message is not None:
        result['event_message'] = event_message

    return result


class TestNotifyExternalCrm:
    @pytest.mark.parametrize(
        'request_json,expected_request',
        (
            pytest.param(
                {'event_kind': 'no_notify', 'notification_data': {}},
                None,
                id='no_notify_ok',
            ),
            pytest.param(
                {'event_kind': 'resolution', 'notification_data': {}},
                expected_sf_request(),
                id='resolution_ok',
            ),
            pytest.param(
                {
                    'event_kind': 'resolution',
                    'notification_data': NOTIFICATION_RESOLUTION_CURATOR_FAIL,
                },
                expected_sf_request(CURATOR_FAIL),
                id='resolution_fail_on_curator',
            ),
            pytest.param(
                {
                    'event_kind': 'resolution',
                    'notification_data': (
                        NOTIFICATION_RESOLUTION_AUTOCHECK_FAIL
                    ),
                },
                expected_sf_request('Some data is invalid.'),
                id='resolution_fail_on_autocheck',
            ),
            pytest.param(
                {
                    'event_kind': 'autocheck_passed_notification',
                    'notification_data': {},
                },
                expected_sf_request(
                    event_code='autocheck_passed_notification',
                ),
                id='autocheck_passed_ok',
            ),
        ),
    )
    async def test_notify_external_crm(
            self,
            mockserver,
            request_notify_external_crm,
            create_context_record,
            request_json,
            expected_request,
    ):
        @mockserver.json_handler(
            '/cargo-sf/internal/cargo-sf/internal-requests/'
            'accept-manager-request-notification',
        )
        def _reg_handler(request):
            assert request.json == expected_request
            return mockserver.make_response(status=200)

        response = await request_notify_external_crm(request_json)
        if expected_request:
            assert _reg_handler.times_called == 1
        else:
            assert _reg_handler.times_called == 0
        assert response.status_code == 200

    async def test_notify_external_crm_by_raw(
            self, mockserver, request_notify_external_crm, create_raw_record,
    ):
        @mockserver.json_handler(
            '/cargo-sf/internal/cargo-sf/internal-requests/'
            'accept-manager-request-notification',
        )
        def _reg_handler(request):
            assert request.json == expected_sf_request('Some data is invalid.')
            return mockserver.make_response(status=200)

        request_json = {
            'event_kind': 'resolution',
            'notification_data': NOTIFICATION_RESOLUTION_AUTOCHECK_FAIL,
        }
        response = await request_notify_external_crm(request_json)
        assert _reg_handler.times_called == 1
        assert response.status_code == 200


@pytest.fixture(name='request_notify_external_crm')
def _request_notify_external_crm(taxi_cargo_crm):
    async def wrapper(request_json):
        url = '/functions/by-flow/notify-external-crm'

        response = await taxi_cargo_crm.post(
            url,
            params={'ticket_id': 'ticket_id', 'flow': 'manager'},
            json=request_json,
        )
        return response

    return wrapper


@pytest.fixture(name='create_context_record')
def _create_context_record(pgsql):
    cursor = pgsql['cargo_crm'].conn.cursor()

    cursor.execute(
        f"""
INSERT INTO
    cargo_crm_manager.tickets_data
        (ticket_id, ticket_data)
VALUES ('ticket_id',
'{{"manager_info_form": {{"manager": {{"login": "voytekh"}} }},
"company_info_form": {{"name": "Beloved Client", "country": "isr"}},
"offer_info_form": {{"name": "Beloved Offered Client"}},
"company_info_pd_form": {{}},
"contract_traits_form": {{"kind": "offer", "type": "prepaid"}} }}')""",
    )
    cursor.close()


@pytest.fixture(name='create_raw_record')
def _create_raw_record(pgsql):
    cursor = pgsql['cargo_crm'].conn.cursor()

    form = {
        'manager_info_form': {
            'manager': {'login': 'voytekh'},
            'crm': {'lead_id': ''},
            'legal': {'st_ticket': ''},
        },
        'company_info_form': {'name': 'Beloved Client', 'country': 'isr'},
        'offer_info_form': {'name': 'Beloved Offered Client'},
        'contract_traits_form': {'kind': 'offer', 'type': 'prepaid'},
    }

    cursor.execute(
        f"""
INSERT INTO
    cargo_crm_manager.tickets_raw_data
        (ticket_id, ticket_raw_data)
VALUES ('ticket_id','{json.dumps(form)}')""",
    )
    cursor.close()
