def compare_item(expected, response):
    assert expected['rule_id'] == response['rule_id']
    assert expected['applied_at'] == response['applied_at']
    assert expected['client_id'] == response['client_id']
    assert expected['commission_type'] == response['commission_type']
    assert expected['commission_params'] == response['commission_params']
    if 'cancelled_at' in response.keys():
        assert expected['cancelled_at'] == response['cancelled_at']


def check_db_state(pgsql, counterparty_id, service_type, expected_state):
    cursor = pgsql['eats_business_rules'].cursor()
    cursor.execute(
        f"""select id, applied_at, cancelled_at
            from eats_business_rules.commission
            where counterparty_id = '{counterparty_id}'
            and service_type = '{service_type}'""",
    )

    selected = list(cursor)

    for sel in selected:
        assert sel in expected_state
        expected_state.remove(sel)

    assert expected_state == []


class AdminCommissionTest:
    commission_type_map = {
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
        self._error_response = None
        self._expected_result = None
        self._expected_result_list = []
        self._status = 200

    def list_request(
            self,
            rule_id_offset,
            max_records,
            counterparty_id,
            commission_type,
            timestamp,
    ):
        self._request = {
            'rule_id_offset': rule_id_offset,
            'max_records': max_records,
            'counterparty_id': counterparty_id,
            'commission_type': commission_type,
            'timestamp': timestamp,
        }
        return self

    def create_request(
            self,
            applied_at,
            counterparty_id,
            commission_type,
            commission_params,
    ):
        self._request = {
            'applied_at': applied_at,
            'counterparty_id': counterparty_id,
            'commission_type': commission_type,
            'commission_params': commission_params,
        }
        return self

    def update_request(
            self,
            applied_at,
            applied_at_new,
            counterparty_id,
            commission_type,
            commission_params,
    ):
        self._request = {
            'applied_at': applied_at,
            'applied_at_new': applied_at_new,
            'counterparty_id': counterparty_id,
            'commission_type': commission_type,
            'commission_params': commission_params,
        }
        return self

    def delete_request(self, applied_at, counterparty_id, commission_type):
        self._request = {
            'applied_at': applied_at,
            'counterparty_id': counterparty_id,
            'commission_type': commission_type,
        }
        return self

    def expected_result(
            self,
            rule_id,
            client_id,
            commission_type,
            applied_at,
            cancelled_at,
            commission_params,
    ):
        self._expected_result = {
            'rule_id': rule_id,
            'client_id': client_id,
            'commission_type': commission_type,
            'applied_at': applied_at,
            'cancelled_at': cancelled_at,
            'commission_params': commission_params,
        }
        return self

    def expected_result_list(self, items: list):
        for item in items:
            self._expected_result_list.append(
                {
                    'rule_id': item['rule_id'],
                    'client_id': item['client_id'],
                    'commission_type': item['commission_type'],
                    'applied_at': item['applied_at'],
                    'cancelled_at': item['cancelled_at'],
                    'commission_params': item['commission_params'],
                },
            )
        return self

    def should_fail(self, status, code, message):
        self._status = status
        self._error_response = {'code': code, 'message': message}
        return self

    def compare_list(self, response):
        response_list = sorted(response['list'], key=lambda k: k['rule_id'])
        expected_list = sorted(
            self._expected_result_list, key=lambda k: k['rule_id'],
        )

        for resp, exp in zip(response_list, expected_list):
            compare_item(resp, exp)

    async def run(self, taxi_eats_business_rules, pgsql, handler):
        response = await taxi_eats_business_rules.post(
            handler, json=self._request,
        )
        assert response.status == self._status

        if self._error_response:
            assert response.json() == self._error_response
        else:
            if self._expected_result_list:
                self.compare_list(response.json())
            else:
                compare_item(self._expected_result, response.json())
