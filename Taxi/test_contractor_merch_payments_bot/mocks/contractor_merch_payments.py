import pytest


@pytest.fixture
def mock_contractor_merch_payments(mockserver):
    @mockserver.json_handler(
        'contractor-merch-payments/'
        'internal/v1/contractor-merch-payments/payment/status',
    )
    async def _payment_status_get(request):
        if context.payment_status_get.status != 200:
            return mockserver.make_response(
                status=context.payment_status_get.status,
                json={
                    'code': 'payment_not_found',
                    'message': 'payment_not_found',
                },
            )

        payment = {
            'contractor': {
                'park_id': 'park-id-0',
                'contractor_id': 'contractor-id-0',
            },
            'status': 'pending_merchant_approve',
            'created_at': context.payment_status_get.created_at,
            'updated_at': context.payment_status_get.updated_at,
        }

        if context.payment_status_get.body is not None:
            payment.update(context.payment_status_get.body)

        return {'payment': payment}

    class PaymentStatusGetContext:
        def __init__(self):
            self.handler = _payment_status_get

            self.body = None
            self.status = 200
            self.created_at = '2021-11-12T12:00:00+00:00'
            self.updated_at = '2021-11-12T12:00:00+00:00'

    @mockserver.json_handler(
        'contractor-merch-payments/'
        'internal/contractor-merch-payments/v1/payment/price',
    )
    async def _payment_price_put(request):
        return context.payment_price_put.body

    class PaymentPricePutContext:
        def __init__(self):
            self.handler = _payment_price_put

            self.body = {
                'contractor': {
                    'park_id': 'park-id-0',
                    'contractor_id': 'contractor-id-0',
                },
                'created_at': '2021-11-12T12:00:00+00:00',
            }

    class Context:
        def __init__(self):
            self.payment_status_get = PaymentStatusGetContext()
            self.payment_price_put = PaymentPricePutContext()

    context = Context()

    return context
