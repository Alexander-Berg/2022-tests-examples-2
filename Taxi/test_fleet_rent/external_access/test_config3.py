import pytest

from fleet_rent.entities import park as park_entities
from fleet_rent.generated.web import web_context as context


@pytest.mark.client_experiments3(
    consumer='fleet/rent/park_records_limit',
    config_name='fleet_rent_park_records_limit',
    args=[
        {'name': 'park_id', 'type': 'string', 'value': 'park_id'},
        {'name': 'park_city', 'type': 'string', 'value': 'Москва'},
        {'name': 'park_country', 'type': 'string', 'value': 'rus'},
    ],
    value={'internal': None, 'external': 100},
)
async def test_get_int_ext_rent_limits(
        web_context: context.Context, park_stub_factory,
):
    park_info = park_stub_factory('park_id')
    res = await web_context.external_access.config3.get_int_ext_rent_limits(
        park_info,
    )
    assert res == (None, 100)


@pytest.mark.client_experiments3(
    consumer='fleet/rent/park_branding',
    config_name='fleet_park_branding',
    args=[
        {'name': 'park_id', 'type': 'string', 'value': 'park_id'},
        {'name': 'park_city', 'type': 'string', 'value': 'Москва'},
        {'name': 'park_country', 'type': 'string', 'value': 'rus'},
        {'name': 'fleet_type', 'type': 'string', 'value': 'yandex'},
    ],
    value={'brand_id': 'Uber'},
)
@pytest.mark.config(
    TAXIMETER_BRANDING={
        'Uber': {
            'control_email': 'no-reply@support-uber.com',
            'main_page': 'https://driver.support-uber.com',
            'no_reply_email': 'no-reply@support-uber.com',
            'opteum_external_uri': 'https://opteum-uber.taxi.tst.yandex.net',
            'opteum_support_uri': 'https://opteum.taxi.tst.yandex-team.ru',
            'park_support_email': 'az@support-uber.com',
            'support_page': 'https://support-uber.com/forpartners',
        },
        'Yandex': {
            'control_email': 'no-reply@taxi.yandex.com',
            'main_page': 'https://driver.yandex',
            'no_reply_email': 'no-reply@taxi.yandex.com',
            'opteum_external_uri': 'https://opteum.taxi.tst.yandex.ru',
            'opteum_support_uri': 'https://opteum.taxi.tst.yandex-team.ru',
            'park_support_email': 'park@taxi.yandex.com',
            'support_page': 'https://taxi.taxi.tst.yandex.ru/taximeter-info',
            'support_page_driver_partner': 'https://техподдержка-таксопарков/',
        },
        'Yango': {
            'control_email': 'no-reply@yango.yandex.com',
            'main_page': 'https://driver.yandex',
            'no_reply_email': 'no-reply@yango.yandex.com',
            'opteum_external_uri': 'https://opteum.taxi.tst.yandex.ru',
            'opteum_support_uri': 'https://opteum.taxi.tst.yandex-team.ru',
            'park_support_email': 'support@yango.yandex.com',
            'support_page': 'https://taxi.taxi.tst.yandex.ru/taximeter-info',
        },
    },
)
async def test_get_park_branding(
        web_context: context.Context, park_stub_factory,
):
    park_info = park_stub_factory('park_id')
    res = await web_context.external_access.config3.get_park_branding(
        park_info,
    )
    assert res == park_entities.Branding(
        id=park_entities.ParkBrand.UBER,
        control_email='no-reply@support-uber.com',
        main_page='https://driver.support-uber.com',
        no_reply_email='no-reply@support-uber.com',
        opteum_external_uri='https://opteum-uber.taxi.tst.yandex.net',
        opteum_support_uri='https://opteum.taxi.tst.yandex-team.ru',
        park_support_email='az@support-uber.com',
        support_page='https://support-uber.com/forpartners',
    )
