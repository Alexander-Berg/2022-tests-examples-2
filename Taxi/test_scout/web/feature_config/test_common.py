from scout import feature_config


async def test_no_config(get_sample_value):
    value = get_sample_value(config_name='NON_EXISTENT_CONFIG')
    assert value is False


async def test_no_config_raising(get_sample_value_raising):
    try:
        get_sample_value_raising(config_name='NON_EXISTENT_CONFIG')
        assert False, 'Assert should never happen'
    except feature_config.HandleError:
        pass


async def test_config_update(get_sample_value, taxi_config, web_context):
    value = get_sample_value()
    assert value is False

    taxi_config.set(
        SCOUT_FEATURE_CONFIG_SAMPLE={'type': 'const', 'value': True},
    )
    await web_context.refresh_caches()

    new_value = get_sample_value()
    assert new_value is True


async def test_config_update_raising(
        get_sample_value_raising, taxi_config, web_context,
):
    value = get_sample_value_raising()
    assert value is False

    taxi_config.set(
        SCOUT_FEATURE_CONFIG_SAMPLE={'type': 'const', 'value': True},
    )
    await web_context.refresh_caches()

    new_value = get_sample_value_raising()
    assert new_value is True
