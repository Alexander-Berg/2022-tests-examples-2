# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from taximeter_proxy_plugins.generated_tests import *  # noqa


async def test_ping_auth(taxi_taximeter_proxy):
    response = await taxi_taximeter_proxy.get('ping-auth')
    assert response.status_code == 200
    assert response.content == b''
