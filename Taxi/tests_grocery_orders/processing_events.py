def check_processing_event(processing, order_id, reason):
    events = list(processing.events(scope='grocery', queue='processing'))
    for event in events:
        if (
                event.payload.get('order_id', None) == order_id
                and event.payload.get('reason', None) == reason
        ):
            return event.payload
    return None
