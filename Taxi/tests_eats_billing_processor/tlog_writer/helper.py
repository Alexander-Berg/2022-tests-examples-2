import datetime
import json
import uuid


COMPANY_TYPE = {
    'restaurant': 'own_delivery',
    'marketplace': 'marketplace',
    'pickup': 'pickup',
    'retail': 'retail_own_packing_and_delivery',
    'shop': 'retail_own_delivery',
    'shop_marketplace': 'retail_marketplace',
    'grocery': 'lavka',
    'donation': 'donation',
    'grocery_eats_flow': 'lavka',
    'inplace': 'pickup',
}

SERVICES = {
    628: 'eats_rest_fee',
    629: 'eats_rest_incentive',
    645: 'eats_delivery_fee_tips',
    646: 'eats_delivery_selfemp',
    661: 'eats_retail_fee',
    676: 'eats_donation',
    699: 'eats_retail_assembling',
    1167: 'eats_payments',
    1176: 'eats_inplace_payments',
    1177: 'eats_inplace_commission',
}


def client_info(client_id, contract_id, country_code, mvp, employment=None):
    result = {
        'id': client_id,
        'contract_id': contract_id,
        'country_code': country_code,
        'mvp': mvp,
    }
    if employment is not None:
        result['employment'] = employment
    return result


def payment_data(
        product_type,
        amount,
        payment_method,
        currency=None,
        product_id=None,
        payment_service=None,
        payment_terminal_id=None,
):
    details = {
        'product_type': product_type,
        'amount': amount,
        'payment_method': payment_method,
        'product_id': product_id or f'{product_type}__001',
    }
    if payment_service:
        details['payment_service'] = payment_service
    if payment_terminal_id:
        details['payment_terminal_id'] = payment_terminal_id
    if currency:
        details['currency'] = currency
    return details


def refund_data(
        product_type,
        amount,
        currency,
        payment_method,
        product_id=None,
        payment_service=None,
        payment_terminal_id=None,
):
    details = {
        'product_type': product_type,
        'amount': amount,
        'payment_method': payment_method,
        'product_id': product_id or f'{product_type}__001',
        'currency': currency,
    }
    if payment_service:
        details['payment_service'] = payment_service
    if payment_terminal_id:
        details['payment_terminal_id'] = payment_terminal_id
    return details


def commission_data(
        product_type,
        amount,
        product_id=None,
        currency=None,
        payment_service=None,
        commission_type=None,
):
    details = {
        'product_type': product_type,
        'amount': amount,
        'product_id': product_id or f'{product_type}__001',
        'currency': currency,
    }
    if payment_service:
        details['payment_service'] = payment_service
    if commission_type:
        details['type'] = commission_type
    return details


class TlogWriterTest:
    def __init__(self):
        self._order_nr = '123456-654321'
        self._rule = None
        self._transaction_date = '2021-10-25T17:15:00+00:00'
        self._billing_event = None
        self._billing_events = []
        self._expected_requests = []
        self._expect_fail = False
        self._async_fail = False
        self._times_called = 0
        self._billing_event_id = 1
        self._reverse = None
        self._patch = None
        self._check_tlog_flag = False

    def with_order_nr(self, order_nr):
        self._order_nr = order_nr
        return self

    def with_transaction_date(self, transaction_date):
        self._transaction_date = transaction_date
        return self

    def on_reverse(self):
        self._reverse = True
        return self

    def on_patch(self, patch):
        self._patch = patch
        return self

    def async_fail(self):
        self._async_fail = True
        self._times_called = 1
        return self

    def expect_no_request(self):
        self._times_called = 0
        return self

    def with_rule(self, rule):
        self._rule = rule
        return self

    def on_billing_event(
            self,
            client,
            payment=None,
            refund=None,
            commission=None,
            templates=None,
            payload=None,
            input_event_id=1,
    ):
        data = {
            'version': '2',
            'transaction_date': self._transaction_date,
            'external_payment_id': uuid.uuid4().hex,
            'client': client,
        }
        kind = None
        if payment is not None:
            kind = 'payment'
            data[kind] = payment
            data['product_type'] = payment['product_type']
        if refund is not None:
            if kind is not None:
                raise ValueError(
                    'Only one of payment, refund or commission allowed',
                )
            kind = 'refund'
            data[kind] = refund
            data['product_type'] = refund['product_type']
        if commission is not None:
            if kind is not None:
                raise ValueError(
                    'Only one of payment, refund or commission allowed',
                )
            kind = 'commission'
            data[kind] = commission
            data['product_type'] = commission['product_type']
        if kind is None:
            raise ValueError('payment, refund or commission expected')
        if templates is not None:
            data['templates'] = templates

        counter = len(self._billing_events) + 1

        if payload is not None:
            data['payload'] = payload

        self._billing_event = {
            'input_event_id': input_event_id,
            'order_nr': self._order_nr,
            'external_id': f'auto_{counter}',
            'kind': kind,
            'event_at': datetime.datetime(2021, 10, 25, 18, counter, 0, 0),
            'transaction_date': data['transaction_date'],
            'data': data,
        }

        return self

    def _add_transaction(self, transaction):
        detailed_product = transaction['detailed_product']
        dp_prefix = detailed_product.split('eats', 1)[1]
        service_prefix = SERVICES[transaction['service_id']]
        payment_kind = f'{service_prefix}{dp_prefix}'

        data = self._billing_event['data']
        if 'client_id' not in transaction.keys():
            transaction['client_id'] = data['client']['id']
        if 'contract_id' not in transaction.keys():
            transaction['contract_id'] = data['client']['contract_id']
        if 'mvp' not in transaction.keys():
            transaction['mvp'] = data['client']['mvp']
        if 'currency' not in transaction.keys():
            transaction['currency'] = data[self._billing_event['kind']][
                'currency'
            ]
        if 'payload' not in transaction.keys():
            transaction['payload'] = data.get('payload', {})
            if transaction['payload'] == {}:
                transaction['payload'] = {'product': data['product_type']}
        if 'original_event_time' not in transaction.keys():
            transaction['original_event_time'] = self._transaction_date
        if 'event_time' not in transaction.keys():
            transaction['event_time'] = self._transaction_date
        if 'external_ref' not in transaction.keys():
            transaction['external_ref'] = self._order_nr
        if 'payment_kind' not in transaction.keys():
            transaction['payment_kind'] = payment_kind
        if 'company_type' not in transaction.keys():
            transaction['company_type'] = COMPANY_TYPE[self._rule]
        if 'tags' in transaction.keys():
            tags = transaction.pop('tags')
        else:
            tags = f'eats/order_id/{self._order_nr}'

        order = {
            'data': {
                'event_version': 1,
                'payments': [transaction],
                'schema_version': 'v2',
                'template_entries': transaction.pop('template_entries', []),
                'topic_begin_at': transaction['original_event_time'],
            },
            'event_at': transaction['event_time'],
            'kind': 'arbitrary_payout',
            'tags': [tags],
        }
        self._expected_requests.append({'orders': [order]})
        self._times_called += 1

    def expect_payment(self, **payment):
        payment['transaction_type'] = 'payment'
        self._add_transaction(payment)
        return self

    def expect_refund(self, **refund):
        refund['transaction_type'] = 'refund'
        self._add_transaction(refund)
        return self

    def expect_fail(self):
        self._expect_fail = True
        return self

    def check_tlog_flag(self):
        self._check_tlog_flag = True
        return self

    async def run(self, fixture):
        if self._async_fail:
            fixture.billing_orders_mock.should_fail()

        cursor = fixture.pgsql['eats_billing_processor'].cursor()

        if self._rule is not None:
            cursor.execute(
                f"""update eats_billing_processor.input_events
                set rule_name = '{self._rule}'""",
            )
        event = self._billing_event
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

        await fixture.stq_runner.eats_billing_processor_tlog_writer.call(
            task_id='billing_1',
            kwargs={
                'order_nr': self._order_nr,
                'billing_event_id': self._billing_event_id,
                'reverse': self._reverse,
                'patch': self._patch,
            },
            expect_fail=self._expect_fail,
        )
        assert fixture.billing_orders_mock.times_called == self._times_called
        assert fixture.billing_orders_mock.requests == self._expected_requests

        if self._check_tlog_flag:
            cursor.execute(
                f"""select transactions_count
                from eats_billing_processor.order_accounting_correction""",
            )

            assert cursor.fetchone()[0] == 0

        if not self._expect_fail and self._expected_requests:
            cursor.execute(
                f"""select tlog_doc_id
                from eats_billing_processor.billing_events
                where tlog_doc_id is not null""",
            )

            db_docs = list(map(lambda x: x[0], cursor))
            docs = []
            for response in fixture.billing_orders_mock.responses:
                docs.extend(map(lambda x: x['doc_id'], response['orders']))

            assert db_docs == docs
