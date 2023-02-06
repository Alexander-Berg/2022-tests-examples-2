def _event_sort_key(event):
    return event['event'] + event.get('event_id', '')


def prepare_response(response):
    # remove volatile fields and sort lists
    assert 'events' in response
    events = response['events']
    assert 'updated' in events
    assert 'expired' in events

    for event in events['updated']:
        assert 'version' in event
        del event['version']

    events['updated'].sort(key=_event_sort_key)
    events['expired'].sort(key=_event_sort_key)

    return response
