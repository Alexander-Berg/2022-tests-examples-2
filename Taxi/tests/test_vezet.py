import pytest
import requests


@pytest.mark.parametrize(
    'domain,final_dest',
    [
        ('vezet.ru', 'https://vezet.ru/TEST'),
        ('www.vezet.ru', 'https://www.vezet.ru/TEST'),
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
        ('www.vezet.ru', 'https://vezet.ru/TEST'),
        ('www.test.vezet.ru', 'https://test.vezet.ru/TEST'),
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
    'domain,final_dest', [('tarif.vezet.ru', 'https://tariff.vezet.ru/TEST')],
)
def test_domain_fix(domain, final_dest):
    r = requests.get(
        'https://localhost/TEST',
        headers={'Host': domain},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_permanent_redirect
    assert r.headers['Location'] == final_dest


@pytest.mark.parametrize(
    'old_name,new_name  ',
    [
        ('artem', 'artyom'),
        ('blg', 'blagoveshchensk'),
        ('chusovoi', 'chusovoy'),
        ('ekaterinburg', 'yekaterinburg'),
        ('habarovsk', 'khabarovsk'),
        ('kirov', 'kirov-kirov-oblast'),
        ('kirovk', 'kirov-kaluga-oblast'),
        ('lisva', 'lysva'),
        ('ludinovo', 'lyudinovo'),
        ('nijniy-novgorod', 'nizhny-novgorod'),
        ('nijniy-tagil', 'nizhny-tagil'),
        ('novoaltaisk', 'novoaltaysk'),
        ('novokujbyshevsk', 'novokuybyshevsk'),
        ('rostov-na-donu', 'rostov-on-don'),
        ('serpuhov', 'serpukhov'),
        ('spb', 'saint-petersburg'),
        ('vnovgorod', 'veliky-novgorod'),
        ('yoshkarola', 'yoshkar-ola'),
        ('zhigulevsk', 'zhigulyovsk'),
    ],
)
def test_city_redirects(old_name, new_name):
    r = requests.get(
        'https://localhost/' + old_name,
        headers={'Host': 'allo.vezet.ru'},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_redirect
    assert r.headers['Location'] == 'https://allo.vezet.ru/' + new_name


@pytest.mark.parametrize(
    'domain,final_dest', [('brand.vezet.ru', 'https://vezet.ru')],
)
def test_vezet_unknown_domain(domain, final_dest):
    r = requests.get(
        'https://localhost/TEST',
        headers={'Host': domain},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_permanent_redirect
    assert r.headers['Location'] == final_dest


@pytest.mark.parametrize(
    'domain,final_dest', [('allo.vezet.ru', 'https://vezet.ru')],
)
def test_domain_redirecs_on_root_location(domain, final_dest):
    r = requests.get(
        'https://localhost/',
        headers={'Host': domain},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_permanent_redirect
    assert r.headers['Location'] == final_dest
