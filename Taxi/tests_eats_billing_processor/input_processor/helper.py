import json

GROCERY_CLIENT_ID = '94062943'


class InputProcessorTest:
    def __init__(self):
        self._request = None
        self._expected_status = 200
        self._expected_response = {'event_id': '1'}
        self._expected_select_result = None
        self._expected_stq_call = True
        self._business_rules = {}
        self._rule_name = 'default'
        self._expected_v2 = False
        self._client_info = {'places': {}, 'couriers': {}, 'pickers': {}}

    def request(
            self, order_nr, external_id, event_at, kind, data, rule_name=None,
    ):
        self._request = {
            'order_nr': order_nr,
            'external_id': external_id,
            'event_at': event_at,
            'kind': kind,
            'data': data,
        }

        if rule_name is not None:
            self._request['rule_name'] = rule_name
            self._rule_name = rule_name

        self._expected_select_result = {
            'order_nr': order_nr,
            'kind': kind,
            'data': data,
        }
        return self

    def expected_response(self, event_id):
        self._expected_response = {'event_id': event_id}
        return self

    def using_business_rules(
            self, client_info, place_id=None, courier_id=None, picker_id=None,
    ):
        counter = sum(
            map(
                lambda x: 0 if x is None else 1,
                [place_id, courier_id, picker_id],
            ),
        )
        if counter == 0:
            raise ValueError('place_id, courier_id or picker_id expected')
        elif counter != 1:
            raise ValueError(
                'Only one of place_id, courier_id and picker_id allowed',
            )

        counterparty_id = None
        client_dict = None
        if place_id is not None:
            counterparty_id = place_id
            client_dict = self._client_info['places']
        elif courier_id is not None:
            counterparty_id = courier_id
            client_dict = self._client_info['couriers']
        else:
            counterparty_id = picker_id
            client_dict = self._client_info['pickers']

        if client_dict is not None and client_info is not None:
            client_dict[counterparty_id] = client_info

        return self

    def expected_rule_name(self, rule_name):
        self._rule_name = rule_name
        return self

    def expected_result_append(self, params: dict):
        self._expected_select_result.update(params)
        return self

    def should_fail(self, status, code, message):
        self._expected_status = status
        self._expected_response = {'code': code, 'message': message}
        return self

    def expected_v2(self, expected):
        self._expected_v2 = expected
        return self

    def no_database_insertion(self):
        self._expected_select_result = None
        return self

    def no_stq_call(self):
        self._expected_stq_call = False
        return self

    async def run(self, fixtures):
        fixtures.client_info_mock(self._client_info)

        response = await fixtures.taxi_eats_billing_processor.post(
            '/v1/create', json=self._request,
        )
        assert response.status == self._expected_status
        assert response.json() == self._expected_response

        if self._expected_status == 200:
            external_id = self._request['external_id']
            cursor = fixtures.pgsql['eats_billing_processor'].cursor()
            cursor.execute(
                f"""
                select order_nr, kind, data, data_v2, rule_name
                from eats_billing_processor.input_events
                where external_id = '{external_id}';""",
            )
            res = cursor.fetchone()
            if res:
                assert res[0] == self._expected_select_result['order_nr']
                assert res[1] == self._expected_select_result['kind']
                print(json.loads(res[2]))
                print(self._expected_select_result['data'])
                assert (
                    json.loads(res[2]) == self._expected_select_result['data']
                )
                data_v2 = res[3]
                if self._expected_v2:
                    assert data_v2 is not None
                    print(json.loads(res[2]))
                    print(data_v2)
                else:
                    assert data_v2 is None
                assert res[4] == self._rule_name
            else:
                assert self._expected_select_result is None

            if self._expected_stq_call:
                call_info = (
                    fixtures.stq.eats_billing_processor_transformer.next_call()
                )
                order_nr = self._request['order_nr']
                assert call_info['id'] == f'trans_{order_nr}'
                assert (
                    call_info['queue'] == 'eats_billing_processor_transformer'
                )

                kwargs = call_info['kwargs']
                assert kwargs['order_nr'] == self._request['order_nr']


class InputProcessorTestV2:
    def __init__(self):
        self._request = None
        self._expected_status = 200
        self._expected_response = {'event_id': '1'}

    def request(self, order_nr, external_id, event_at, data):
        self._request = {
            'order_nr': order_nr,
            'external_id': external_id,
            'event_at': event_at,
            'data': data,
        }
        return self

    def expected_response(self, event_id):
        self._expected_response = {'event_id': event_id}
        return self

    def should_fail(self, status):
        self._expected_status = status
        return self

    async def run(self, fixtures):
        response = await fixtures.taxi_eats_billing_processor.post(
            '/v2/create', json=self._request,
        )
        assert response.status == self._expected_status
        if self._expected_status == 200:
            assert response.json() == self._expected_response
