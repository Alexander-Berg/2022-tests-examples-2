import pytest
import requests


@pytest.mark.parametrize(
    'domain,final_dest',
    [
        ('rutaxi.ru', 'https://rutaxi.ru/TEST'),
        ('www.rutaxi.ru', 'https://www.rutaxi.ru/TEST'),
    ],
)
def test_schema_redirects(domain, final_dest):
    r = requests.get(
        'http://localhost/TEST',
        headers={'Host': domain},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_permanent_redirect
    assert r.headers['Location'] == final_dest


@pytest.mark.parametrize(
    'domain,final_dest',
    [
        ('www.rutaxi.ru', 'https://rutaxi.ru/TEST'),
        ('www.test.rutaxi.ru', 'https://test.rutaxi.ru/TEST'),
    ],
)
def test_www_redirects(domain, final_dest):
    r = requests.get(
        'https://localhost/TEST',
        headers={'Host': domain},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_permanent_redirect
    assert r.headers['Location'] == final_dest


@pytest.mark.parametrize(
    'domain,url,final_dest',
    [
        ('main.rutaxi.ru', '/', 'https://rutaxi.ru'),
        ('main.rutaxi.ru', '/TEST', 'https://rutaxi.ru'),
        ('m.main.rutaxi.ru', '/', 'https://rutaxi.ru'),
        ('m.main.rutaxi.ru', '/TEST', 'https://rutaxi.ru'),
    ],
)
def test_main_redirects(domain, url, final_dest):
    r = requests.get(
        'https://localhost' + url,
        headers={'Host': domain},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_permanent_redirect
    assert r.headers['Location'] == final_dest


@pytest.mark.parametrize(
    'domain,url,final_dest',
    [
        ('rutaxi.ru', '/index.html', 'https://rutaxi.ru'),
        ('m.rutaxi.ru', '/index.html', 'https://rutaxi.ru'),
    ],
)
def test_index_html_redirects(domain, url, final_dest):
    r = requests.get(
        'https://localhost' + url,
        headers={'Host': domain},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_permanent_redirect
    assert r.headers['Location'] == final_dest


@pytest.mark.parametrize(
    'domain,final_dest',
    [
        ('testname.rutaxi.ru', 'https://rutaxi.ru'),
        ('m.testname.rutaxi.ru', 'https://rutaxi.ru'),
    ],
)
def test_unknown_domain_redirect(domain, final_dest):
    r = requests.get(
        'https://localhost/TEST',
        headers={'Host': domain},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_permanent_redirect
    assert r.headers['Location'] == final_dest


@pytest.mark.parametrize(
    'domain,final_dest',
    [
	('abakan.rutaxi.ru', 'https://rutaxi.ru/abakan'),
	('astrakhan.rutaxi.ru', 'https://rutaxi.ru/astrakhan'),
	('barnaul.rutaxi.ru', 'https://rutaxi.ru/barnaul'),
	('berezniki.rutaxi.ru', 'https://rutaxi.ru/berezniki'),
	('blagoveshchensk.rutaxi.ru', 'https://rutaxi.ru/blagoveshchensk'),
	('bryansk.rutaxi.ru', 'https://rutaxi.ru/bryansk'),
	('vnovgorod.rutaxi.ru', 'https://rutaxi.ru/veliky-novgorod'),
	('vladivostok.rutaxi.ru', 'https://rutaxi.ru/vladivostok'),
	('volgograd.rutaxi.ru', 'https://rutaxi.ru/volgograd'),
	('volzhskiy.rutaxi.ru', 'https://rutaxi.ru/volzhsky'),
	('vologda.rutaxi.ru', 'https://rutaxi.ru/vologda'),
	('voronezh.rutaxi.ru', 'https://rutaxi.ru/voronezh'),
	('votkinsk.rutaxi.ru', 'https://rutaxi.ru/votkinsk'),
	('gatchina.rutaxi.ru', 'https://rutaxi.ru/gatchina'),
	('dmgrad.rutaxi.ru', 'https://rutaxi.ru/dimitrovgrad'),
	('domodedovo.rutaxi.ru', 'https://rutaxi.ru/domodedovo'),
	('ekt.rutaxi.ru', 'https://rutaxi.ru/yekaterinburg'),
	('zhigulevsk.rutaxi.ru', 'https://rutaxi.ru/zhigulyovsk'),
	('zlatoust.rutaxi.ru', 'https://rutaxi.ru/zlatoust'),
	('ivanovo.rutaxi.ru', 'https://rutaxi.ru/ivanovo'),
	('yoshkarola.rutaxi.ru', 'https://rutaxi.ru/yoshkar-ola'),
	('kazan.rutaxi.ru', 'https://rutaxi.ru/kazan'),
	('kaliningrad.rutaxi.ru', 'https://rutaxi.ru/kaliningrad'),
	('kaluga.rutaxi.ru', 'https://rutaxi.ru/kaluga'),
	('kemerovo.rutaxi.ru', 'https://rutaxi.ru/kemerovo'),
	('krv.rutaxi.ru', 'https://rutaxi.ru/kirov-kaluga-oblast'),
	('kirov.rutaxi.ru', 'https://rutaxi.ru/kirov-kirov-oblast'),
	('kozelsk.rutaxi.ru', 'https://rutaxi.ru/kozelsk'),
	('kondrovo.rutaxi.ru', 'https://rutaxi.ru/kondrovo'),
	('kostroma.rutaxi.ru', 'https://rutaxi.ru/kostroma'),
	('krasnodar.rutaxi.ru', 'https://rutaxi.ru/krasnodar'),
	('krasnoyarsk.rutaxi.ru', 'https://rutaxi.ru/krasnoyarsk'),
	('kungur.rutaxi.ru', 'https://rutaxi.ru/kungur'),
	('kyzyl.rutaxi.ru', 'https://rutaxi.ru/kyzyl'),
	('lipeck.rutaxi.ru', 'https://rutaxi.ru/lipetsk'),
	('lisva.rutaxi.ru', 'https://rutaxi.ru/lysva'),
	('lyudinovo.rutaxi.ru', 'https://rutaxi.ru/lyudinovo'),
	('magnitogorsk.rutaxi.ru', 'https://rutaxi.ru/magnitogorsk'),
	('miass.rutaxi.ru', 'https://rutaxi.ru/miass'),
	('minus.rutaxi.ru', 'https://rutaxi.ru/minusinsk'),
	('moscow.rutaxi.ru', 'https://rutaxi.ru/moscow'),
	('murmansk.rutaxi.ru', 'https://rutaxi.ru/murmansk'),
	('nnovgorod.rutaxi.ru', 'https://rutaxi.ru/nizhny-novgorod'),
	('ntagil.rutaxi.ru', 'https://rutaxi.ru/nizhny-tagil'),
	('novoaltaisk.rutaxi.ru', 'https://rutaxi.ru/novoaltaysk'),
	('novokuznetsk.rutaxi.ru', 'https://rutaxi.ru/novokuznetsk'),
	('novokuib.rutaxi.ru', 'https://rutaxi.ru/novokuybyshevsk'),
	('novomoskovsk.rutaxi.ru', 'https://rutaxi.ru/novomoskovsk'),
	('novoross.rutaxi.ru', 'https://rutaxi.ru/novorossiysk'),
	('novosibirsk.rutaxi.ru', 'https://rutaxi.ru/novosibirsk'),
	('novochek.rutaxi.ru', 'https://rutaxi.ru/novocherkassk'),
	('obninsk.rutaxi.ru', 'https://rutaxi.ru/obninsk'),
	('oktiabrsky.rutaxi.ru', 'https://rutaxi.ru/oktyabrsky'),
	('omsk.rutaxi.ru', 'https://rutaxi.ru/omsk'),
	('orenburg.rutaxi.ru', 'https://rutaxi.ru/orenburg'),
	('orsk.rutaxi.ru', 'https://rutaxi.ru/orsk'),
	('penza.rutaxi.ru', 'https://rutaxi.ru/penza'),
	('pervouralsk.rutaxi.ru', 'https://rutaxi.ru/pervouralsk'),
	('perm.rutaxi.ru', 'https://rutaxi.ru/perm'),
	('ptz.rutaxi.ru', 'https://rutaxi.ru/petrozavodsk'),
	('pskov.rutaxi.ru', 'https://rutaxi.ru/pskov'),
	('rostov.rutaxi.ru', 'https://rutaxi.ru/rostov-on-don'),
	('ryazan.rutaxi.ru', 'https://rutaxi.ru/ryazan'),
	('salavat.rutaxi.ru', 'https://rutaxi.ru/salavat'),
	('samara.rutaxi.ru', 'https://rutaxi.ru/samara'),
	('spb.rutaxi.ru', 'https://rutaxi.ru/saint-petersburg'),
	('saransk.rutaxi.ru', 'https://rutaxi.ru/saransk'),
	('saratov.rutaxi.ru', 'https://rutaxi.ru/saratov'),
	('sayan.rutaxi.ru', 'https://rutaxi.ru/sayanogorsk'),
	('serpuhov.rutaxi.ru', 'https://rutaxi.ru/serpukhov'),
	('smolensk.rutaxi.ru', 'https://rutaxi.ru/smolensk'),
	('solikamsk.rutaxi.ru', 'https://rutaxi.ru/solikamsk'),
	('sochi.rutaxi.ru', 'https://rutaxi.ru/sochi'),
	('sterl.rutaxi.ru', 'https://rutaxi.ru/sterlitamak'),
	('syzran.rutaxi.ru', 'https://rutaxi.ru/syzran'),
	('syktyvkar.rutaxi.ru', 'https://rutaxi.ru/syktyvkar'),
	('taganrog.rutaxi.ru', 'https://rutaxi.ru/taganrog'),
	('tver.rutaxi.ru', 'https://rutaxi.ru/tver'),
	('tolyatti.rutaxi.ru', 'https://rutaxi.ru/tolyatti'),
	('tomsk.rutaxi.ru', 'https://rutaxi.ru/tomsk'),
	('tyumen.rutaxi.ru', 'https://rutaxi.ru/tyumen'),
	('ulyanovsk.rutaxi.ru', 'https://rutaxi.ru/ulyanovsk'),
	('ufa.rutaxi.ru', 'https://rutaxi.ru/ufa'),
	('habarovsk.rutaxi.ru', 'https://rutaxi.ru/khabarovsk'),
	('chaykovskiy.rutaxi.ru', 'https://rutaxi.ru/chaykovsky'),
	('chapaevsk.rutaxi.ru', 'https://rutaxi.ru/chapayevsk'),
	('cheboksary.rutaxi.ru', 'https://rutaxi.ru/cheboksary'),
	('chel.rutaxi.ru', 'https://rutaxi.ru/chelyabinsk'),
	('cherepovec.rutaxi.ru', 'https://rutaxi.ru/cherepovets'),
	('chernogorsk.rutaxi.ru', 'https://rutaxi.ru/chernogorsk'),
	('chus.rutaxi.ru', 'https://rutaxi.ru/chusovoy'),
	('engels.rutaxi.ru', 'https://rutaxi.ru/engels'),
    ],
)
def test_subdomain_redirects(domain,final_dest):
    r = requests.get(
        'https://localhost/TEST',
        headers={'Host': domain},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_redirect
    assert r.headers['Location'] == final_dest
    rm = requests.get(
        'https://localhost/TEST',
        headers={'Host': 'm.' + domain},
        allow_redirects=False,
        verify=False,
    )
    assert rm.is_redirect
    assert rm.headers['Location'] == final_dest
