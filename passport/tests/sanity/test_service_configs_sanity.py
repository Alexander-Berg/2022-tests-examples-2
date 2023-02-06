# -*- coding: utf-8 -*-
from passport.backend.takeout.common.conf.services import ServiceConfig
import pytest
import yaml
import yatest.common


SERVICE_CONFIG_FILES = [
    'passport/backend/takeout/configs/services-development.yaml',
    'passport/backend/takeout/configs/services-testing.yaml',
    'passport/backend/takeout/configs/services-production.yaml',
]


@pytest.mark.parametrize(
    'filename',
    SERVICE_CONFIG_FILES,
)
def test_all_service_configs_have_required_fields(filename):
    with open(yatest.common.source_path(filename)) as f:
        config_file_contents = yaml.safe_load(f)

    for service_name, service_dict in config_file_contents['services'].items():
        service_config = ServiceConfig.from_dict(service_dict)
        debug_message = '%s (%s)' % (service_name, service_dict)

        assert service_config.url_base, debug_message
        if service_config.type == 'sync':
            assert service_config.url_suffix_start is None, debug_message
            assert service_config.url_suffix_get is not None, debug_message
        elif service_config.type == 'async':
            assert service_config.url_suffix_start is not None, debug_message
            assert service_config.url_suffix_get is not None, debug_message
        elif service_config.type == 'async_upload':
            assert service_config.url_suffix_start is not None, debug_message
            assert service_config.url_suffix_get is None, debug_message
        else:
            assert False, debug_message  # noqa
