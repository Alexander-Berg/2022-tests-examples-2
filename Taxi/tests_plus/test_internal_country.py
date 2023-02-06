import pytest


@pytest.mark.parametrize(
    'ipaddress,country',
    [
        ('95.59.90.0', 'kz'),
        ('185.15.98.233', 'ru'),
        ('93.170.252.25', 'by'),
        ('0.0.0.0', None),
    ],
)
async def test_internal_country(web_plus, ipaddress, country):
    result = await web_plus.country.request(ipaddress=ipaddress).perform()

    if country:
        content = result.json()
        assert content['iso_name'] == country
    else:
        assert result.status_code == 409
