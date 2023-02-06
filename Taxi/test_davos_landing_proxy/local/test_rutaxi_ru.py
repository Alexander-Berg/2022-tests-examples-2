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
        ('/', 'rutaxi.ru', 'rutaxi.ru/'),
        ('/test', 'rutaxi.ru', 'rutaxi.ru/test'),
        ('/test', 'www.rutaxi.ru', 'rutaxi.ru/test'),
        ('/', 'www.test.rutaxi.ru', 'rutaxi.ru/'),
        ('/', 'testname.rutaxi.ru', 'rutaxi.ru/'),
        ('/', 'm.testname.rutaxi.ru', 'rutaxi.ru/'),
        ('/', 'main.rutaxi.ru', 'rutaxi.ru/'),
        ('/test', 'main.rutaxi.ru', 'rutaxi.ru/'),
        ('/', 'm.main.rutaxi.ru', 'rutaxi.ru/'),
        ('/test', 'm.main.rutaxi.ru', 'rutaxi.ru/'),
        ('/index.html', 'rutaxi.ru', 'rutaxi.ru/'),
        ('/index.html', 'm.rutaxi.ru', 'rutaxi.ru/'),
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
    'domain_name,domain_response',
    [
        ('abakan.rutaxi.ru', 'rutaxi.ru/abakan'),
        ('astrakhan.rutaxi.ru', 'rutaxi.ru/astrakhan'),
        ('barnaul.rutaxi.ru', 'rutaxi.ru/barnaul'),
        ('berezniki.rutaxi.ru', 'rutaxi.ru/berezniki'),
        ('blagoveshchensk.rutaxi.ru', 'rutaxi.ru/blagoveshchensk'),
        ('bryansk.rutaxi.ru', 'rutaxi.ru/bryansk'),
        ('vnovgorod.rutaxi.ru', 'rutaxi.ru/veliky-novgorod'),
        ('vladivostok.rutaxi.ru', 'rutaxi.ru/vladivostok'),
        ('volgograd.rutaxi.ru', 'rutaxi.ru/volgograd'),
        ('volzhskiy.rutaxi.ru', 'rutaxi.ru/volzhsky'),
        ('vologda.rutaxi.ru', 'rutaxi.ru/vologda'),
        ('voronezh.rutaxi.ru', 'rutaxi.ru/voronezh'),
        ('votkinsk.rutaxi.ru', 'rutaxi.ru/votkinsk'),
        ('gatchina.rutaxi.ru', 'rutaxi.ru/gatchina'),
        ('dmgrad.rutaxi.ru', 'rutaxi.ru/dimitrovgrad'),
        ('domodedovo.rutaxi.ru', 'rutaxi.ru/domodedovo'),
        ('ekt.rutaxi.ru', 'rutaxi.ru/yekaterinburg'),
        ('zhigulevsk.rutaxi.ru', 'rutaxi.ru/zhigulyovsk'),
        ('zlatoust.rutaxi.ru', 'rutaxi.ru/zlatoust'),
        ('ivanovo.rutaxi.ru', 'rutaxi.ru/ivanovo'),
        ('yoshkarola.rutaxi.ru', 'rutaxi.ru/yoshkar-ola'),
        ('kazan.rutaxi.ru', 'rutaxi.ru/kazan'),
        ('kaliningrad.rutaxi.ru', 'rutaxi.ru/kaliningrad'),
        ('kaluga.rutaxi.ru', 'rutaxi.ru/kaluga'),
        ('kemerovo.rutaxi.ru', 'rutaxi.ru/kemerovo'),
        ('krv.rutaxi.ru', 'rutaxi.ru/kirov-kaluga-oblast'),
        ('kirov.rutaxi.ru', 'rutaxi.ru/kirov-kirov-oblast'),
        ('kozelsk.rutaxi.ru', 'rutaxi.ru/kozelsk'),
        ('kondrovo.rutaxi.ru', 'rutaxi.ru/kondrovo'),
        ('kostroma.rutaxi.ru', 'rutaxi.ru/kostroma'),
        ('krasnodar.rutaxi.ru', 'rutaxi.ru/krasnodar'),
        ('krasnoyarsk.rutaxi.ru', 'rutaxi.ru/krasnoyarsk'),
        ('kungur.rutaxi.ru', 'rutaxi.ru/kungur'),
        ('kyzyl.rutaxi.ru', 'rutaxi.ru/kyzyl'),
        ('lipeck.rutaxi.ru', 'rutaxi.ru/lipetsk'),
        ('lisva.rutaxi.ru', 'rutaxi.ru/lysva'),
        ('lyudinovo.rutaxi.ru', 'rutaxi.ru/lyudinovo'),
        ('magnitogorsk.rutaxi.ru', 'rutaxi.ru/magnitogorsk'),
        ('miass.rutaxi.ru', 'rutaxi.ru/miass'),
        ('minus.rutaxi.ru', 'rutaxi.ru/minusinsk'),
        ('moscow.rutaxi.ru', 'rutaxi.ru/moscow'),
        ('murmansk.rutaxi.ru', 'rutaxi.ru/murmansk'),
        ('nnovgorod.rutaxi.ru', 'rutaxi.ru/nizhny-novgorod'),
        ('ntagil.rutaxi.ru', 'rutaxi.ru/nizhny-tagil'),
        ('novoaltaisk.rutaxi.ru', 'rutaxi.ru/novoaltaysk'),
        ('novokuznetsk.rutaxi.ru', 'rutaxi.ru/novokuznetsk'),
        ('novokuib.rutaxi.ru', 'rutaxi.ru/novokuybyshevsk'),
        ('novomoskovsk.rutaxi.ru', 'rutaxi.ru/novomoskovsk'),
        ('novoross.rutaxi.ru', 'rutaxi.ru/novorossiysk'),
        ('novosibirsk.rutaxi.ru', 'rutaxi.ru/novosibirsk'),
        ('novochek.rutaxi.ru', 'rutaxi.ru/novocherkassk'),
        ('obninsk.rutaxi.ru', 'rutaxi.ru/obninsk'),
        ('oktiabrsky.rutaxi.ru', 'rutaxi.ru/oktyabrsky'),
        ('omsk.rutaxi.ru', 'rutaxi.ru/omsk'),
        ('orenburg.rutaxi.ru', 'rutaxi.ru/orenburg'),
        ('orsk.rutaxi.ru', 'rutaxi.ru/orsk'),
        ('penza.rutaxi.ru', 'rutaxi.ru/penza'),
        ('pervouralsk.rutaxi.ru', 'rutaxi.ru/pervouralsk'),
        ('perm.rutaxi.ru', 'rutaxi.ru/perm'),
        ('ptz.rutaxi.ru', 'rutaxi.ru/petrozavodsk'),
        ('pskov.rutaxi.ru', 'rutaxi.ru/pskov'),
        ('rostov.rutaxi.ru', 'rutaxi.ru/rostov-on-don'),
        ('ryazan.rutaxi.ru', 'rutaxi.ru/ryazan'),
        ('salavat.rutaxi.ru', 'rutaxi.ru/salavat'),
        ('samara.rutaxi.ru', 'rutaxi.ru/samara'),
        ('spb.rutaxi.ru', 'rutaxi.ru/saint-petersburg'),
        ('saransk.rutaxi.ru', 'rutaxi.ru/saransk'),
        ('saratov.rutaxi.ru', 'rutaxi.ru/saratov'),
        ('sayan.rutaxi.ru', 'rutaxi.ru/sayanogorsk'),
        ('serpuhov.rutaxi.ru', 'rutaxi.ru/serpukhov'),
        ('smolensk.rutaxi.ru', 'rutaxi.ru/smolensk'),
        ('solikamsk.rutaxi.ru', 'rutaxi.ru/solikamsk'),
        ('sochi.rutaxi.ru', 'rutaxi.ru/sochi'),
        ('sterl.rutaxi.ru', 'rutaxi.ru/sterlitamak'),
        ('syzran.rutaxi.ru', 'rutaxi.ru/syzran'),
        ('syktyvkar.rutaxi.ru', 'rutaxi.ru/syktyvkar'),
        ('taganrog.rutaxi.ru', 'rutaxi.ru/taganrog'),
        ('tver.rutaxi.ru', 'rutaxi.ru/tver'),
        ('tolyatti.rutaxi.ru', 'rutaxi.ru/tolyatti'),
        ('tomsk.rutaxi.ru', 'rutaxi.ru/tomsk'),
        ('tyumen.rutaxi.ru', 'rutaxi.ru/tyumen'),
        ('ulyanovsk.rutaxi.ru', 'rutaxi.ru/ulyanovsk'),
        ('ufa.rutaxi.ru', 'rutaxi.ru/ufa'),
        ('habarovsk.rutaxi.ru', 'rutaxi.ru/khabarovsk'),
        ('chaykovskiy.rutaxi.ru', 'rutaxi.ru/chaykovsky'),
        ('chapaevsk.rutaxi.ru', 'rutaxi.ru/chapayevsk'),
        ('cheboksary.rutaxi.ru', 'rutaxi.ru/cheboksary'),
        ('chel.rutaxi.ru', 'rutaxi.ru/chelyabinsk'),
        ('cherepovec.rutaxi.ru', 'rutaxi.ru/cherepovets'),
        ('chernogorsk.rutaxi.ru', 'rutaxi.ru/chernogorsk'),
        ('chus.rutaxi.ru', 'rutaxi.ru/chusovoy'),
        ('engels.rutaxi.ru', 'rutaxi.ru/engels'),
    ],
)
def test_custom_rewrite(domain_name, domain_response):
    req = requests.get('http://{}'.format(domain_name), verify=False)
    assert req.text == domain_response
