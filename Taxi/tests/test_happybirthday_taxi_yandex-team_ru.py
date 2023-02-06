import pytest
import requests

@pytest.mark.parametrize(
    'domain_name,domain_final',
    [
        ('happybirthday.taxi.yandex-team.ru', 'https://happybirthday.taxi.yandex-team.ru/TEST'),
    ],
)

def test_main_schema_redirect(domain_name, domain_final):
    r = requests.get(
        'http://localhost/TEST',
        headers={'Host': domain_name},
        allow_redirects=False,
        verify=False,
    )
    assert r.is_permanent_redirect
    assert r.headers['Location'] == domain_final
