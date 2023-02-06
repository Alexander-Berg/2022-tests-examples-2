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
        ('/', 'vezet.ru', 'vezet.ru/'),
        ('/test', 'vezet.ru', 'vezet.ru/test'),
        ('/', 'www.vezet.ru', 'vezet.ru/'),
        ('/test', 'www.vezet.ru', 'vezet.ru/test'),
        ('/', 'www.test.vezet.ru', 'vezet.ru/'),
        ('/', 'tarif.vezet.ru', 'tariff.vezet.ru/'),
    ],
)
def test_basic_redirect(location, domain_name, domain_response):
    req = requests.get(
        'http://{}{}'.format(domain_name, location), verify=False,
    )
    assert req.text == domain_response


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
        ('/artem', 'allo.vezet.ru', 'vezet.ru/allo/artyom'),
        ('/blg', 'allo.vezet.ru', 'vezet.ru/allo/blagoveshchensk'),
        ('/chusovoi', 'allo.vezet.ru', 'vezet.ru/allo/chusovoy'),
        ('/ekaterinburg', 'allo.vezet.ru', 'vezet.ru/allo/yekaterinburg'),
        ('/habarovsk', 'allo.vezet.ru', 'vezet.ru/allo/khabarovsk'),
        ('/kirov', 'allo.vezet.ru', 'vezet.ru/allo/kirov-kirov-oblast'),
        ('/kirovk', 'allo.vezet.ru', 'vezet.ru/allo/kirov-kaluga-oblast'),
        ('/lisva', 'allo.vezet.ru', 'vezet.ru/allo/lysva'),
        ('/ludinovo', 'allo.vezet.ru', 'vezet.ru/allo/lyudinovo'),
        ('/nijniy-novgorod', 'allo.vezet.ru', 'vezet.ru/allo/nizhny-novgorod'),
        ('/nijniy-tagil', 'allo.vezet.ru', 'vezet.ru/allo/nizhny-tagil'),
        ('/novoaltaisk', 'allo.vezet.ru', 'vezet.ru/allo/novoaltaysk'),
        ('/novokujbyshevsk', 'allo.vezet.ru', 'vezet.ru/allo/novokuybyshevsk'),
        ('/rostov-na-donu', 'allo.vezet.ru', 'vezet.ru/allo/rostov-on-don'),
        ('/serpuhov', 'allo.vezet.ru', 'vezet.ru/allo/serpukhov'),
        ('/spb', 'allo.vezet.ru', 'vezet.ru/allo/saint-petersburg'),
        ('/vnovgorod', 'allo.vezet.ru', 'vezet.ru/allo/veliky-novgorod'),
        ('/yoshkarola', 'allo.vezet.ru', 'vezet.ru/allo/yoshkar-ola'),
        ('/zhigulevsk', 'allo.vezet.ru', 'vezet.ru/allo/zhigulyovsk'),
    ],
)
def test_custom_rewrite(location, domain_name, domain_response):
    req = requests.get(
        'http://{}{}'.format(domain_name, location), verify=False,
    )
    assert req.text == domain_response
