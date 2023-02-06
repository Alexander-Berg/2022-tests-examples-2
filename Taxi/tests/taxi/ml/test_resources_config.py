from taxi.ml import resources_config


def test_config(get_file_path):
    config = resources_config.ResourcesConfig(get_file_path('resources.yaml'))

    assert len(config.handlers) == 2
    assert config.handlers[0].url_path == '/drivers_tickets_tagging/v1'
    assert len(config.handlers[1].resources) == 1
    assert config.handlers[1].resources[0].path == 'autoreply/autoreply'
    assert config.paths_by_name('/autoreply/v1') == ['autoreply/autoreply']


def test_meta(get_file_path):
    meta = resources_config.ResourceMeta(get_file_path('resource_meta.yaml'))

    assert meta.name == 'autoreply'
    assert meta.type == 'autoreply'
    assert meta.version_maj == '3'
    assert meta.version_min == '2'
