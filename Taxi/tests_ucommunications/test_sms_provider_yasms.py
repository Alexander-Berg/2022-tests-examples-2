import pytest

from testsuite.utils import http


async def test_ok(taxi_ucommunications, mockserver, mock_personal, load_json):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    await taxi_ucommunications.invalidate_caches()

    @mockserver.json_handler('/yasms/sendsms', raw_request=True)
    async def _mock_yasms(request):
        post = await request.post()

        assert post['sender'] == 'yango'
        assert post['route'] == 'taxi'
        assert post['phone'] == '+70001112233'
        assert post['text'] == 'Добрый день!'
        assert post['utf8'] == '1'

        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }


@pytest.mark.parametrize(
    'expected_code,yasms_response',
    [
        (502, http.make_response('<doc></doc>', 200)),
        (200, http.make_response('', 500)),
        (
            400,
            http.make_response(
                """
                <doc>
                    <error>Phone is blocked</error>
                    <errorcode>PHONEBLOCKED</errorcode>
                </doc>""",
                200,
            ),
        ),
        (
            400,
            http.make_response(
                """
                    <doc>
                        <error>Text is too large</error>
                        <errorcode>INTERROR</errorcode>
                    </doc>""",
                200,
            ),
        ),
        (
            200,
            http.make_response(
                """
                <doc>
                    <error>SMS limit for this phone is exceeded</error>
                    <errorcode>LIMITEXCEEDED</errorcode>
                </doc>""",
                200,
            ),
        ),
        (
            502,
            http.make_response(
                """
                <doc>
                    <error>Unknown error</error>
                    <errorcode>INTERROR</errorcode>
                </doc>""",
                200,
            ),
        ),
    ],
)
async def test_errors(
        taxi_ucommunications,
        mockserver,
        expected_code,
        yasms_response,
        mock_personal,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/yasms/sendsms')
    def _mock_yasms(request):
        return yasms_response

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': 'greeting',
        },
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'intent,sender,route',
    [('yango', 'yango', 'taxi'), ('auth', 'passport', 'taxiauth')],
)
async def test_routing(
        taxi_ucommunications,
        mockserver,
        intent,
        sender,
        route,
        mock_personal,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/yasms/sendsms', raw_request=True)
    async def _mock_yasms(request):
        post = await request.post()

        assert post['sender'] == sender
        assert post['identity'] == intent
        assert post['route'] == route

        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={'phone': 'deadbeaf', 'text': 'Добрый день!', 'intent': intent},
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }


@pytest.mark.config(
    COMMUNICATIONS_SMS_PROVIDER_SETTINGS={
        'yasms': {'sender_to_route': {'taxi': 'taxiauth', 'yango': 'yango'}},
        'infobip': {'sender_to_alpha_name': {}},
    },
)
@pytest.mark.parametrize(
    'sender,route', [('taxi', 'taxiauth'), ('yango', 'yango')],
)
async def test_send_with_sender(
        taxi_ucommunications,
        mock_personal,
        mockserver,
        sender,
        route,
        load_json,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/yasms/sendsms', raw_request=True)
    async def _mock_yasms(request):
        post = await request.post()
        assert post['route'] == route
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    response = await taxi_ucommunications.post(
        'general/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'sender': sender,
            'intent': 'greeting',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('message_id')
    assert response_json == {
        'code': '200',
        'message': 'OK',
        'content': 'Добрый день!',
        'status': 'sent',
    }


@pytest.mark.parametrize(
    'intent', ['ignore_limit_exceed', 'ignore_limit_exceed_undefined'],
)
async def test_treat_sms_limit_exceed_as_error(
        taxi_ucommunications, mockserver, intent, mock_personal,
):
    @mockserver.json_handler('/yasms/sendsms')
    def _mock_yasms(request):
        return http.make_response(
            """<doc>
            <error>SMS limit for this phone is exceeded</error>
          <errorcode>LIMITEXCEEDED</errorcode>
          </doc>""",
            200,
        )

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': '+70001112233',
            'text': 'Добрый день!',
            'intent': intent,
        },
    )
    assert response.status_code == 429


@pytest.mark.config(
    COMMUNICATIONS_SMS_PROVIDER_SETTINGS={
        'yasms': {
            'sender_to_tvm_source_service': {
                'taxi_logistics': 'ucommunications-sms01',
            },
            'sender_to_route': {'taxi': 'taxiauth', 'yango': 'yango'},
        },
        'infobip': {'sender_to_alpha_name': {}},
    },
)
async def test_src_name(
        taxi_ucommunications, mockserver, mock_personal, testpoint,
):
    @testpoint('set_tvm_source')
    def set_tvm_source(data):
        # flake8: noqa
        assert data['src'] == 'ucommunications-sms01'

    @mockserver.json_handler('/yasms/sendsms')
    def _sendsms(request):
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    response = await taxi_ucommunications.post(
        'user/sms/send',
        json={
            'phone': 'deadbeaf',
            'text': 'Добрый день!',
            'intent': 'src_name',
        },
    )
    assert response.status_code == 200
    await set_tvm_source.wait_call()
