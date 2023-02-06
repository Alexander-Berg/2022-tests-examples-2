import pytest

from envoy.service.discovery.v3 import discovery_pb2 as proto

from scout import feature_config
from test_scout.web import conftest as root_conftest


DEFAULT_ZONE = 'sas'
DEFAULT_CLUSTER = 'taxi_tst_envoy-exp-alpha_testing'
DEFAULT_HOST = 'taxi-envoy-exp-alpha-testing-3.man.yp-c.yandex.net'
DEFAULT_CONFIG_NAME = 'SCOUT_FEATURE_CONFIG_SAMPLE'


@pytest.fixture(name='config_component')
def _config_component(web_context):
    try:
        root_conftest.PersistentStorage.rewrite_to_default()
        web_context.persistent_storage.load_fs_cache()
        yield web_context.feature_config
    finally:
        root_conftest.PersistentStorage.drop()
        web_context.persistent_storage.load_fs_cache()


@pytest.fixture(name='get_xds_request')
def _get_xds_request():
    def _wrapper(
            *, zone: str, cluster: str, host: str,
    ) -> proto.DiscoveryRequest:
        # disable false positive error
        # pylint: disable=no-member
        req = proto.DiscoveryRequest()

        req.node.id = host
        req.node.cluster = cluster
        req.node.locality.zone = zone

        return req

    return _wrapper


@pytest.fixture(name='get_sample_value')
def _get_sample_value(config_component, get_xds_request):
    def _wrapper(
            *,
            zone: str = DEFAULT_ZONE,
            cluster: str = DEFAULT_CLUSTER,
            host: str = DEFAULT_HOST,
            config_name: str = DEFAULT_CONFIG_NAME,
    ) -> bool:
        request = get_xds_request(zone=zone, cluster=cluster, host=host)
        config = config_component.get_config(config_name)

        value = config.get_value(request)
        assert isinstance(value, bool)

        return value

    return _wrapper


@pytest.fixture(name='get_sample_value_raising')
def _get_sample_value_raising(config_component, get_xds_request):
    def _wrapper(
            *,
            zone: str = DEFAULT_ZONE,
            cluster: str = DEFAULT_CLUSTER,
            host: str = DEFAULT_HOST,
            config_name: str = DEFAULT_CONFIG_NAME,
    ) -> bool:
        request = get_xds_request(zone=zone, cluster=cluster, host=host)
        config = config_component.get_config(config_name)

        try:
            value = config.get_value_raising(request)
        except Exception as exc:
            assert isinstance(exc, feature_config.HandleError)
            raise exc

        assert isinstance(value, bool)
        return value

    return _wrapper
