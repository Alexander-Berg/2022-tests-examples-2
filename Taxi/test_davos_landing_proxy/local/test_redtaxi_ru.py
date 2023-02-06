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
        ('/', 'adler.redtaxi.ru', 'redtaxi.ru/adler'),
        ('/', 'armavir.redtaxi.ru', 'redtaxi.ru/armavir'),
        ('/', 'balashikha.redtaxi.ru', 'redtaxi.ru/balashikha'),
        ('/', 'domodedovo.redtaxi.ru', 'redtaxi.ru/domodedovo'),
        ('/', 'khimki.redtaxi.ru', 'redtaxi.ru/khimki'),
        ('/', 'krasnayapolyana.redtaxi.ru', 'redtaxi.ru/krasnaya-polyana'),
        ('/', 'lubertsy.redtaxi.ru', 'redtaxi.ru/lyubertsy'),
        ('/', 'maykop.redtaxi.ru', 'vezet.ru/allo/maykop'),
        ('/', 'moscow.redtaxi.ru', 'rutaxi.ru/moscow'),
        ('/', 'novorossiysk.redtaxi.ru', 'redtaxi.ru/novorossiysk'),
        ('/', 'odintsovo.redtaxi.ru', 'redtaxi.ru/odintsovo'),
        ('/', 'OTHER-CITY.redtaxi.ru', 'redtaxi.ru/'),
        ('/', 'podolsk.redtaxi.ru', 'redtaxi.ru/podolsk'),
        ('/', 'pyatigorsk.redtaxi.ru', 'redtaxi.ru/pyatigorsk'),
        ('/', 'sochi.redtaxi.ru', 'redtaxi.ru/sochi'),
    ],
)
def test_basic_redirect(location, domain_name, domain_response):
    req = requests.get(
        'http://{}{}'.format(domain_name, location), verify=False,
    )
    assert req.text == domain_response
