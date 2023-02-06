# pylint: disable=wildcard-import, unused-wildcard-import, import-error

import pytest

from bank_communications_plugins import *  # noqa: F403 F401


try:
    import library.python.resource  # noqa: F401
    _IS_ARCADIA = True
except ImportError:
    _IS_ARCADIA = False

if _IS_ARCADIA:
    import logging
    import dataclasses

    @pytest.fixture(autouse=True)
    async def service_logs(taxi_bank_communications):
        levels = {
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'CRITICAL': logging.CRITICAL,
        }

        # Each log record is captured as a dictionary,
        # so we need to turn it back into a string
        def serialize_tskv(row):
            # these two will only lead to data duplication
            skip = {'timestamp', 'level'}

            # reorder keys so that 'text' is always in front
            keys = list(row.keys())
            keys.remove('text')
            keys.insert(0, 'text')

            return '\t'.join([f'{k}={row[k]}' for k in keys if k not in skip])

        async with taxi_bank_communications.capture_logs() as capture:
            # This hack tricks the client into thinking that
            # caches still need to be invalidated on the first call
            # so as not to break tests that depend on this behaviour
            # pylint: disable=protected-access
            taxi_bank_communications._client._state_manager._state = (
                dataclasses.replace(
                    # pylint: disable=protected-access
                    taxi_bank_communications._client._state_manager._state,
                    caches_invalidated=False,
                )
            )

            @capture.subscribe()
            # pylint: disable=unused-variable
            def log(**row):
                logging.log(
                    levels.get(row['level'], logging.DEBUG),
                    serialize_tskv(row),
                )

            yield capture


@pytest.fixture
def bank_service(mockserver):
    class Context:
        def __init__(self):
            self.phone_number_handler = None
            self.send_yasms_handler = None
            self.get_latest_session_handler = None
            self.idempotency_count = -1
            self.allow_unused_text_params = False

    context = Context()

    def make_response_phone_number(buid: str):
        phones = {
            '67754336-d4d1-43c1-aadb-cabd06674ea6': {'phone': '+71234567890'},
            '40054336-d4d1-43c1-aadb-cabd06674ea6': {'phone': '+700000000'},
            '00000000-d4d1-43c1-aadb-cabd06674ea6': {
                'code': '400',
                'message': 'buid not found',
            },
            '22254336-d4d1-43c1-aadb-cabd06674ea6': {'phone': '+71112223344'},
            '024e7db5-9bd6-4f45-a1cd-2a442e15bdc2': {'phone': '+71112223355'},
            '024e7db5-9bd6-4f45-a1cd-2a442e15bdc4': {'phone': '+71112223366'},
        }

        second_attempt = [{'phone': '+q1234'}, {'phone': '+71234567890'}]
        invalid_userinfo_phones = [{'phone': '+q1234'}, {'phone': '12242423'}]

        if buid in (
                '50054336-d4d1-43c1-aadb-cabd06674ea6',
                '02054336-d4d1-43c1-aadb-cabd06674ea6',
        ):
            context.idempotency_count += 1
            return (
                invalid_userinfo_phones[context.idempotency_count]
                if buid == '50054336-d4d1-43c1-aadb-cabd06674ea6'
                else second_attempt[context.idempotency_count]
            )

        return (
            phones[buid]
            if 'code' not in phones[buid]
            else mockserver.make_response(json=phones[buid], status=400)
        )

    def make_response_send_yasms(phone: str):
        responses = {
            '+71112223355': '<doc><message-sent id="127000000003456" /></doc>',
            '+71112223366': '<doc><message-sent id="127000000003456" /></doc>',
            '+71234567890': '<doc><message-sent id="127000000003456" /></doc>',
            '+72223334445': '<doc><message-sent id="127000000004445" /></doc>',
            '+700000000': (
                '<?xml version="1.0" encoding="windows-1251"?>'
                '<doc>'
                '<error>Bad number</error>'
                '<errorcode>BADPHONE</errorcode>'
                '</doc>'
            ),
        }
        for_second_time_responses = [
            (
                '<?xml version="1.0" encoding="windows-1251"?>'
                '<doc>'
                '<error>Internal Error</error>'
                '<errorcode>INTERROR</errorcode>'
                '</doc>'
            ),
            (
                '<?xml version="1.0" encoding="windows-1251"?>'
                '<doc>'
                'message-sent id="127000000003456" />'
                '</doc>'
            ),
        ]
        if phone in ['+71112223344', '+71125456756']:
            context.idempotency_count += 1
            return for_second_time_responses[context.idempotency_count]
        return mockserver.make_response(responses[phone], 200)

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_number',
    )
    def _mock_get_phone_number(request):
        assert request.method == 'POST'
        return make_response_phone_number(request.json.get('buid'))

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_latest_session',
    )
    def _mock_get_latest_session(request):
        assert request.method == 'POST'
        buid = request.json.get('buid')
        base_answer = {
            'session_uuid': '1',
            'status': 'ACTIVE',
            'created_at': '2022-01-01T20:28:58.838783+00:00',
            'updated_at': '2022-02-01T20:28:58.838783+00:00',
            'antifraud_info': {'device_id': 'device_id'},
            'buid': buid,
        }
        test_case_by_buid = {
            'bank_uid': {
                'app_vars': 'platform=android, app_name=sdk_example',
                'locale': 'ru',
            },
            '7948e3a9-623c-4524-a390-9e4264d27a11': {
                'app_vars': 'platform=android, app_name=sdk_example',
                'locale': 'ru',
            },
            '024e7db5-9bd6-4f45-a1cd-2a442e15bdc2': {
                'app_vars': 'platform=android, app_name=bad_sdk',
                'locale': 'ru',
            },
            '024e7db5-9bd6-4f45-a1cd-2a442e15bdc4': {
                'app_vars': 'platform=bad_platform, app_name=sdk_example',
                'locale': 'ru',
            },
        }
        if buid not in test_case_by_buid.keys():
            buid = 'bank_uid'
        base_answer.update(test_case_by_buid[buid])
        return mockserver.make_response(json=base_answer, status=200)

    @mockserver.json_handler('/yasms-client/sendsms')
    def _mock_send_yasms(request):
        assert request.method == 'POST'
        assert request.query['text']
        assert request.query['sender'] == 'test_bank-communications'
        assert request.query['route'] == 'test_bank'
        assert request.query['phone']
        res = request.query.get('allow_unused_text_params', None) is not None
        assert (res ^ context.allow_unused_text_params) is False
        return make_response_send_yasms(request.query['phone'])

    context.send_yasms_handler = _mock_send_yasms
    context.phone_number_handler = _mock_get_phone_number
    context.get_latest_session_handler = _mock_get_latest_session

    return context


@pytest.fixture
def xiva_mock(mockserver):
    @mockserver.json_handler('/xiva/v2/subscribe/app')
    def _mock_subscribe(request):
        assert request.method == 'POST'
        assert request.query.keys() == {
            'app_name',
            'uuid',
            'platform',
            'user',
            'service',
            'app_name',
            'device',
        }
        assert request.get_data().decode() == 'push_token=push_token'
        return mockserver.make_response(
            json={'subscription-id': 'xiva_subscription_id'},
        )

    @mockserver.json_handler('/xiva/v2/send')
    def _mock_send(request):
        assert request.method == 'POST'
        assert request.headers.get('X-DeliveryMode') == 'direct'
        assert request.query.keys() == {'service', 'user', 'event'}

        return mockserver.make_response(headers={'TransitID': 'id'})

    xiva_mock.subscribe_handle = _mock_subscribe
    xiva_mock.send_handle = _mock_send
    return xiva_mock


@pytest.fixture
def access_control_mock(mockserver):
    class Context:
        def __init__(self):
            self.apply_policies_handler = None
            self.http_status_code = 200
            self.handler_path = None

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/bank-access-control/access-control-internal/v1/apply-policies',
    )
    def _apply_policies_handler(request):
        assert request.method == 'POST'
        context.handler_path = request.json['resource_attributes'][
            'handler_path'
        ]
        decision = (
            'PERMIT'
            if request.json['subject_attributes']['jwt'] == 'allow'
            else 'DENY'
        )
        return mockserver.make_response(
            status=context.http_status_code, json={'decision': decision},
        )

    context.apply_policies_handler = _apply_policies_handler
    return context
