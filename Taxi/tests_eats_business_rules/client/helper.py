class ClientTest:
    client_type_map = {
        'delivery': 'delivery',
        'pickup': 'pickup',
        'qr_pay': 'qrpay',
        'picker_delivery': 'delivery',
        'tips': 'tips',
    }
    agreement_type_map = {
        'delivery': 'delivery',
        'pickup': 'delivery',
        'qr_pay': 'delivery',
        'picker_delivery': 'picker',
        'tips': 'delivery',
    }

    def __init__(self):
        self._request = None
        self._core_response = None
        self._error_response = None
        self._expected_result = None
        self._times_called = 0
        self._status = 200

    def request(self, counterparty_type, counterparty_id, timestamp):
        self._request = {
            'counterparty_type': counterparty_type,
            'counterparty_id': counterparty_id,
            'timestamp': timestamp,
        }
        return self

    def core_response(
            self, client_id, commission, acquiring_commission, fix_commission,
    ):
        self._core_response = {
            'status': 200,
            'body': {
                'client_id': client_id,
                'commissions': {
                    'commission': commission,
                    'acquiring_commission': acquiring_commission,
                    'fix_commission': fix_commission,
                },
            },
        }
        return self

    def core_response_error(self, status, code, message):
        self._core_response = {
            'status': status,
            'body': {'status': code, 'message': message},
        }
        return self

    def expected_result(self, client_id):
        self._expected_result = {'client_id': client_id}
        return self

    def should_fail(self, status, code, message):
        self._status = status
        self._error_response = {'code': code, 'message': message}
        return self

    def times_called(self, number):
        self._times_called = number
        return self

    async def run(self, taxi_eats_business_rules, mockserver):
        @mockserver.json_handler(
            '/eats-billing-business-rules/eats-billing/business-rules',
        )
        def _handler(req):
            return mockserver.make_response(
                status=self._core_response['status'],
                json=self._core_response['body'],
                headers={},
                content_type='application/json',
            )

        response = await taxi_eats_business_rules.post(
            '/v1/client/id', json=self._request,
        )
        assert response.status == self._status
        assert response.json() == self.expected_response()
        assert _handler.times_called <= self.expected_times_called_max()

    def expected_response(self):
        if self._error_response:
            return self._error_response

        if self._expected_result:
            return self._expected_result

        return {'client_id': self._core_response['body']['client_id']}

    def expected_times_called_max(self):
        return self._times_called
