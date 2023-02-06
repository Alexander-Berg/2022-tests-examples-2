import pytest
import requests


@pytest.mark.parametrize('schema', ['http', 'https'])
@pytest.mark.parametrize(
    'domain_name,domain_final',
    [
        ('m.taxi-leader.ru', 'https://taxi-leader.ru/'),
        ('www.taxi-leader.ru', 'https://taxi-leader.ru/'),
        ('www.m.taxi-leader.ru', 'https://taxi-leader.ru/'),
    ],
)
def test_domain_redirects(schema, domain_name, domain_final):
    r = requests.get(
        schema + '://localhost/',
        headers={'Host': domain_name},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_redirect
    assert r.headers['Location'] == domain_final

@pytest.mark.parametrize('schema', ['http', 'https'])
@pytest.mark.parametrize(
    'domain_name,domain_final',
    [
        ('taxi-leader.ru', 'https://taxi-leader.ru/TEST'),
        ('m.taxi-leader.ru', 'https://taxi-leader.ru/TEST'),
        ('www.taxi-leader.ru', 'https://taxi-leader.ru/TEST'),
        ('www.m.taxi-leader.ru', 'https://taxi-leader.ru/TEST'),
    ],
)

def test_main_schema_redirect(schema, domain_name, domain_final):
    r = requests.get(
        'http://localhost/TEST',
        headers={'Host': domain_name},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_redirect
    assert r.headers['Location'] == domain_final
