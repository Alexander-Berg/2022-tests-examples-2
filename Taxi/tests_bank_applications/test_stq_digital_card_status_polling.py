import pytest


@pytest.fixture
def bank_core_card(mockserver):
    class Context:
        def __init__(self):
            self.http_status_code = 200
            self.card_request_check = None
            self.errors = None
            self.status = 'SUCCESS'

        def set_status(self, status):
            self.status = status

        def set_errors(self, errors):
            assert all(
                'code' in error and 'message' in error for error in errors
            )
            self.errors = errors

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler('/bank-core-card/v1/card/request/check')
    def _card_request_check(request):
        return mockserver.make_response(
            status=context.http_status_code,
            json={
                'status': context.status,
                'request_id': request.json['request_id'],
                'errors': context.errors,
            },
        )

    context.card_request_check = _card_request_check

    return context


@pytest.mark.parametrize('core_card_status', ['SUCCESS', 'PENDING', 'FAILED'])
async def test_bank_applications_digital_card_status_polling(
        mockserver, stq_runner, bank_core_card, core_card_status,
):
    @mockserver.json_handler(
        '/bank-applications/applications-internal/v1/set_application_status',
    )
    def _set_application_status(request):
        return mockserver.make_response(json={}, status=200)

    bank_core_card.set_status(core_card_status)
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a05'
    await stq_runner.bank_applications_digital_card_status_polling.call(
        task_id='sample_task',
        kwargs={
            'buid': 'BUID',
            'session_uuid': 'session_uuid',
            'request_id': 'request_id',
            'application_id': application_id,
        },
        expect_fail=False,
    )
    if core_card_status == 'PENDING':
        assert _set_application_status.times_called == 0
    else:
        assert _set_application_status.times_called == 1


async def test_digital_card_status_polling_failed_with_errors(
        mockserver, stq_runner, bank_core_card,
):
    @mockserver.json_handler(
        '/bank-applications/applications-internal/v1/set_application_status',
    )
    def _set_application_status(request):
        assert request.json['errors'] == [
            'error_code_1:message_1',
            'error_code_2:message_2',
        ]
        return mockserver.make_response(json={}, status=200)

    errors = [
        {'code': 'error_code_1', 'message': 'message_1'},
        {'code': 'error_code_2', 'message': 'message_2'},
    ]
    bank_core_card.set_errors(errors)
    bank_core_card.set_status('FAILED')
    await stq_runner.bank_applications_digital_card_status_polling.call(
        task_id='sample_task',
        kwargs={
            'buid': 'BUID',
            'session_uuid': 'session_uuid',
            'request_id': 'request_id',
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a05',
        },
        expect_fail=False,
    )
    assert _set_application_status.times_called == 1


@pytest.mark.parametrize('core_card_error_code', [400, 404, 500])
async def test_digital_card_status_polling_core_card_error(
        stq_runner, bank_core_card, core_card_error_code,
):
    bank_core_card.set_http_status_code(core_card_error_code)
    await stq_runner.bank_applications_digital_card_status_polling.call(
        task_id='sample_task',
        kwargs={
            'buid': 'BUID',
            'session_uuid': 'session_uuid',
            'request_id': 'request_id',
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a05',
        },
        expect_fail=True,
    )


@pytest.mark.parametrize('set_status_error_code', [404, 500])
async def test_digital_card_status_polling_set_status_error(
        mockserver, stq_runner, bank_core_card, set_status_error_code,
):
    @mockserver.json_handler(
        '/bank-applications/applications-internal/v1/set_application_status',
    )
    def _set_application_status(request):
        return mockserver.make_response(json={}, status=set_status_error_code)

    await stq_runner.bank_applications_digital_card_status_polling.call(
        task_id='sample_task',
        kwargs={
            'buid': 'BUID',
            'session_uuid': 'session_uuid',
            'request_id': 'request_id',
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a05',
        },
        expect_fail=True,
    )
    assert _set_application_status.times_called == 1
