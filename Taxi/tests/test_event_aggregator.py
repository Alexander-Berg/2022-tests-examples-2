def test_event_throttling(load_json, get_pytest_signalq_config):
    import copy

    from signalq_pyml.processors import events
    from signalq_pyml.core import types

    config = get_pytest_signalq_config(cv='yandex', mode='testing')
    aggregator = events.EventAggregator(**config.pop('EventAggregator', {}))

    outputs = types.Outputs(
        events=[
            types.Event(
                source='EyeClose',
                payload=types.EventPayload(flag=True, score=0.9),
            ),
            types.Event(
                source='Distraction',
                payload=types.EventPayload(flag=True, score=0.9),
            ),
            types.Event(
                source='Smoking',
                payload=types.EventPayload(flag=True, score=0.9),
            ),
        ],
    )

    events = []
    for time in [10, 11, 15, 100, 1200]:
        aggregator.process(timestamp=time - 0.1, outputs=types.Outputs())
        events.extend(
            aggregator.process(
                timestamp=time, outputs=copy.deepcopy(outputs),
            ).events,
        )

    assert len(events) == 10


def test_negated_event(load_json, get_pytest_signalq_config):
    from signalq_pyml.processors import events
    from signalq_pyml.core import types

    config = get_pytest_signalq_config(cv='yandex', mode='testing')
    aggregator = events.EventAggregator(**config.pop('EventAggregator', {}))

    outputs = types.Outputs(
        events=[
            types.Event(
                source='Presence',
                payload=types.EventPayload(flag=True, score=0.9),
            ),
            types.Event(
                source='Presence',
                payload=types.EventPayload(flag=False, score=0.9),
            ),
        ],
    )

    events = aggregator.process(10.0, outputs).events

    assert events[0].name == 'driver_found'
    assert events[1].name == 'driver_lost'

    outputs = types.Outputs(
        events=[
            types.Event(
                source='PositioningPresence',
                payload=types.EventPayload(flag=True, score=0.9),
            ),
            types.Event(
                source='PositioningPresence',
                payload=types.EventPayload(flag=False, score=0.9),
            ),
        ],
    )

    events = aggregator.process(10.0, outputs).events

    assert events[0].name == 'driver_found_driving'
    assert events[1].name == 'driver_lost_driving'


def test_separate_threshold(load_json):
    import copy

    from signalq_pyml import get_config_path, compose_config
    from signalq_pyml.processors import events
    from signalq_pyml.core import types

    diff = load_json('config.json')
    base = load_json(get_config_path(cv='yandex', mode=None))
    config = compose_config(base, diff)

    aggregator = events.EventAggregator(**config['EventAggregator'])

    in_events = [
        types.Event(
            source='EyeClose',
            payload=types.EventPayload(
                flag=s / 10 > 0.3, score=s / 10, repeated=True,
            ),
        )
        for s in range(0, 20)
    ]

    in_events.extend(in_events[::-1])

    events = []
    for e, t in zip(in_events, range(len(in_events))):
        events.extend(
            aggregator.process(
                timestamp=t, outputs=copy.deepcopy(types.Outputs(events=[e])),
            ).events,
        )

    assert len(events) == 5
    assert all([e.payload.flag for e in events[1:4]])
    assert events[3].info.signal
    assert events[4].info.send and events[4].info.signal
    assert not events[4].payload.flag
