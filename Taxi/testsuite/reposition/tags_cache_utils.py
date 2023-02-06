def create_tags_cache_config(
        enable: bool = True, dump_restore_enabled: bool = False,
):
    return {
        '__default__': {
            'enabled': enable,
            'dump_restore_enabled': dump_restore_enabled,
        },
    }


def change_tags_cache_config(
        config, enable: bool, dump_restore_enabled: bool = False,
):
    config.set_values(
        dict(
            TAGS_CACHE_SETTINGS=create_tags_cache_config(
                enable, dump_restore_enabled,
            ),
        ),
    )
