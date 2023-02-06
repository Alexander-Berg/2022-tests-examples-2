def test_force_recompute(load_json):
    from signalq_pyml import get_config_path
    from signalq_pyml.processors import features
    from signalq_pyml.core import types

    config_path = get_config_path(cv='yandex', mode='testing')
    config: dict = load_json(config_path)

    aggregator_config = config.pop('FeatureAggregator', {})
    aggregator = features.FeatureAggregator(**aggregator_config)

    outputs = types.Outputs(
        events=[
            types.Event(
                source='Yawn', payload=types.EventPayload(flag=True, score=9),
            ),
            types.Event(
                source='AdaptiveBlink',
                payload=types.EventPayload(flag=True, score=9, duration=0.04),
            ),
        ],
    )

    empty = types.Outputs([])

    for seq_no in range(0, 152):
        if seq_no % 30 == 0:
            aggregator.process(
                timestamp=seq_no / 30, outputs=outputs, force=True,
            )
        else:
            aggregator.process(
                timestamp=seq_no / 30, outputs=empty, force=True,
            )

    assert len(aggregator.state.cache)


def test_extractor():

    from signalq_pyml.core import types
    from signalq_pyml.processors import extractors as e
    from signalq_pyml.processors.extractors import aggregations as ea

    event = types.Event(
        source='LongBlink', payload=types.EventPayload(flag=True, score=0.95),
    )

    extractor = e.TimeGridExtractor(
        source='LongBlink',
        window_length=3600,
        measure_period=30,
        grid_step=300,
        default=0.0,
        getter=e.default,
        grid_agg=ea.cell_not_empty,
        aggregators=[
            ea.grid_counter(3, 0),
            ea.grid_counter(3, 3),
            ea.grid_counter(3, 6),
        ],
    )

    frequency = 147

    for num in range(2500):
        act_event = None
        if num % frequency == 0 and num != 0:
            act_event = event

        extractor.process(num / 2, act_event)

    checks = {
        'long_blink/default/time_grid/3600/300/grid_counter_0_3': 3.0,
        'long_blink/default/time_grid/3600/300/grid_counter_3_3': 1.0,
        'long_blink/default/time_grid/3600/300/grid_counter_6_3': 0.0,
    }

    assert all(
        extractor.state.cache.contained[k] == v for k, v in checks.items()
    )
