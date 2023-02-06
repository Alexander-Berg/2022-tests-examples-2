class CommissionTest:
    commission_type_map = {
        'place_delivery': 'delivery',
        'courier_delivery': 'delivery',
        'pickup': 'pickup',
        'qr_pay': 'qrpay',
        'picker_delivery': 'delivery',
        'tips': 'tips',
    }
    agreement_type_map = {
        'place_delivery': 'delivery',
        'courier_delivery': 'delivery',
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
        self._status = 200
        self._core_commission_response = None

    def request(self, counterparty_id, commission_type, timestamp):
        self._request = {
            'counterparty_id': counterparty_id,
            'commission_type': commission_type,
            'timestamp': timestamp,
        }
        return self

    def core_commission_response(
            self, commission, acquiring_commission, fix_commission,
    ):
        self._core_commission_response = {
            'status': 200,
            'body': {
                'commission': commission,
                'acquiring_commission': acquiring_commission,
                'fix_commission': fix_commission,
            },
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

    def expected_result(
            self,
            rule_id,
            client_id,
            commission,
            fix_commission,
            acquiring_commission,
            billing_frequency=None,
    ):
        expected_result = {
            'rule_id': rule_id,
            'client_id': client_id,
            'commission_params': {
                'commission': commission,
                'fix_commission': fix_commission,
                'acquiring_commission': acquiring_commission,
            },
        }
        if billing_frequency is not None:
            expected_result['billing_frequency'] = billing_frequency
        self._expected_result = expected_result
        return self

    def should_fail(self, status, code, message):
        self._status = status
        self._error_response = {'code': code, 'message': message}
        return self

    async def run(self, taxi_eats_business_rules, mockserver):
        @mockserver.json_handler(
            '/eats-billing-business-rules/eats-billing/business-rules',
        )
        def _handler(req):
            assert dict(req.json) == self.expected_core_request()
            return mockserver.make_response(
                status=self._core_response['status'],
                json=self._core_response['body'],
                headers={},
                content_type='application/json',
            )

        @mockserver.json_handler(
            '/eats-billing-business-rules/eats-billing/commission',
        )
        def _handler_commission(req):
            return mockserver.make_response(
                status=self._core_commission_response['status'],
                json=self._core_commission_response['body'],
                headers={},
                content_type='application/json',
            )

        response = await taxi_eats_business_rules.post(
            '/v1/commission', json=self._request,
        )
        assert response.status == self._status

        def strip_rule_id(response):
            response.pop('rule_id', 0)
            return response

        assert strip_rule_id(response.json()) == strip_rule_id(
            self.expected_response(),
        )
        assert _handler.times_called == self.expected_times_called()
        assert (
            _handler_commission.times_called == self.commission_times_called()
        )

    def expected_core_request(self):
        if (
                self._request['commission_type'] == 'place_delivery'
                or self._request['commission_type'] == 'pickup'
                or self._request['commission_type'] == 'qr_pay'
        ):
            counterparty_type = 'place'
        else:
            counterparty_type = 'courier'
        ret = {
            'counteragent_type': counterparty_type,
            'billing_date': self._request['timestamp'],
        }
        if (
                self._request['commission_type'] == 'place_delivery'
                or self._request['commission_type'] == 'pickup'
                or self._request['commission_type'] == 'qr_pay'
        ):
            ret['counteragent_details'] = {
                'place_id': self._request['counterparty_id'],
                'commission_type': self.commission_type_map[
                    self._request['commission_type']
                ],
            }
        else:
            ret['counteragent_details'] = {
                'courier_id': self._request['counterparty_id'],
                'product_type': self.commission_type_map[
                    self._request['commission_type']
                ],
                'agreement_type': self.agreement_type_map[
                    self._request['commission_type']
                ],
            }
        return ret

    def expected_response(self):
        if self._error_response:
            return self._error_response

        if self._expected_result:
            return self._expected_result

        return {
            'rule_id': '',
            'client_id': self._core_response['body']['client_id'],
            'commission_params': {
                'commission': self._core_response['body']['commissions'][
                    'commission'
                ],
                'acquiring_commission': self._core_response['body'][
                    'commissions'
                ]['acquiring_commission'],
                'fix_commission': self._core_response['body']['commissions'][
                    'fix_commission'
                ],
            },
        }

    def expected_times_called(self):
        return 1 if self._core_response else 0

    def commission_times_called(self):
        return 1 if self._core_commission_response else 0
