# flake8: noqa
# pylint: disable=import-error,wildcard-import
from market_uaccess_plugins.generated_tests import *

# Feel free to provide your custom implementation to override generated tests.
async def test_echo(taxi_market_uaccess):
    text = 'Hello, Market!!!!111'
    response = await taxi_market_uaccess.get('echo?text-param={}'.format(text))
    assert response.status_code == 200
    assert response.json() == {'payload': text}


async def test_echo_validation(taxi_market_uaccess):
    text = 'H' * 51
    response = await taxi_market_uaccess.get('echo?text-param={}'.format(text))
    assert response.status_code == 400
