import datetime

import pytest


@pytest.mark.config(some_url={'$mockserver': '/path', '$schema': True})
def test_mark_config_substitutes_mockserver(taxi_config, mockserver):
    some_url = taxi_config.get('some_url')
    assert some_url == mockserver.url('path')


@pytest.mark.config(some_url={'$mockserver_https': '/path', '$schema': True})
def test_mark_config_substitutes_mockserver_https(taxi_config, mockserver_ssl):
    some_url = taxi_config.get('some_url')
    assert some_url == mockserver_ssl.url('path')


@pytest.mark.config(some_date={'$dateDiff': 1})
def test_mark_config_substitutes_date(taxi_config, now):
    some_date = taxi_config.get('some_date')
    assert some_date == now + datetime.timedelta(seconds=1)
