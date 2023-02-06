def compare_item(expected, response):
    assert expected['rule_id'] == response['rule_id']
    assert expected['level'] == response['level']
    assert expected['applied_at'] == response['applied_at']
    assert expected['business_type'] == response['business_type']
    assert expected['delivery_type'] == response['delivery_type']
    assert expected['reason'] == response['reason']
    assert expected['fine_params'] == response['fine_params']
    if 'client_id' in response.keys():
        assert expected['client_id'] == response['client_id']
    if 'region_name' in response.keys():
        assert expected['region_name'] == response['region_name']
    if 'cancelled_at' in response.keys():
        assert expected['cancelled_at'] == response['cancelled_at']


def check_db_state(pgsql, level, business, delivery, reason, expected_state):
    cursor = pgsql['eats_business_rules'].cursor()
    cursor.execute(
        f"""select id, applied_at, cancelled_at
            from eats_business_rules.fine
            where level = '{level}'
            and business = '{business}'
            and delivery = '{delivery}'
            and reason = '{reason}'""",
    )

    selected = list(cursor)

    for sel in selected:
        assert sel in expected_state
        expected_state.remove(sel)

    assert expected_state == []


class AdminFineTest:
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
            level,
            counterparty_type,
            counterparty_id,
            region_name,
            business_type,
            delivery_type,
            reason,
            timestamp,
    ):
        self._request = {
            'rule_id_offset': rule_id_offset,
            'max_records': max_records,
            'level': level,
            'counterparty_type': counterparty_type,
            'counterparty_id': counterparty_id,
            'region_name': region_name,
            'business_type': business_type,
            'delivery_type': delivery_type,
            'reason': reason,
            'timestamp': timestamp,
        }
        return self

    def create_request(
            self,
            applied_at,
            level,
            business_type,
            delivery_type,
            reason,
            counterparty_id,
            counterparty_type,
            region_name,
            fine_params,
    ):
        self._request = {
            'applied_at': applied_at,
            'level': level,
            'business_type': business_type,
            'delivery_type': delivery_type,
            'reason': reason,
            'counterparty_id': counterparty_id,
            'counterparty_type': counterparty_type,
            'region_name': region_name,
            'fine_params': fine_params,
        }
        return self

    def update_request(
            self,
            applied_at,
            applied_at_new,
            level,
            business_type,
            delivery_type,
            reason,
            counterparty_id,
            counterparty_type,
            region_name,
            fine_params,
    ):
        self._request = {
            'applied_at': applied_at,
            'applied_at_new': applied_at_new,
            'level': level,
            'business_type': business_type,
            'delivery_type': delivery_type,
            'reason': reason,
            'counterparty_id': counterparty_id,
            'counterparty_type': counterparty_type,
            'region_name': region_name,
            'fine_params': fine_params,
        }
        return self

    def delete_request(
            self,
            applied_at,
            level,
            business_type,
            delivery_type,
            reason,
            counterparty_id,
            counterparty_type,
            region_name,
    ):
        self._request = {
            'applied_at': applied_at,
            'level': level,
            'business_type': business_type,
            'delivery_type': delivery_type,
            'reason': reason,
            'counterparty_id': counterparty_id,
            'counterparty_type': counterparty_type,
            'region_name': region_name,
        }
        return self

    def expected_result(
            self,
            rule_id,
            applied_at,
            cancelled_at,
            level,
            business_type,
            delivery_type,
            reason,
            client_id,
            region_name,
            fine_params,
    ):
        self._expected_result = {
            'rule_id': rule_id,
            'level': level,
            'client_id': client_id,
            'region_name': region_name,
            'applied_at': applied_at,
            'cancelled_at': cancelled_at,
            'business_type': business_type,
            'delivery_type': delivery_type,
            'reason': reason,
            'fine_params': fine_params,
        }
        return self

    def expected_result_list(self, items: list):
        for item in items:
            self._expected_result_list.append(
                {
                    'rule_id': item['rule_id'],
                    'level': item['level'],
                    'applied_at': item['applied_at'],
                    'cancelled_at': item['cancelled_at'],
                    'business_type': item['business_type'],
                    'delivery_type': item['delivery_type'],
                    'reason': item['reason'],
                    'fine_params': item['fine_params'],
                },
            )
            if 'client_id' in item.keys():
                self._expected_result_list[-1]['client_id'] = item['client_id']
            else:
                self._expected_result_list[-1]['region_name'] = item[
                    'region_name'
                ]

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

        for exp, resp in zip(expected_list, response_list):
            compare_item(exp, resp)

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
