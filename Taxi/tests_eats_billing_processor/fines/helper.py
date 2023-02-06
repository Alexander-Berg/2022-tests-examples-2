class OrderFinesTest:
    def __init__(self):
        self._request = None
        self._expected = {'fines': []}
        self._expected_status = 200
        self._expected_response = {'code': '200', 'message': 'OK'}
        self._create_expected_response = {'event_id': '1'}
        self._expected_create_request = None
        self._expected_appeals = []

    def on_request(self, order_nr):
        self._request = {'order_nr': order_nr}
        return self

    def on_request_by_id(self, fine_id):
        self._request = {'id': fine_id}
        return self

    def appeal_request(self, fine_id, ticket):
        self._request = {'fine_id': fine_id, 'ticket': ticket}
        return self

    def expect_order_fine(
            self,
            fine_id,
            amount,
            currency,
            is_appealed,
            ticket=None,
            fine_reason_id=None,
            fine_reason=None,
    ):
        order_fine = {
            'fine_id': fine_id,
            'amount': amount,
            'currency': currency,
            'is_appealed': is_appealed,
        }
        if ticket is not None:
            order_fine['ticket'] = ticket
        if fine_reason_id is not None:
            order_fine['fine_reason_id'] = fine_reason_id
        if fine_reason is not None:
            order_fine['fine_reason'] = fine_reason
        self._expected['fines'].append(order_fine)
        return self

    def expect_fine_by_id(
            self,
            fine_id,
            order_nr,
            amount,
            currency,
            is_appealed,
            fine_reason_id,
            fine_reason,
            ticket=None,
    ):
        fine_by_id = {
            'fine_id': fine_id,
            'order_nr': order_nr,
            'amount': amount,
            'currency': currency,
            'is_appealed': is_appealed,
            'fine_reason_id': fine_reason_id,
            'fine_reason': fine_reason,
        }
        if ticket is not None:
            fine_by_id['ticket'] = ticket
        self._expected = {'fine': fine_by_id}
        return self

    def expect_fine_appeal_event(self, **kwargs):
        self._expected_create_request = kwargs
        return self

    def should_fail(self, status, code, message=None):
        self._expected_status = status
        self._expected_response = {'code': code}
        if message is not None:
            self._expected_response['message'] = message
        return self

    def expect_appeal(self, fine_id, ticket, amount):
        self._expected_appeals.append((fine_id, ticket, amount))
        return self

    async def run(self, fixtures):
        response = await fixtures.taxi_eats_billing_processor.post(
            '/v1/order_fines', json=self._request,
        )

        assert response.status == 200
        assert response.json() == self._expected

    async def run_by_id(self, fixtures):
        response = await fixtures.taxi_eats_billing_processor.post(
            '/v1/order_fines/by_id', json=self._request,
        )

        assert response.status == self._expected_status
        if response.status == 200:
            assert response.json() == self._expected
        else:
            assert response.json()['code'] == self._expected_response['code']
            if 'message' in self._expected_response:
                assert (
                    response.json()['message']
                    == self._expected_response['message']
                )

    async def appeal_run(self, fixtures, pgsql):
        @fixtures.mockserver.json_handler('/eats-billing-processor/v1/create')
        def _handler(req):
            assert req.json['data'] == self._expected_create_request
            return fixtures.mockserver.make_response(
                status=200,
                json=self._create_expected_response,
                headers={},
                content_type='application/json',
            )

        response = await fixtures.taxi_eats_billing_processor.post(
            '/v1/order_fines/appeal', json=self._request,
        )
        assert response.status == self._expected_status
        assert response.json() == self._expected_response

        cursor = pgsql['eats_billing_processor'].cursor()
        cursor.execute(
            f"""select cast(fine_id as text) as fine_id,
            ticket as ticket,
            cast(amount as text) as amount
            from eats_billing_processor.appeals""",
        )
        result_appeals = list(cursor)
        assert result_appeals == self._expected_appeals
