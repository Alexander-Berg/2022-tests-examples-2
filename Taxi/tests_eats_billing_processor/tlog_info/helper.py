def column_format(column_name, column_number, title):
    column = {
        'column_name': column_name,
        'column_number': column_number,
        'title': title,
    }
    return column


def make_doc(doc_id, transaction):
    doc = {'doc_id': doc_id, 'data': {'payments': transaction}}
    return doc


class TLogInfoTest:
    def __init__(self):
        self._request = None
        self._response = None
        self._order_nr = None
        self._expected_status = 200
        self._times_called = 0
        self._async_fail = False
        self._docs = None

    def request(self, order_nr):
        self._order_nr = order_nr
        self._request = {'order_nr': self._order_nr}
        return self

    def async_fail(self):
        self._async_fail = True
        self._times_called = 3
        self._expected_status = 500
        return self

    def response(self, table_format, docs):
        self._docs = docs
        trs = []
        for doc in docs:
            trs.append(doc['data']['payments'])
        self._response = {
            'order_nr': self._order_nr,
            'table_format': table_format,
            'transactions': trs,
        }
        self._times_called = 1
        return self

    async def run(self, fixtures):
        if self._async_fail:
            fixtures.billing_reports_mock.should_fail()
        else:
            fixtures.billing_reports_mock.docs(self._docs)

        response = await fixtures.taxi_eats_billing_processor.post(
            '/v1/tlog_info', json=self._request,
        )

        assert fixtures.billing_reports_mock.times_called == self._times_called
        assert response.status == self._expected_status

        if self._async_fail is False:
            table_format = self._response['table_format']
            expect_table_format = response.json()['table_format']

            for column in table_format:
                find = False
                for expect_column in expect_table_format:
                    if column == expect_column:
                        find = True
                        break
                assert find is True

            assert (
                response.json()['transactions']
                == self._response['transactions']
            )
