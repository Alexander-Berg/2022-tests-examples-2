import datetime as dt

_REBILL_EVENT_AT = dt.datetime(2019, 10, 8, 7, 0, 1, tzinfo=dt.timezone.utc)
_REBILL_CREATED = dt.datetime(2019, 10, 8, 7, 0, 2, tzinfo=dt.timezone.utc)
_REBILL_PROCESS_AT = dt.datetime(2019, 10, 8, 7, 0, 3, tzinfo=dt.timezone.utc)


def input_rebill_order():
    doc = _common_rebill_order()
    doc['external_obj_id'] = 'taxi/rebill_order/some_alias_id'
    doc['event_at'] = _format_input_datetime(_REBILL_EVENT_AT)
    doc['created'] = _format_input_datetime(_REBILL_CREATED)
    doc['process_at'] = _format_input_datetime(_REBILL_PROCESS_AT)
    return doc


def output_rebill_order():
    doc = _common_rebill_order()
    doc['topic'] = 'taxi/rebill_order/some_alias_id'
    doc['event_at'] = _format_output_datetime(_REBILL_EVENT_AT)
    doc['created'] = _format_output_datetime(_REBILL_CREATED)
    doc['process_at'] = _format_output_datetime(_REBILL_PROCESS_AT)
    return doc


def _common_rebill_order():
    return {
        'doc_id': 875911250037,
        'kind': 'rebill_order',
        'external_event_ref': 'updated/2019-10-08T07:00:01.000000+00:00',
        'data': {
            'order': {
                'alias_id': 'some_alias_id',
                'due': '2019-01-02T00:00:00.000000+00:00',
                'id': 'some_order_id',
                'version': 5,
                'zone_name': 'moscow',
            },
            'reason': {
                'data': {'ticket_id': '71597475', 'ticket_type': 'zendesk'},
                'kind': 'cost_changed',
            },
        },
        'service': 'billing-orders',
        'tags': [
            'system://parent_doc_id/4294967296',
            'taxi/alias_id/some_alias_id',
            'taxi/entity_id/taximeter_driver_id/some_db_id/some_uuid',
            'taxi/shift_ended/unique_driver_id/'
            '5bab4bf979b9e5513fe5ec4a/2020-02-26/nmfg',
        ],
        'status': 'complete',
    }


def _format_input_datetime(datetime):
    return datetime.isoformat(timespec='microseconds')


def _format_output_datetime(datetime):
    return datetime.isoformat()
