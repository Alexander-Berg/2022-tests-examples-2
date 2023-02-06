class FineTest:
    def __init__(self):
        self._request = None
        self._core_response = None
        self._error_response = None
        self._expected_result = None
        self._status = 200

    def request(
            self,
            counterparty_type,
            client_id,
            business_type,
            delivery_type,
            reason,
            timestamp,
    ):
        self._request = {
            'counterparty_type': counterparty_type,
            'client_id': client_id,
            'business_type': business_type,
            'delivery_type': delivery_type,
            'reason': reason,
            'timestamp': timestamp,
        }
        return self

    def expected_result(
            self,
            rule_id,
            client_id,
            period,
            fine,
            fix_fine,
            min_fine,
            max_fine,
            gmv_limit,
    ):
        self._expected_result = {
            'rule_id': rule_id,
            'client_id': client_id,
            'fine_params': {
                'application_period': period,
                'fine': fine,
                'fix_fine': fix_fine,
                'min_fine': min_fine,
                'max_fine': max_fine,
                'gmv_limit': gmv_limit,
            },
        }
        return self

    def should_fail(self, status, code, message):
        self._status = status
        self._error_response = {'code': code, 'message': message}
        return self

    def core_response(self, application_period, fine, gmv_limit):
        self._core_response = {
            'status': 200,
            'body': {
                'application_period': application_period,
                'fine': fine,
                'gmv_limit': gmv_limit,
            },
        }
        return self

    def core_response_error(self, status, code, message):
        self._core_response = {
            'status': status,
            'body': {'status': code, 'message': message},
        }
        return self

    async def run(self, taxi_eats_business_rules, mockserver):
        @mockserver.json_handler(
            '/eats-billing-business-rules/eats-billing/fine',
        )
        def _handler(req):
            return mockserver.make_response(
                status=self._core_response['status'],
                json=self._core_response['body'],
                headers={},
                content_type='application/json',
            )

        response = await taxi_eats_business_rules.post(
            '/v1/fine', json=self._request,
        )

        def strip_non_core_fields(response):
            response.pop('rule_id', None)
            if 'fine_params' in response:
                response['fine_params'].pop('fix_fine', None)
                response['fine_params'].pop('min_fine', None)
                response['fine_params'].pop('max_fine', None)

        assert response.status == self._status
        if self._core_response:
            assert strip_non_core_fields(
                response.json(),
            ) == strip_non_core_fields(self.expected_response())
        else:
            assert response.json() == self.expected_response()

    def expected_response(self):
        if self._error_response:
            return self._error_response

        if self._core_response:
            return self._core_response

        return self._expected_result
