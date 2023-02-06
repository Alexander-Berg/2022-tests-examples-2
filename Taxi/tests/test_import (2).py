def test_import():
    from signalq_pyml import processors
    driver_state_processor_cls = processors.Runner  # noqa: F841


def test_init(load_json, get_pytest_signalq_config):
    import itertools

    from signalq_pyml import profiles
    from signalq_pyml import processors

    cv_choices = ['yandex']

    for cv, mode in itertools.product(cv_choices, profiles):
        config = get_pytest_signalq_config(cv=cv, mode=mode)
        processor = processors.Runner(config)
        assert 'FeatureAggregator' in processor.get_state_dict()
