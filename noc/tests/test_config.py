import pytest
from modules.config import Config


class TestConfig(object):
    FILENAME = "modules/tests/test_config.ini"

    @pytest.yield_fixture(autouse=True, scope="session")
    def config(self):
        config = Config(self.FILENAME, "Test")
        yield config

    @pytest.yield_fixture(autouse=True, scope="session")
    def empty_config(self):
        config = Config(self.FILENAME, "Empty")
        yield config

    def test_get_attr(self, config):
        assert (
            config.str("vip_description_filepath")
            == "/var/run/keepalived-*-desc.json"
        ), "received wrong vip_description_filepath"
        assert config.str("not_exist_value") is None, "not_exist_value exists"

    def test_get_bool_attr(self, config):
        assert isinstance(
            config.bool("export_service_mapping_wildcard_to_config"), bool
        ), "received non boolean type"
        assert config.bool(
            "export_service_mapping_wildcard_to_config"
        ), "export_service_mapping_wildcard_to_config is False"

    def test_get_int_attr(self, config):
        assert isinstance(
            config.int("mapping_update_interval"), int
        ), "received non int type"
        assert (
            config.int("mapping_update_interval") == 60
        ), "mapping_update_interval attr has wrong value"

    def test_get_float_attr(self, config):
        assert isinstance(
            config.float("vips_description_update_interval"), float
        ), "vips_description_update_interval is not float type"
        assert (
            config.float("active_consumers_update_interval") == 0.1
        ), "active_consumers_update_interval attr has wrong value"

    def test_is_route_originator(self, config, empty_config):
        assert config.is_route_originator(), "Test is not route originator"
        assert (
            not empty_config.is_route_originator()
        ), "Empty is route originator"

    def test_is_write_mapping_to_config(self, config, empty_config):
        assert (
            config.is_write_mapping_to_config()
        ), "Test has no attr write mapping to config"
        assert (
            not empty_config.is_write_mapping_to_config()
        ), "Empty has attr store mapping"

    def test_is_read_mapping_from_config(self, config, empty_config):
        assert (
            not config.is_read_mapping_from_config()
        ), "Test read mapping from config, but need from service_mapping_wildcard"
        assert (
            empty_config.is_read_mapping_from_config()
        ), "Empty doesn't read mapping from config"
