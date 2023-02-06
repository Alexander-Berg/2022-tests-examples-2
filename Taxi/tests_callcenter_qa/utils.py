def get_aggregator_config(
        feedback_type_to_settings, period=30000, cfg_enabled=True,
):
    config = {
        'enabled': cfg_enabled,
        'period': period,
        'aggregation_settings': {},
    }
    for feedback_type, settings in feedback_type_to_settings.items():
        config['aggregation_settings'][feedback_type] = {
            'processors': (
                settings['processors'] if settings.get('processors') else None
            ),
            'thresholds': (
                settings['thresholds'] if settings.get('thresholds') else None
            ),
            'filters': (
                settings['filters'] if settings.get('filters') else None
            ),
            'upload_settings': {
                'interval': (
                    settings['upload_interval']
                    if settings.get('upload_interval')
                    else 600  # 10m
                ),
            },
        }

    return config
