import pytest


@pytest.fixture(name='mock_payments_pay_waiting', autouse=True)
def _mock_payments_pay_waiting(mockserver):
    @mockserver.json_handler('/cargo-claims/v1/claims/payments/pay-waiting')
    def mock(request):
        context.requests.append(request)
        if context.status_code == 200:
            return {'new_status': 'pay_waiting'}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


@pytest.fixture(name='mock_payments_finish', autouse=True)
def _mock_payments_finish(mockserver):
    @mockserver.json_handler('/cargo-claims/v1/claims/payments/finish')
    def mock(request):
        context.requests.append(request)
        if context.status_code == 200:
            return {}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.requests = []
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


PAYMENT_ID = '4e3c6120-f437-4c55-a980-4b9171f9f9c2'


async def test_cargo_on_confirmed(stq_runner, mock_payments_pay_waiting):
    """
        Check cargo-claims v1/payments/pay-waiting was called.
    """
    await stq_runner.cargo_payment_status_changed.call(
        task_id='test',
        kwargs={'payment_id': PAYMENT_ID, 'new_status': 'confirmed'},
    )

    assert mock_payments_pay_waiting.handler.times_called == 1


async def test_cargo_on_authorized(stq_runner, mock_payments_finish):
    """
        Check cargo-claims v1/claims/payments/finished was called.
    """
    await stq_runner.cargo_payment_status_changed.call(
        task_id='test',
        kwargs={
            'payment_id': PAYMENT_ID,
            'new_status': 'authorized',
            'cost': '20.0000',
        },
    )

    assert mock_payments_finish.handler.times_called == 1


async def test_cargo_on_finished(stq_runner, mock_payments_finish):
    """
        Check cargo-claims v1/claims/payments/finished was called.
    """
    await stq_runner.cargo_payment_status_changed.call(
        task_id='test',
        kwargs={
            'payment_id': PAYMENT_ID,
            'new_status': 'finished',
            'cost': '20.0000',
            'invoice_link': 'link',
        },
    )

    assert mock_payments_finish.handler.times_called == 1

    await stq_runner.cargo_payment_status_changed.call(
        task_id='test',
        kwargs={
            'payment_id': PAYMENT_ID,
            'new_status': 'finished',
            'cost': '20.0000',
        },
    )

    assert mock_payments_finish.handler.times_called == 1
