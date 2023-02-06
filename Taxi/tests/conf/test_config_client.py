import pytest
import mock

from conf.config import ConfigClient
from lib import exceptions

RESPONSE_DICT = {
    u'configs': {u'ATLAS_FOODTECH_MONITORING':
                     {u'native_delivery_delay': 150,
                      u'fast_food_delivery_delay': 210,
                      u'store_delivery_delay': 48}},
    u'updated_at': u'2019-12-23T21:50:36.619Z'
}


class TestConfigClient:
    def test_base_config(self):
        client = ConfigClient()
        assert client.BASE['app']['deliveries']['database'] is not None

        with pytest.raises(KeyError):
            client.BASE['nonexistent_key']

    @mock.patch.object(
        ConfigClient, '_request_config_part', lambda self, name: RESPONSE_DICT
    )
    def test_remote_config(self):
        client = ConfigClient()

        assert client.ATLAS_FOODTECH_MONITORING == RESPONSE_DICT['configs']['ATLAS_FOODTECH_MONITORING']

        with pytest.raises(KeyError):
            client.ATLAS_FOODTECH_MONITORING['nonexistent_key']

    def test_remote_config_does_not_exist(self):
        client = ConfigClient()

        with pytest.raises(exceptions.ConfigError):
            client.NONEXISTENT_CONFIG
