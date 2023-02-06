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
    'domain_name,domain_response',
    [
        ('abinsk.taxisaturn.ru', 'vezet.ru/'),
        ('adler.taxisaturn.ru', 'redtaxi.ru/adler'),
        ('angarsk.taxisaturn.ru', 'vezet.ru/'),
        ('armavir.taxisaturn.ru', 'redtaxi.ru/armavir'),
        ('balashixa.taxisaturn.ru', 'redtaxi.ru/balashikha'),
        ('bryansk.taxisaturn.ru', 'rutaxi.ru/bryansk'),
        ('cheboksary.taxisaturn.ru', 'rutaxi.ru/cheboksary'),
        ('domoded.taxisaturn.ru', 'redtaxi.ru/domodedovo'),
        ('essentuki.taxisaturn.ru', 'vezet.ru/'),
        ('himki.taxisaturn.ru', 'redtaxi.ru/khimki'),
        ('irkutsk.taxisaturn.ru', 'vezet.ru/'),
        ('korolev.taxisaturn.ru', 'vezet.ru/'),
        ('kropotkin.taxisaturn.ru', 'vezet.ru/allo/kropotkin'),
        ('krymsk.taxisaturn.ru', 'vezet.ru/'),
        ('kurganinsk.taxisaturn.ru', 'vezet.ru/'),
        ('kursk.taxisaturn.ru', 'vezet.ru/allo/kursk'),
        ('labinsk.taxisaturn.ru', 'vezet.ru/'),
        ('maykop.taxisaturn.ru', 'vezet.ru/allo/maykop'),
        ('mineralnye-vody.taxisaturn.ru', 'vezet.ru/'),
        ('moscow.taxisaturn.ru', 'rutaxi.ru/moscow'),
        ('mutishi.taxisaturn.ru', 'vezet.ru/'),
        ('nevinomusk.taxisaturn.ru', 'taxisaturn.ru/nevinnomyssk'),
        ('nn.taxisaturn.ru', 'vezet.ru/allo/nizhny-novgorod'),
        ('novoros.taxisaturn.ru', 'taxisaturn.ru/novorossiysk'),
        ('podolsk.taxisaturn.ru', 'redtaxi.ru/podolsk'),
        ('pyatigorsk.taxisaturn.ru', 'redtaxi.ru/pyatigorsk'),
        ('slavyansk-na-kubani.taxisaturn.ru', 'vezet.ru/'),
        ('sochi.taxisaturn.ru', 'redtaxi.ru/sochi'),
        ('stavropol.taxisaturn.ru', 'vezet.ru/'),
        ('tihoreck.taxisaturn.ru', 'vezet.ru/'),
        ('timashevsk.taxisaturn.ru', 'vezet.ru/'),
        ('vladimir.taxisaturn.ru', 'rutaxi.ru/'),
        ('volzhskij.taxisaturn.ru', 'rutaxi.ru/volzhsky'),
        ('voronezh.taxisaturn.ru', 'rutaxi.ru/voronezh'),
    ],
)
def test_basic_redirect(domain_name, domain_response):
    req = requests.get('http://{}'.format(domain_name), verify=False)
    assert req.text == domain_response
