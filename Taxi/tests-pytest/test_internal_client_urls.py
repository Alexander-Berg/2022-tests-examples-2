import pytest

from taxi.internal import client_urls


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
@pytest.mark.config(
    MAX_TARIFFS_URL='https://m.taxi.taxi.tst.yandex.ru/city-tariff/?city={}'
)
def test_build_max_tariffs_url():
    result = yield client_urls.build_max_tariffs_url('moscow')
    assert (
        result == 'https://m.taxi.taxi.tst.yandex.ru/city-tariff/?city=moscow'
    )


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
@pytest.mark.config(
    PARK_TARIFFS_URL='https://m.taxi.taxi.tst.yandex.ru/park-tariff/?parkid={}'
)
def test_build_park_tariffs_url():
    result = yield client_urls.build_park_tariffs_url('park')
    assert (
        result == 'https://m.taxi.taxi.tst.yandex.ru/park-tariff/?parkid=park'
    )


@pytest.inline_callbacks
@pytest.mark.config(
    ZONE_TARIFFS_URL='https://m.taxi.taxi.tst.yandex.ru/zone-tariff/?id={}'
)
def test_build_zone_tariffs_url():
    result = yield client_urls.build_zone_tariffs_url('moscow')
    assert (
        result == 'https://m.taxi.taxi.tst.yandex.ru/zone-tariff/?id=moscow'
    )


@pytest.inline_callbacks
@pytest.mark.config(REFERRAL_URL='https://taxi.taxi.tst.yandex.ru/?ref={}')
def test_build_referral_url():
    result = yield client_urls.build_referral_url('ref123456')
    assert result == 'https://taxi.taxi.tst.yandex.ru/?ref=ref123456'


@pytest.inline_callbacks
@pytest.mark.config(
    IMAGES_URL_TEMPLATE='https://tc-tst.mobile.yandex.net'
                        '/static/test-images/{}')
def test_build_image_url():
    result = yield client_urls.build_image_url('foo.png')
    assert (
        result == 'https://tc-tst.mobile.yandex.net/static/test-images/foo.png'
    )


@pytest.inline_callbacks
def test_build_referral_promocode_url():
    result = yield client_urls.build_referral_promocode_url('promo123')
    assert result == 'https://m.taxi.yandex.ru/invite/promo123'
