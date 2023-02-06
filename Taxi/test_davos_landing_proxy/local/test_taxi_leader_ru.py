import os

import pytest
import requests


@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'skip: local test ',
        'run localy: ',
        '. ./services/davos-landing-proxy/test_davos_landing_proxy/'
        'local/run_tests.sh',
    ),
)
@pytest.mark.parametrize(
    'location,domain_name,domain_response',
    [
        ('/', 'm.taxi-leader.ru', 'taxi-leader.ru/'),
        ('/', 'www.taxi-leader.ru', 'taxi-leader.ru/'),
        ('/', 'www.m.taxi-leader.ru', 'taxi-leader.ru/'),
        ('/test', 'm.taxi-leader.ru', 'taxi-leader.ru/test'),
        ('/test', 'www.taxi-leader.ru', 'taxi-leader.ru/test'),
        ('/test', 'www.m.taxi-leader.ru', 'taxi-leader.ru/test'),
    ],
)
def test_basic_redirect(location, domain_name, domain_response):
    req = requests.get(
        'http://{}{}'.format(domain_name, location), verify=False,
    )
    assert req.text == domain_response
