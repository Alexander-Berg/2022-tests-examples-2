import itertools
import json
import pytest


from taxi_maintenance.stuff import (
    yt_upload_partner_payments_reports as reports_upload
)


PARKS_MAP = {'clid1': 'db_id1'}


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'input_rows_file,input_keys_file,expected_rows,reducer', [
        (
            'input_rows.json',
            None,
            [{'subvention': None, 'db_id': 'db_id1', 'currency': u'RUB',
              'park_id': u'clid1', 'id': u'345', 'payment_batch_id': 1,
              'ride': '900', 'created': 1521019900, 'total_delta': 356,
              'cancelled': False, 'tips': None, 'bank_order_id': u'32123'},
             {'subvention': None, 'db_id': 'db_id1', 'currency': u'RUB',
              'park_id': u'clid1', 'id': u'345', 'payment_batch_id': 1,
              'ride': '163', 'created': 1521019825, 'total_delta': 356,
              'cancelled': False, 'tips': None, 'bank_order_id': None}],
            reports_upload._PartnerPaymentsReducer(PARKS_MAP),
        ),
        (
            'input_rows_with_refund.json',
            None,
            [{'subvention': None, 'db_id': 'db_id1', 'currency': u'RUB',
              'park_id': u'clid1', 'id': u'345', 'payment_batch_id': 1,
              'ride': '900', 'created': 1521019825, 'total_delta': 356,
              'cancelled': False, 'tips': None, 'bank_order_id': None}],
            reports_upload._PartnerPaymentsReducer(PARKS_MAP),
        ),
        (
            'input_rows_for_reducer_by_orders.json',
            None,
            [{'@table_index': 0,
              'address_from_street': u'street_from',
              'bank_order_id': '123',
              'cancelled': False,
              'created': 1521019825,
              'currency': u'RUB',
              'date_booking': 1504137600,
              'db_id': u'db_id1',
              'id': u'345',
              'number': 123,
              'park_id': u'clid1',
              'payment_batch_id': 1,
              'ride': u'900',
              'subvention': None,
              'tips': None,
              'total_delta': 356}],
            reports_upload._reduce_by_orders,
        ),
        (
            'input_rows_for_reducer_by_batches.json',
            'input_keys_for_reducer_by_batches.json',
            [{
                'subvention': '0',
                'commission': '-544',
                'bank_order_id': '123',
                'ride': '900',
                'some': 'data',
                'tobe': 'updated',
                'currency': 'RUB',
                'total_delta': 356,
                'park_id': 'clid1',
                'cancelled': False,
                'tips': '0'}],
            reports_upload._reduce_by_batches,
        ),

    ]
)
@pytest.mark.asyncenv('blocking')
def test_reducer(load, input_rows_file, input_keys_file,
                 expected_rows, reducer):
    input_rows = json.loads(load(input_rows_file))
    if input_keys_file:
        input_keys = json.loads(load(input_keys_file))
    else:
        input_keys = itertools.repeat(None)
    actual_rows = []
    for key, row_group in itertools.izip(input_keys, input_rows):
        actual_rows.extend(list(reducer(key, row_group)))
    assert actual_rows == expected_rows
