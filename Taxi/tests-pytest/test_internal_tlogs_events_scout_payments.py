# -*- coding: utf-8 -*-

import datetime

import pytest

from taxi.core import async
from taxi.internal.tlogs_events import scout_payments as events

from taxi.internal.scout_payments import helper as scout_helper


@pytest.mark.parametrize(
    'last_created_at, selected_rows, expected_event_for_billing_orders', [
        (
            datetime.datetime(2018, 8, 6),
            {
                'bank_order_id': '685306',
                'credit': None,
                'created': 1554881600,
                'currency': 'RUB',
                'debet': 5000000,
                'description': 'П\п № 111111',
                'payload': {
                    'db': 'da3dda721d8d461fa076665ea69767c0',
                    'scout_id': 'drusskikhkrd',
                    'scout_name': 'Иванов Иван Иванович',
                    'transaction_id': '002a88c1c251a4480e1e8822fcddd27e',
                    'uuid': 'aa462cd019da530cd0aedcc7cf23c0fa'
                },
                'trust_payment_id': '002a88c1c251a4480e1e8822fcddd27e',
                'trust_refund_id': None,
                'bank_order_created': 1554152400
            },
            {
                'kind': 'scout_payment',
                'external_obj_id':
                    'taxi/scout_payment/'
                    '0d6445f08a0e117dc715eb9f85e00fad98a2e117',
                'external_event_ref':
                    'taxi/scout_payment/'
                    '0d6445f08a0e117dc715eb9f85e00fad98a2e117',
                'event_at': '2019-04-10T07:33:20+00:00',
                'data': {
                    'scout_info': {
                        'driver': {
                            'db_id': 'da3dda721d8d461fa076665ea69767c0',
                            'driver_uuid': 'aa462cd019da530cd0aedcc7cf23c0fa'
                        },
                        'scout_id': 'drusskikhkrd',
                        'scout_name': 'Иванов Иван Иванович'
                    },
                    'scout_payment_info': {
                        'amount': '500',
                        'currency': 'RUB',
                        'description': 'П\п № 111111',
                        'transaction_id': '002a88c1c251a4480e1e8822fcddd27e',
                        'bank_order_id': '685306',
                        'trust_payment_id': '002a88c1c251a4480e1e8822fcddd27e',
                        'trust_refund_id': None,
                        'bank_order_created': 1554152400,
                    },
                    'transaction_id':
                        '0d6445f08a0e117dc715eb9f85e00fad98a2e117',
                    'write_real_journal_for_taximeter': False
                },
                'reason': ''
            }
        ),
        (
            datetime.datetime(2018, 8, 6),
            {
                'bank_order_id': '685306',
                'credit': None,
                'created': 1554881600,
                'currency': 'RUB',
                'debet': 5000000,
                'description': 'П\п № 111111',
                'payload': {
                    'db': 'da3dda721d8d461fa076665ea69767c0',
                    'scout_id': 'drusskikhkrd',
                    'transaction_id': '002a88c1c251a4480e1e8822fcddd27e',
                    'uuid': 'aa462cd019da530cd0aedcc7cf23c0fa'
                },
                'trust_payment_id': '002a88c1c251a4480e1e8822fcddd27e',
                'trust_refund_id': None,
                'bank_order_created': 1554152400
            },
            {
                'kind': 'scout_payment',
                'external_obj_id':
                    'taxi/scout_payment/'
                    '0d6445f08a0e117dc715eb9f85e00fad98a2e117',
                'external_event_ref':
                    'taxi/scout_payment/'
                    '0d6445f08a0e117dc715eb9f85e00fad98a2e117',
                'event_at': '2019-04-10T07:33:20+00:00',
                'data': {
                    'scout_info': {
                        'driver': {
                            'db_id': 'da3dda721d8d461fa076665ea69767c0',
                            'driver_uuid': 'aa462cd019da530cd0aedcc7cf23c0fa'
                        },
                        'scout_id': 'drusskikhkrd',
                        'scout_name': None
                    },
                    'scout_payment_info': {
                        'amount': '500',
                        'currency': 'RUB',
                        'description': 'П\п № 111111',
                        'transaction_id': '002a88c1c251a4480e1e8822fcddd27e',
                        'bank_order_id': '685306',
                        'trust_payment_id': '002a88c1c251a4480e1e8822fcddd27e',
                        'trust_refund_id': None,
                        'bank_order_created': 1554152400,
                    },
                    'transaction_id':
                        '0d6445f08a0e117dc715eb9f85e00fad98a2e117',
                    'write_real_journal_for_taximeter': False
                },
                'reason': ''
            }
        ),
    ])
@pytest.mark.config(
    TLOGS_EVENTS_SLEEP_BEFORE_SEND=0,
    TLOGS_EVENTS_SLEEP_BETWEEN_SEND=0,
    TLOGS_EVENTS_SLEEP_BETWEEN_CHUNKS=0,
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_events_processor(
        patch, last_created_at, selected_rows,
        expected_event_for_billing_orders):
    yield events._INFO.event_monitor(last_created_at=last_created_at)

    @patch('taxi.internal.scout_payments.helper.find_scout_payments')
    @async.inline_callbacks
    def find_scout_payments(*args, **kwargs):
        yield
        rows = [selected_rows]
        async.return_value(rows)

    @patch('taxi.external.billing_orders.send_doc')
    def send_doc(kind, external_obj_id, external_event_ref, event_at, data,
                 reason, **kwargs):
        actual_event = {
            'kind': kind,
            'external_obj_id': external_obj_id,
            'external_event_ref': external_event_ref,
            'event_at': event_at,
            'data': data,
            'reason': reason
        }
        assert actual_event == expected_event_for_billing_orders

    events_processor = events.EventsProcessor()
    yield events_processor.process_new_events()


@pytest.mark.parametrize(
    'query_parameters, expected_query', [
        (
            {
                'pbl_fields': ['csv_updated as created', 'debet', 'credit'],
                'table_pbl': '//home/test_pbl',
                'table_index':'//home/test_index',
                'start':1554881677,
                'end':1554881600
            },
            'csv_updated as created, debet, credit '
            'FROM [//home/test_index] as index JOIN [//home/test_pbl] '
            'ON (index.alias_id, index.payment_type, index.trust_payment_id, '
            'index.trust_refund_id) = '
            '(alias_id, payment_type, trust_payment_id,'
            ' trust_refund_id) WHERE index.csv_updated >= 1554881677 '
            'AND index.csv_updated < 1554881600 '
            'AND index.csv_updated = csv_updated'
        )
    ]
)
@pytest.mark.asyncenv('blocking')
def test_yt_query(query_parameters, expected_query):
    yt_query = scout_helper._get_yt_query(
        pbl_fields=query_parameters['pbl_fields'],
        table_pbl=query_parameters['table_pbl'],
        table_index=query_parameters['table_index'],
        start=query_parameters['start'],
        end=query_parameters['end']
    )
    assert yt_query == expected_query
