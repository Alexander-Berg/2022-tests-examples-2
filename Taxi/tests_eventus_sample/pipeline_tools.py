def create_event(ev_id):
    return {
        'some_id': f'order_id_{ev_id}',
        'some_index': ev_id,
        'event_key': f'event_key_{ev_id}',
        'user_phone_id': f'user_phone_id_{ev_id}',
        'user_id': f'user_id_{ev_id}',
        'nz': f'nz_{ev_id}',
        'status_updated': 1571253356.368,
        'field_test_1': 'asdasd',
        'field_test_2': 'asdasdasd',
    }
