import pytest
import requests


@pytest.mark.parametrize('schema', ['http', 'https'])
@pytest.mark.parametrize(
    'city_domain,final_dest',
    [
        ('adler.redtaxi.ru', 'https://redtaxi.ru/adler'),
        ('armavir.redtaxi.ru', 'https://redtaxi.ru/armavir'),
        ('balashikha.redtaxi.ru', 'https://redtaxi.ru/balashikha'),
        ('domodedovo.redtaxi.ru', 'https://redtaxi.ru/domodedovo'),
        ('khimki.redtaxi.ru', 'https://redtaxi.ru/khimki'),
        ('krasnayapolyana.redtaxi.ru', 'https://redtaxi.ru/krasnaya-polyana'),
        ('lubertsy.redtaxi.ru', 'https://redtaxi.ru/lyubertsy'),
        ('maykop.redtaxi.ru', 'https://allo.vezet.ru/maykop'),
        ('moscow.redtaxi.ru', 'https://moscow.rutaxi.ru'),
        ('novorossiysk.redtaxi.ru', 'https://redtaxi.ru/novorossiysk'),
        ('odintsovo.redtaxi.ru', 'https://redtaxi.ru/odintsovo'),
        ('OTHER-CITY.redtaxi.ru', 'https://redtaxi.ru'),
        ('podolsk.redtaxi.ru', 'https://redtaxi.ru/podolsk'),
        ('pyatigorsk.redtaxi.ru', 'https://redtaxi.ru/pyatigorsk'),
        ('sochi.redtaxi.ru', 'https://redtaxi.ru/sochi'),
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
        headers={'Host': 'redtaxi.ru'},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_redirect
    assert r.headers['Location'] == 'https://redtaxi.ru'
