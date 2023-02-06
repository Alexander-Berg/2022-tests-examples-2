import pytest
import requests


@pytest.mark.parametrize('schema', ['http', 'https'])
@pytest.mark.parametrize(
    'city_domain,final_dest',
    [
        ('abinsk.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('adler.taxisaturn.ru', 'https://redtaxi.ru/adler'),
        ('angarsk.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('armavir.taxisaturn.ru', 'https://redtaxi.ru/armavir'),
        ('balashixa.taxisaturn.ru', 'https://redtaxi.ru/balashikha'),
        ('bryansk.taxisaturn.ru', 'https://bryansk.rutaxi.ru'),
        ('cheboksary.taxisaturn.ru', 'https://cheboksary.rutaxi.ru'),
        ('domoded.taxisaturn.ru', 'https://redtaxi.ru/domodedovo'),
        ('essentuki.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('himki.taxisaturn.ru', 'https://redtaxi.ru/khimki'),
        ('irkutsk.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('korolev.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('kropotkin.taxisaturn.ru', 'https://allo.vezet.ru/kropotkin'),
        ('krymsk.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('kurganinsk.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('kursk.taxisaturn.ru', 'https://allo.vezet.ru/kursk'),
        ('labinsk.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('maykop.taxisaturn.ru', 'https://allo.vezet.ru/maykop'),
        ('mineralnye-vody.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('moscow.taxisaturn.ru', 'https://moscow.rutaxi.ru'),
        ('mutishi.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('nevinomusk.taxisaturn.ru', 'https://taxisaturn.ru/nevinnomyssk'),
        ('nn.taxisaturn.ru', 'https://allo.vezet.ru/nijniy-novgorod'),
        ('novoros.taxisaturn.ru', 'https://taxisaturn.ru/novorossiysk'),
        ('podolsk.taxisaturn.ru', 'https://redtaxi.ru/podolsk'),
        ('pyatigorsk.taxisaturn.ru', 'https://redtaxi.ru/pyatigorsk'),
        ('slavyansk-na-kubani.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('sochi.taxisaturn.ru', 'https://redtaxi.ru/sochi'),
        ('stavropol.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('tihoreck.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('timashevsk.taxisaturn.ru', 'https://allo.vezet.ru'),
        ('vladimir.taxisaturn.ru', 'https://vladimir.rutaxi.ru'),
        ('volzhskij.taxisaturn.ru', 'https://volzhskiy.rutaxi.ru'),
        ('voronezh.taxisaturn.ru', 'https://voronezh.rutaxi.ru'),
    ],
)
def test_city_redirects(schema, city_domain, final_dest):
    r = requests.get(
        schema + '://localhost/',
        headers={'Host': city_domain},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_redirect
    assert r.headers['Location'] == final_dest


def test_main_schema_redirect():
    r = requests.get(
        'http://localhost/TEST',
        headers={'Host': 'vezetdobro.ru'},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_redirect
    assert r.headers['Location'] == 'https://vezetdobro.ru/TEST'
