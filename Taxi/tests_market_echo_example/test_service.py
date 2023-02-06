# flake8: noqa
# pylint: disable=import-error,wildcard-import
from market_echo_example_plugins.generated_tests import *
import pytest


async def test_echo(taxi_market_echo_example):
    text = 'Hello, Market!!!!111'
    response = await taxi_market_echo_example.get(
        'echo?text-param={}'.format(text),
    )
    assert response.status_code == 200
    assert response.json() == {'payload': text}


async def test_echo_validation(taxi_market_echo_example):
    text = 'H' * 51
    response = await taxi_market_echo_example.get(
        'echo?text-param={}'.format(text),
    )
    assert response.status_code == 400
