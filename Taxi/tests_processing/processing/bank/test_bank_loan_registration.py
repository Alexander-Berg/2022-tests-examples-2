import urllib

from tests_processing.processing.bank import common


async def test_bank_loan_registration_happy_path(processing, mockserver):
    await processing.bank.applications.send_event(
        item_id=common.APPLICATION_ID,
        payload={'kind': 'init', 'type': 'LOAN_REGISTRATION'},
        stq_queue='bank_applications_procaas',
    )

    @mockserver.json_handler('/applications-internal/v1/get_application_data')
    def _mock_get_application_data(request):
        assert request.json == {'application_id': common.APPLICATION_ID}
        return {'form': {'phone': common.PHONE_NUMBER}}

    @mockserver.handler('/userinfo-internal/v1/set_bank_phone')
    def _mock_set_bank_phone(request):
        assert request.json == {
            'buid': common.BUID,
            'phone': common.PHONE_NUMBER,
        }
        return mockserver.make_response('')

    @mockserver.json_handler(
        r'/account/(?P<yuid>\d+)/alias/bank_phonenumber/', regex=True,
    )
    def _mock_bank_phonenumber(request, yuid):
        assert yuid == common.YUID
        assert request.method == 'POST'
        assert 'Ya-Consumer-Client-Ip' not in request.headers
        assert request.form == {'phone_number': common.PHONE_NUMBER}
        return {'status': 'ok'}

    @mockserver.json_handler(
        r'/account/(?P<yuid>\d+)/subscription/bank/', regex=True,
    )
    def _mock_subscription_bank(request, yuid):
        assert yuid == common.YUID
        assert request.method == 'POST'
        assert request.query == {'consumer': 'processing_fintech'}
        return {'status': 'ok'}

    @mockserver.handler('/applications-internal/v1/set_application_status')
    def _mock_set_application_status(request):
        assert request.json == {
            'application_id': common.APPLICATION_ID,
            'status': 'SUCCESS',
            'errors': None,
        }
        return mockserver.make_response('')

    await processing.bank.applications.send_event(
        item_id=common.APPLICATION_ID,
        payload={
            'kind': 'update',
            'type': 'LOAN_REGISTRATION',
            'buid': common.BUID,
            'yuid': common.YUID,
        },
        stq_queue='bank_applications_procaas',
    )


async def test_bank_loan_registration_failed(processing, mockserver):
    await processing.bank.applications.send_event(
        item_id=common.APPLICATION_ID,
        payload={'kind': 'init', 'type': 'LOAN_REGISTRATION'},
        stq_queue='bank_applications_procaas',
    )

    @mockserver.json_handler('/applications-internal/v1/get_application_data')
    def _mock_get_application_data(request):
        assert request.json == {'application_id': common.APPLICATION_ID}
        return {'form': {'phone': common.PHONE_NUMBER}}

    @mockserver.json_handler('/userinfo-internal/v1/set_bank_phone')
    def _mock_set_bank_phone(request):
        assert request.json == {
            'buid': common.BUID,
            'phone': common.PHONE_NUMBER,
        }
        return mockserver.make_response(
            json={'code': 409, 'message': 'Phone already in use'}, status=409,
        )

    @mockserver.handler('/applications-internal/v1/set_application_status')
    def _mock_set_application_status(request):
        assert request.json == {
            'application_id': common.APPLICATION_ID,
            'status': 'FAILED',
            'errors': ['409:Phone already in use'],
        }
        return mockserver.make_response('')

    await processing.bank.applications.send_event(
        item_id=common.APPLICATION_ID,
        payload={
            'kind': 'update',
            'type': 'LOAN_REGISTRATION',
            'buid': common.BUID,
            'yuid': common.YUID,
        },
        stq_queue='bank_applications_procaas',
    )
