COMPLETE_STATUS = 200
INCORRECT_STATUS = 409
ERROR_STATUS = 500

COMPLETE_MESSAGE = 'Корректировка успешно создана'
ERROR_MESSAGE = 'Internal Server Error'


def make_doc(doc_id, transaction):
    doc = {'doc_id': doc_id, 'data': {'payments': transaction}}
    return doc


class CorrectionSaveTest:
    def __init__(self):
        self._request = None
        self._response = None
        self._should_fail = False
        self._docs = None
        self._expect_amount = '0'
        self._expected_status = COMPLETE_STATUS
        self._response = {
            'code': f'{COMPLETE_STATUS}',
            'message': COMPLETE_MESSAGE,
        }

    def request(
            self,
            order_nr,
            login,
            amount,
            currency,
            ticket,
            correction_type,
            correction_group,
            product=None,
            detailed_product=None,
    ):
        self._request = {
            'order_nr': order_nr,
            'login': login,
            'amount': amount,
            'currency': currency,
            'ticket': ticket,
            'correction_group': correction_group,
            'correction_type': correction_type,
        }
        if product is not None:
            self._request['product'] = product
        if detailed_product is not None:
            self._request['detailed_product'] = detailed_product
        return self

    def expected_status(self, status, expected_message):
        self._expected_status = status
        self._response['code'] = f'{status}'
        self._response['message'] = expected_message
        return self

    def should_fail(self, status, code, message):
        self._should_fail = True
        self._expected_status = status
        self._response = {'code': code, 'message': message}
        return self

    def docs(self, docs):
        self._docs = docs
        return self

    def expect_amount(self, amount):
        self._expect_amount = amount
        return self

    async def run(self, fixtures):
        if self._expected_status == ERROR_STATUS:
            fixtures.billing_reports_mock.should_fail()
        else:
            fixtures.billing_reports_mock.docs(self._docs)
        response = await fixtures.taxi_eats_billing_processor.post(
            '/v1/correction_save', json=self._request,
        )
        assert response.status == self._expected_status
        assert response.json() == self._response

        if self._should_fail is False:
            cursor = fixtures.pgsql['eats_billing_processor'].cursor()
            cursor.execute(
                f"""select login, ticket, correction_group, correction_type,
                    cast(amount as TEXT) as amount, currency,
                    detailed_product, product
                    from eats_billing_processor.order_accounting_correction""",
            )
            res = cursor.fetchone()
            assert res[0] == self._request['login']
            assert res[1] == self._request['ticket']
            assert res[2] == self._request['correction_group']
            assert res[3] == self._request['correction_type']
            assert res[4] == self._expect_amount
            assert res[5] == self._request['currency']
            if 'detailed_product' in self._request:
                assert res[6] == self._request['detailed_product']
            if 'product' in self._request:
                assert res[7] == self._request['product']

            call_info = (
                fixtures.stq.eats_orders_billing_input_events.next_call()
            )
            order_nr = self._request['order_nr']
            assert call_info['id'] == f'eats_orders_billing_{order_nr}_1'
