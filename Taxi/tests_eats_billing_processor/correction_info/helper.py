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


class CorrectionInfoTest:
    def __init__(self):
        self._request = None
        self._response = None
        self._order_nr = None
        self._expect_fail = False
        self._expected_status = 200
        self._docs = None

    def request(self, order_nr):
        self._order_nr = order_nr
        self._request = {'order_nr': self._order_nr}
        return self

    def expect_fail(self, status=500):
        self._expect_fail = True
        self._expected_status = status
        return self

    def response(self, amounts, table_format, corrections, docs=None):
        self._response = {
            'order_nr': self._order_nr,
            'amounts': amounts,
            'table_format': table_format,
            'corrections': corrections,
        }
        self._docs = docs
        return self

    async def run(self, fixtures):
        if self._expect_fail:
            fixtures.billing_reports_mock.should_fail()
        else:
            fixtures.billing_reports_mock.docs(self._docs)

        response = await fixtures.taxi_eats_billing_processor.post(
            '/v1/correction_info', json=self._request,
        )
        assert response.status == self._expected_status
        if not self._expect_fail:
            amounts = self._response['amounts']
            expect_amounts = response.json()['amounts']
            assert len(amounts) == len(expect_amounts)
            for amount in amounts:
                find = False
                for expect_amount in expect_amounts:
                    if amount == expect_amount:
                        find = True
                        break
                assert find is True

            corrections = self._response['corrections']
            expect_corrections = response.json()['corrections']
            assert len(corrections) == len(expect_corrections)
            for correction in corrections:
                find = False
                for expect_correction in expect_corrections:
                    if correction == expect_correction:
                        find = True
                        break
                assert find is True

            table_format = self._response['table_format']
            expect_table_format = response.json()['table_format']
            assert len(table_format) == len(expect_table_format)
            for column in table_format:
                find = False
                for expect_column in expect_table_format:
                    if column == expect_column:
                        find = True
                        break
                assert find is True
