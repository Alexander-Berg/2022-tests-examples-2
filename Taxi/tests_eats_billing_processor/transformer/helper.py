import datetime
import json
import uuid

from testsuite.utils import callinfo

from tests_eats_billing_processor.transformer import common

PLUS_CLIENT_ID = '82058879'

SERVICE_FEE_CLIENT_ID_RUB = '95332016'
SERVICE_FEE_CONTRACT_ID_RUB = '4469918'

SERVICE_FEE_CLIENT_ID_KZT = '97543252'
SERVICE_FEE_CONTRACT_ID_KZT = '5339448'

SERVICE_FEE_CLIENT_ID_BYN = '97543826'
SERVICE_FEE_CONTRACT_ID_BYN = '5339784'


def make_doc(doc_id, transaction):
    doc = {'doc_id': doc_id, 'data': {'payments': transaction}}
    return doc


class TransformerTest:
    def __init__(self, rule_name='default'):
        common.set_rule_name(rule_name)
        self._order_nr = '123456'
        self._transaction_date = '2021-07-10T09:22:00+00:00'
        self._event_date = '2021-07-14T09:30:00+00:00'
        self._delivered_at = '2021-07-20T12:35:00+00:00'
        self._order_finished_at = '2021-07-10T08:22:00+00:00'
        self._rule_name = rule_name
        self._currency = 'RUB'
        self._commissions = {}
        self._fines = {}
        self._client_info = {'places': {}, 'couriers': {}, 'pickers': {}}
        self._input_events = []
        self._billing_events = []
        self._transformer_args = {}
        self._expected_billing_events = []
        self._expected_stq_call = True
        self._expect_fail = False
        self._expected_accounts = []
        self._expected_fines = []
        self._expected_appeals = []
        self._expected_stq_call_id = 1
        self._should_reschedule = False
        self._expected_billing_orders_calls = 0
        self._docs = None

    def with_order_nr(self, order_nr):
        self._order_nr = order_nr
        return self

    def tlog_docs(self, docs):
        self._docs = docs
        return self

    def using_business_rules(
            self,
            place_id=None,
            courier_id=None,
            picker_id=None,
            client_id=None,
            client_info=None,
            fine=None,
            commission=None,
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
            if client_id is None:
                client_id = client_info['id']

        if commission is not None:
            if counterparty_id not in self._commissions.keys():
                self._commissions[counterparty_id] = {'client_id': client_id}
            assert self._commissions[counterparty_id]['client_id'] == client_id
            self._commissions[counterparty_id][commission['type']] = {
                'rule_id': (
                    commission['rule_id']
                    if commission['rule_id'] is not None
                    else f'commission_{client_id}_{commission["type"]}'
                ),
                'params': commission['params'],
                'billing_frequency': commission['billing_frequency'],
            }

        if fine is not None:
            if client_id not in self._fines.keys():
                self._fines[client_id] = {}
            self._fines[client_id][fine['type']] = {
                'rule_id': (
                    fine['rule_id']
                    if fine['rule_id'] is not None
                    else f'fine_{client_id}_{fine["type"]}'
                ),
                'params': fine['params'],
                'billing_frequency': fine['billing_frequency'],
            }

        return self

    def insert_input_event(
            self, kind, data, status='new', external_id=None, event_at=None,
    ):
        counter = len(self._input_events) + 1
        self._input_events.append(
            {
                'order_nr': self._order_nr,
                'external_id': (
                    external_id
                    if external_id is not None
                    else uuid.uuid4().hex
                ),
                'event_at': event_at or datetime.datetime(
                    2021, 7, 14, 12, counter, 0, 0,
                ),
                'kind': kind,
                'data': data,
                'status': status,
            },
        )
        return self

    def insert_billing_event(
            self, input_event_id, data, external_id=None, event_at=None,
    ):
        counter = len(self._billing_events) + 1
        self._billing_events.append(
            {
                'input_event_id': input_event_id,
                'order_nr': self._order_nr,
                'external_id': (
                    f'external_id_{counter}'
                    if not external_id
                    else external_id
                ),
                'kind': (
                    'payment'
                    if 'payment' in data.keys()
                    else 'refund'
                    if 'refund' in data.keys()
                    else 'commission'
                ),
                'event_at': event_at or datetime.datetime(
                    2021, 3, 26, 17, counter, 0, 0,
                ),
                'transaction_date': data['transaction_date'],
                'data': data,
            },
        )
        return self

    def on_order_cancelled(
            self,
            products,
            currency=None,
            is_payment_expected=False,
            is_reimbursement_required=False,
            courier_id=None,
            place_id=None,
            is_place_fault=False,
            picker_id=None,
            amount_picker_paid=None,
            external_id=None,
            order_type=None,
            service_fee_amount=None,
            order_cancel_id=None,
    ):
        optional_fields = {}
        if amount_picker_paid:
            optional_fields['amount_picker_paid'] = amount_picker_paid
        if service_fee_amount is not None:
            optional_fields['service_fee_amount'] = service_fee_amount
        self.insert_input_event(
            kind='order_cancelled',
            data={
                **{
                    'order_nr': self._order_nr,
                    'order_type': order_type or 'native',
                    'flow_type': 'retail',
                    'cancelled_at': self._event_date,
                    'transaction_date': self._transaction_date,
                    'order_cancel_id': order_cancel_id or '1',
                    'is_payment_expected': is_payment_expected,
                    'is_reimbursement_required': is_reimbursement_required,
                    'courier_id': courier_id,
                    'picker_id': picker_id,
                    'place_id': place_id,
                    'currency': currency or self._currency,
                    'is_place_fault': is_place_fault,
                    'products': products,
                },
                **optional_fields,
            },
            external_id=external_id,
        )
        return self

    def on_compensation(
            self,
            items,
            service_fee_amount=None,
            is_place_fault=False,
            courier_id=None,
            place_id=None,
            currency=None,
            picker_id=None,
            compensation_id=None,
    ):
        data = {
            'order_nr': self._order_nr,
            'flow_type': 'native',
            'is_place_fault': is_place_fault,
            'transaction_date': self._transaction_date,
            'compensation_id': compensation_id or '1',
            'courier_id': courier_id,
            'picker_id': picker_id,
            'place_id': place_id,
            'currency': currency or self._currency,
            'items': items,
            'order_finished_at': self._order_finished_at,
        }
        if service_fee_amount is not None:
            data['service_fee_amount'] = service_fee_amount
        self.insert_input_event(kind='compensation', data=data)
        return self

    def on_order_gmv(
            self,
            place_id,
            gmv_amount,
            special_commission_type=None,
            currency=None,
            dynamic_price=None,
    ):
        data = {
            'order_nr': self._order_nr,
            'transaction_date': self._transaction_date,
            'event_at': self._event_date,
            'place_id': place_id,
            'gmv_amount': gmv_amount,
            'currency': currency or self._currency,
            'operation_type': 'income',
            'fiscal_drive_number': 'fdn',
            'fiscal_document_number': 1,
            'fiscal_sign': 'fs',
        }
        if special_commission_type is not None:
            data['special_commission_type'] = special_commission_type
        if dynamic_price is not None:
            data['dynamic_price'] = dynamic_price
        self.insert_input_event(kind='order_gmv', data=data)
        return self

    def on_fine_appeal(
            self,
            fine_id,
            ticket,
            amount,
            product_type,
            product_id,
            place_id='123',
            fine_reason='refund',
            currency=None,
    ):
        data = {
            'order_nr': self._order_nr,
            'transaction_date': self._transaction_date,
            'fine_id': fine_id,
            'ticket': ticket,
            'amount': amount,
            'currency': currency or self._currency,
            'product_type': product_type,
            'product_id': product_id,
            'fine_reason': fine_reason,
            'place_id': place_id,
        }

        self.insert_input_event(kind='fine_appeal', data=data)
        return self

    def on_courier_earning(self, courier_id, details):
        data = {
            'order_nr': self._order_nr,
            'transaction_date': self._transaction_date,
            'courier_id': courier_id,
            'details': details,
        }

        self.insert_input_event(kind='courier_earning', data=data)
        return self

    def expect(self, *events):
        counter = len(self._expected_billing_events)

        def enrich(event):
            nonlocal counter
            if not event['external_payment_id']:
                event['external_payment_id'] = counter
            counter += 1
            details = (
                event['payment']
                if 'payment' in event.keys()
                else event['refund']
                if 'refund' in event.keys()
                else event['commission']
            )
            if 'currency' not in details.keys() or details['currency'] is None:
                details['currency'] = self._currency
            return event

        self._expected_billing_events.extend(map(enrich, events))
        return self

    def _get_external_payment_id(self, index):
        if index is None:
            return uuid.uuid4().hex

        if isinstance(index, int):
            return self._input_events[index + 1]['data']['external_payment_id']

        return str(index)

    def on_plus_cashback_emission(
            self,
            client_id,
            amount,
            flow_type=None,
            plus_cashback_amount_per_place='0',
            currency=None,
            payload=None,
            event_at=None,
    ):
        data = {
            'order_nr': self._order_nr,
            'event_at': self._transaction_date,
            'amount': amount,
            'amount_details': {
                'plus_cashback_amount_per_place': (
                    plus_cashback_amount_per_place
                ),
            },
            'currency': currency or self._currency,
            'client_id': client_id,
            'payload': payload or {},
        }
        if flow_type is not None:
            data['flow_type'] = flow_type

        self.insert_input_event(
            kind='plus_cashback_emission', data=data, event_at=event_at,
        )
        return self

    def on_receipt(self, place_id, amount, currency=None):
        counter = len(self._input_events) + 1
        self.insert_input_event(
            kind='receipt',
            data={
                'order_nr': self._order_nr,
                'transaction_date': self._transaction_date,
                'event_at': str(
                    datetime.datetime(2021, 4, 14, 12, counter, 0, 0),
                ),
                'place_id': place_id,
                'sum': amount,
                'currency': currency or self._currency,
                'operation_type': 'income',
                'fiscal_drive_number': 'fdn',
                'fiscal_document_number': 1,
                'fiscal_sign': 'fs',
            },
        )
        return self

    def on_order_delivered(
            self,
            products,
            currency=None,
            service_fee_amount=None,
            place_compensations=None,
            picker_id=None,
            courier_id=None,
            place_id=None,
            flow_type='retail',
    ):
        data = {
            'order_nr': self._order_nr,
            'flow_type': flow_type,
            'transaction_date': self._transaction_date,
            'delivered_at': self._delivered_at,
            'picker_id': picker_id,
            'courier_id': courier_id,
            'place_id': place_id,
            'currency': currency or self._currency,
            'products': products,
        }
        if service_fee_amount is not None:
            data['service_fee_amount'] = service_fee_amount
        if place_compensations is not None:
            data['place_compensations'] = place_compensations
        self.insert_input_event(kind='order_delivered', data=data)
        return self

    def on_payment_not_received(
            self,
            products,
            picker_id=None,
            courier_id=None,
            place_id=None,
            currency=None,
            external_payment_id=None,
            order_type=None,
            flow_type='retail',
    ):
        self.insert_input_event(
            kind='payment_not_received',
            data={
                'order_nr': self._order_nr,
                'transaction_date': self._transaction_date,
                'external_payment_id': self._get_external_payment_id(
                    external_payment_id,
                ),
                'payment_not_received_at': self._event_date,
                'courier_id': courier_id,
                'picker_id': picker_id,
                'place_id': place_id,
                'payment_type': 'card',
                'payment_terminal_id': 'termimal_1',
                'currency': currency or self._currency,
                'flow_type': flow_type,
                'products': products,
                'order_type': order_type,
            },
        )
        return self

    def on_payment_received(
            self,
            counteragent_id,
            product_type,
            amount,
            client_id=None,
            currency=None,
            product_id=None,
            external_payment_id=None,
            order_type=None,
            flow_type='retail',
    ):
        data = {
            'order_nr': self._order_nr,
            'transaction_date': self._transaction_date,
            'external_payment_id': self._get_external_payment_id(
                external_payment_id,
            ),
            'amount': amount,
            'currency': currency or self._currency,
            'client_id': client_id,
            'payment_method': 'card',
            'payment_terminal_id': 'terminal_1',
            'counteragent_id': counteragent_id,
            'product_type': product_type,
            'product_id': (product_id or common.make_product_id(product_type)),
            'transaction_type': 'payment',
            'flow_type': flow_type,
        }
        if order_type is not None:
            data['order_type'] = order_type
        self.insert_input_event(kind='payment_received', data=data)
        return self

    def on_payment_refund(
            self,
            counteragent_id,
            product_type,
            amount,
            client_id=None,
            currency=None,
            external_payment_id=None,
            order_type=None,
            flow_type='retail',
    ):
        data = {
            'order_nr': self._order_nr,
            'transaction_date': self._transaction_date,
            'external_payment_id': self._get_external_payment_id(
                external_payment_id,
            ),
            'amount': amount,
            'currency': currency or self._currency,
            'client_id': client_id,
            'payment_method': 'card',
            'payment_terminal_id': 'terminal_1',
            'counteragent_id': counteragent_id,
            'product_type': product_type,
            'product_id': common.make_product_id(product_type),
            'transaction_type': 'refund',
            'flow_type': flow_type,
        }
        if order_type is not None:
            data['order_type'] = order_type
        self.insert_input_event(kind='payment_refund', data=data)
        return self

    def on_payment_update_plus_cashback(
            self,
            client_id,
            amount,
            payment_method,
            product_type,
            currency=None,
            product_id=None,
            payload=None,
            processing_type=None,
            event_at=None,
            counteragent_id=None,
    ):
        self.insert_input_event(
            kind='payment_update_plus_cashback',
            data={
                'order_nr': self._order_nr,
                'transaction_date': self._transaction_date,
                'amount': amount,
                'currency': currency or self._currency,
                'client_id': client_id,
                'event_at': self._event_date,
                'payment_method': payment_method,
                'counteragent_id': counteragent_id or '1',
                'product_type': product_type,
                'product_id': (
                    product_id or common.make_product_id(product_type)
                ),
                'transaction_type': 'plus_update',
                'flow_type': 'retail',
                'order_type': 'native',
                'processing_type': processing_type,
                'payload': payload or {},
            },
            event_at=event_at,
        )
        return self

    def on_additional_promo_payment(
            self, amount, place_id, currency=None, promo_id='promo_id',
    ):
        self.insert_input_event(
            kind='additional_promo_payment',
            data={
                'order_nr': self._order_nr,
                'transaction_date': self._transaction_date,
                'amount': amount,
                'currency': currency or self._currency,
                'place_id': place_id,
                'promo_id': promo_id,
            },
        )
        return self

    def on_rerun(self, fix_event_id, disable_reverse=None, rule_override=None):
        self._transformer_args['fix_event_id'] = fix_event_id
        if disable_reverse is not None:
            self._transformer_args['disable_reverse'] = disable_reverse
        if rule_override is not None:
            self._transformer_args['rule_override'] = rule_override
        return self

    def expected_fail(self):
        self._expect_fail = True
        return self

    def no_stq_call_expected(self):
        self._expected_stq_call = False
        return self

    def expect_billing_events(self, events):
        self._expected_billing_events = events
        return self

    def expect_stq_call_id(self, call_id):
        self._expected_stq_call_id = call_id
        return self

    def expect_accounting(self, client_id, account_type, amount):
        self._expected_accounts.append((client_id, account_type, amount))
        return self

    def expect_fine(
            self,
            client_id,
            fine_reason,
            actual_amount,
            calculated_amount,
            currency='RUB',
            fine_reason_id=1,
    ):
        external_id = f'{self._order_nr}/{fine_reason_id}'
        self._expected_fines.append(
            (
                self._order_nr,
                client_id,
                fine_reason,
                actual_amount,
                calculated_amount,
                currency,
                external_id,
                fine_reason_id,
            ),
        )
        return self

    def expect_appeal(self, fine_id, ticket, amount):
        self._expected_appeals.append((fine_id, ticket, amount))
        return self

    def should_reschedule(self):
        self._should_reschedule = True
        return self

    def expect_billing_orders_call(self, times_called=1):
        self._expected_billing_orders_calls = times_called
        return self

    async def run(self, fixtures):
        fixtures.business_rules_mock(self._commissions, self._fines)
        fixtures.client_info_mock(self._client_info)

        if self._expect_fail:
            fixtures.billing_reports_mock.should_fail()
        else:
            fixtures.billing_reports_mock.docs(self._docs)

        cursor = fixtures.pgsql['eats_billing_processor'].cursor()
        for event in self._input_events:
            cursor.execute(
                f"""insert into eats_billing_processor.input_events
                (order_nr, external_id, event_at,
                kind, data, status, rule_name)
                values ('{event['order_nr']}', '{event['external_id']}',
                        '{event['event_at']}', '{event['kind']}',
                        '{json.dumps(event['data'])}',
                        '{event['status']}', '{self._rule_name}')""",
            )

        for event in self._billing_events:
            data = event['data']
            details = data[event['kind']]
            cursor.execute(
                f"""insert into eats_billing_processor.billing_events
                 (input_event_id, order_nr, external_id, kind, event_at,
                  transaction_date, external_payment_id, client_id,
                  product_type, amount, currency, data, business_rules_id)
                 values ({event['input_event_id']}, '{self._order_nr}',
                         '{event['external_id']}', '{event['kind']}',
                         '{event['event_at']}', '{event['transaction_date']}',
                         '{data['external_payment_id']}',
                         '{data['client']['id']}', '{details['product_type']}',
                          {details['amount']}, '{details['currency']}',
                         '{json.dumps(event['data'])}', 'N/A')""",
            )

        self._transformer_args['order_nr'] = self._order_nr
        await fixtures.stq_runner.eats_billing_processor_transformer.call(
            task_id='trans_1',
            kwargs=self._transformer_args,
            expect_fail=self._expect_fail,
        )

        try:
            call_info = (
                fixtures.stq.eats_billing_processor_transformer.next_call()
            )
            assert self._should_reschedule
            assert call_info['id'] == 'trans_1'
        except callinfo.CallQueueEmptyError:
            assert not self._should_reschedule

        cursor.execute(
            f"""select data from eats_billing_processor.billing_events
             where order_nr='{self._order_nr}' and status='new'""",
        )
        billing_events = list(row[0] for row in cursor)
        assert len(billing_events) == len(self._expected_billing_events)

        external_payment_ids = []
        for event in billing_events:
            external_payment_ids.append(event['external_payment_id'])
        for event in self._expected_billing_events:
            if isinstance(event['external_payment_id'], int):
                event['external_payment_id'] = external_payment_ids[
                    event['external_payment_id']
                ]
        assert billing_events == self._expected_billing_events

        cursor.execute(
            f"""
            select client_id, name, cast(amount as text) as amount
            from eats_billing_processor.accounts
            """,
        )

        def key(x):
            return f'{x[0]}_{x[1]}'

        result_accounts = list(cursor)
        assert sorted(result_accounts, key=key) == sorted(
            self._expected_accounts, key=key,
        )

        cursor.execute(
            f"""select order_nr, client_id,
            cast(fine_reason as text) as fine_reason,
            cast(actual_amount as text) as actual_amount,
            cast(calculated_amount as text) as calculated_amount,
            currency, external_id, fine_reason_id
            from eats_billing_processor.fines
            where order_nr='{self._order_nr}'""",
        )
        result_fines = list(cursor)
        assert result_fines == self._expected_fines

        cursor.execute(
            f"""select cast(fine_id as text) as fine_id,
            ticket, cast(amount as text) as amount
            from eats_billing_processor.appeals""",
        )
        result_appeals = list(cursor)
        assert result_appeals == self._expected_appeals

        if self._expected_stq_call:
            stq = fixtures.stq.eats_billing_processor_billing_processor
            call_info = stq.next_call()
            assert call_info['id'] == f'billing_{self._expected_stq_call_id}'
            assert (
                call_info['queue']
                == 'eats_billing_processor_billing_processor'
            )

            kwargs = call_info['kwargs']
            kwargs.pop('log_extra')
            assert kwargs == {'order_nr': self._order_nr}

        assert (
            fixtures.billing_orders_mock.times_called
            == self._expected_billing_orders_calls
        )
