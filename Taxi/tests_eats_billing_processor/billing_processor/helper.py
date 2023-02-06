import datetime
import json

from testsuite.utils import callinfo


class BillingProcessorTest:
    def __init__(self):
        self._order_nr = '12345'
        self._billing_events = []
        self._columns = ['kind']
        self._expected_transfers = []
        self._should_reschedule = False
        self._expect_fail = False
        self._expected_core_write_back = []

    def for_order_nr(self, order_nr):
        self._order_nr = order_nr
        return self

    def expected_fail(self):
        self._expect_fail = True
        return self

    def insert_billing_event(self, data, input_event_id=1):
        counter = len(self._billing_events) + 1
        self._billing_events.append(
            {
                'input_event_id': input_event_id,
                'order_nr': self._order_nr,
                'external_id': f'auto_{counter}',
                'kind': (
                    'payment'
                    if 'payment' in data.keys()
                    else 'refund'
                    if 'refund' in data.keys()
                    else 'commission'
                ),
                'event_at': datetime.datetime(2021, 3, 26, 17, counter, 0, 0),
                'transaction_date': data['transaction_date'],
                'data': data,
            },
        )
        return self

    def should_reschedule(self):
        self._should_reschedule = True
        return self

    def checking_columns(self, *columns):
        self._columns = columns
        return self

    def expect_transfers(self, *transfers):
        self._expected_transfers.extend(transfers)
        return self

    def expect_core_write_back(self, *events):
        self._expected_core_write_back.extend(events)
        return self

    async def run(self, fixture):
        core_write_back = []

        @fixture.mockserver.json_handler(
            '/eats-billing-storage/billing-storage/create/bulk',
        )
        def _handler(request):
            nonlocal core_write_back
            for item in request.json:
                if item['kind'] == 'CommissionOrder':
                    core_write_back.append(
                        ('commission', item['data']['commission_sum']),
                    )
                else:
                    core_write_back.append(
                        (
                            item['data']['transaction_type'],
                            item['data']['value_amount'],
                            item['data']['commission'],
                        ),
                    )
            response = {'message': 'OK', 'status': 'success'}
            return fixture.mockserver.make_response(json=response, status=200)

        cursor = fixture.pgsql['eats_billing_processor'].cursor()
        for event in self._billing_events:
            data = event['data']
            details = data[event['kind']]
            cursor.execute(
                f"""insert into eats_billing_processor.billing_events
                 (input_event_id, order_nr, external_id, kind, event_at,
                  transaction_date, external_payment_id, client_id,
                  product_type, amount, currency, data)
                 values ({event['input_event_id']}, '{event['order_nr']}',
                         '{event['external_id']}', '{event['kind']}',
                         '{event['event_at']}', '{event['transaction_date']}',
                         '{data['external_payment_id']}',
                         '{data['client']['id']}', '{details['product_type']}',
                          {details['amount']}, '{details['currency']}',
                         '{json.dumps(event['data'])}')""",
            )

        await fixture.stq_runner.eats_billing_processor_billing_processor.call(
            task_id='billing_1',
            kwargs={'order_nr': self._order_nr},
            expect_fail=self._expect_fail,
        )

        try:
            eats_billing_processor_stq = (
                fixture.stq.eats_billing_processor_billing_processor
            )
            call = eats_billing_processor_stq.next_call()
            assert self._should_reschedule
            assert call['id'] == 'billing_1'
        except callinfo.CallQueueEmptyError:
            assert not self._should_reschedule

        cursor.execute(
            f"""select {', '.join(self._columns)}
            from eats_billing_processor.transfers
            where service_order_id='{self._order_nr}'""",
        )
        billing_events = list(cursor)
        assert billing_events == self._expected_transfers

        assert core_write_back == self._expected_core_write_back
