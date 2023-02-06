import dataclasses
import typing

# pylint: disable=import-error
from eats_analytics import eats_analytics  # noqa: F401
# pylint: enable=import-error
import pytest

from tests_eats_communications import adverts
from tests_eats_communications import experiments
from tests_eats_communications import utils

URL = 'http://yandex.ru'
APP_LINK = 'http://yandex.ru/mobile'
IMAGE_URL = 'beautiful_shortcut.png'
REQ_EXP = 'request_exp'
PAGE_ID = 1
HEADERS = {
    'x-yandex-uid': '12950',
    'x-user-id': '100500',
    'X-Eats-User': 'personal_phone_id=444phoneid, user_id=100500',
    'x-device-id': 'test_device',
    'x-app-version': '5.4.0',
    'x-platform': 'eda_ios_app',
}


def make_feeds_banner(
        banner_id: int, experiment: str, pictures: None, width: str = 'single',
) -> dict:
    return {
        'banner_id': banner_id,
        'experiment': experiment,
        'recipients': {'type': 'info'},
        'url': URL,
        'appLink': APP_LINK,
        'priority': 10,
        'width': width,
        'images': [{'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'}],
        'wide_and_short': pictures,
        'shortcuts': [{'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'}],
    }


def create_yabs_banner(banner_id: int) -> adverts.BSDataBanner:
    return adverts.BSDataBanner(bs_data=adverts.BSData(adId=str(banner_id)))


@experiments.feed(REQ_EXP)
async def test_advert_banners_in_blocks(taxi_eats_communications, mockserver):
    """
    Проверяем, что если есть баннер, подходящий в рекламный блок по настройкам,
    то он не попадёт в основную выдачу
    """

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds_payload(
            make_feeds_banner(
                10,
                REQ_EXP,
                [{'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'}],
                'double',
            ),
        )

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={
            'latitude': 0,
            'longitude': 0,
            'blocks': [
                {
                    'block_id': '1',
                    'type': 'advert',
                    'experiments': [REQ_EXP],
                    'advert_settings': {
                        'format': 'classic',
                        'include_banner_ids': ['10'],
                    },
                },
            ],
        },
    )

    assert feeds.times_called == 1
    assert response.status_code == 200
    data = response.json()

    data_blocks = data['payload']['blocks']
    assert data_blocks
    assert len(data_blocks) == 1

    ad_block = data_blocks[0]
    assert ad_block['block_id'] == '1'
    assert ad_block['type'] == 'advert'

    payload_block = ad_block['payload']
    assert payload_block['block_type'] == 'advert'

    assert len(payload_block['advert_banners']) == 1
    assert payload_block['advert_banners'][0]['id'] == 10
    for banner in payload_block['advert_banners']:
        context = eats_analytics.AnalyticsContext(item_id=str(banner['id']))
        assert banner['meta']['analytics'] == eats_analytics.encode(context)

    assert not data['payload']['banners']


@experiments.feed(REQ_EXP)
async def test_advert_banners_different_formats(
        taxi_eats_communications, mockserver,
):
    """
    Проверяем, что если два блока имеют разные настройки по форматам,
    то баннер попадёт в оба
    """

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds_payload(
            make_feeds_banner(
                10,
                REQ_EXP,
                [{'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'}],
                'double',
            ),
            make_feeds_banner(
                20,
                REQ_EXP,
                [{'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'}],
                'double',
            ),
        )

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={
            'latitude': 0,
            'longitude': 0,
            'blocks': [
                {
                    'block_id': '1',
                    'type': 'advert',
                    'experiments': [REQ_EXP],
                    'advert_settings': {
                        'format': 'classic',
                        'include_banner_ids': ['10'],
                    },
                },
                {
                    'block_id': '2',
                    'type': 'advert',
                    'experiments': [REQ_EXP],
                    'advert_settings': {
                        'format': 'wide-and-short',
                        'include_banner_ids': ['10'],
                    },
                },
                {
                    'block_id': '3',
                    'type': 'advert',
                    'experiments': [REQ_EXP],
                    'advert_settings': {
                        'format': 'classic',
                        'include_banner_ids': ['10', '20'],
                    },
                },
            ],
        },
    )

    assert feeds.times_called == 1
    assert response.status_code == 200
    data = response.json()

    data_blocks = data['payload']['blocks']
    assert data_blocks
    assert len(data_blocks) == 3

    for i in range(2):
        ad_block = data_blocks[i]
        assert ad_block['type'] == 'advert'

        payload_block = ad_block['payload']
        assert payload_block['block_type'] == 'advert'

        assert len(payload_block['advert_banners']) == 1
        if i < 2:
            assert payload_block['advert_banners'][0]['id'] == 10
        else:
            assert payload_block['advert_banners'][0]['id'] == 20


@dataclasses.dataclass
class YabsTestBanner:
    banner_id: int
    view_url: str
    click_url: str


@experiments.feed(REQ_EXP)
@experiments.use_eats_catalog()
@experiments.yabs_parameters(page_id=PAGE_ID)
@pytest.mark.parametrize(
    'yabs_response, expected_banners',
    [
        pytest.param(adverts.MetaBannersetResponse(), [], id='empty response'),
        pytest.param(
            adverts.MetaBannersetResponse(
                common=adverts.Common(linkHead='http://eda.yandex.ru'),
            ),
            [],
            id='empty response when response has no direct field',
        ),
        pytest.param(
            adverts.MetaBannersetResponse(
                common=adverts.Common(linkHead='http://eda.yandex.ru'),
                direct=adverts.Direct(),
            ),
            [],
            id='empty response when response has no banners',
        ),
        pytest.param(
            adverts.MetaBannersetResponse(
                common=adverts.Common(linkHead='http://eda.yandex.ru'),
                direct=adverts.Direct(ads=[create_yabs_banner(1)]),
            ),
            [
                YabsTestBanner(
                    banner_id=1,
                    view_url='http://eda.yandex.ru/view/1',
                    click_url='http://yandex.ru/click/1',
                ),
            ],
            id='single advert banner',
        ),
        pytest.param(
            adverts.MetaBannersetResponse(
                common=adverts.Common(linkHead='http://eda.yandex.ru'),
                direct=adverts.Direct(
                    ads=[create_yabs_banner(3), create_yabs_banner(1)],
                ),
            ),
            [
                YabsTestBanner(
                    banner_id=3,
                    view_url='http://eda.yandex.ru/view/3',
                    click_url='http://yandex.ru/click/3',
                ),
                YabsTestBanner(
                    banner_id=1,
                    view_url='http://eda.yandex.ru/view/1',
                    click_url='http://yandex.ru/click/1',
                ),
            ],
            id='strong advert order',
        ),
        pytest.param(
            adverts.MetaBannersetResponse(
                common=adverts.Common(linkHead='http://eda.yandex.ru'),
                direct=adverts.Direct(
                    ads=[create_yabs_banner(4), create_yabs_banner(1)],
                ),
            ),
            [
                YabsTestBanner(
                    banner_id=1,
                    view_url='http://eda.yandex.ru/view/1',
                    click_url='http://yandex.ru/click/1',
                ),
            ],
            id='unknown banner in response',
        ),
    ],
)
async def test_yabs_advertisements(
        taxi_eats_communications,
        mockserver,
        eats_catalog,
        yabs,
        yabs_response: adverts.MetaBannersetResponse,
        expected_banners: typing.List[YabsTestBanner],
):
    banner_ids = [1, 2, 3]
    banners = []
    places = []
    for banner_id in banner_ids:
        banners.append(
            {
                'banner_id': banner_id,
                'experiment': REQ_EXP,
                'recipients': {'type': 'restaurant', 'places': [banner_id]},
                'priority': 10 + banner_id,
                'images': [
                    {'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'},
                ],
                'advert_settings': {
                    'enabled': True,
                    'direct': {
                        'campaign_id': f'campaign_{banner_id}',
                        'yandex_uid': f'passport_{banner_id}',
                        'banner_id': str(banner_id),
                    },
                },
            },
        )
        places.append(
            {
                'id': str(banner_id),
                'slug': f'place_{banner_id}',
                'brand': {
                    'id': str(banner_id),
                    'slug': 'brand_slug_{banner_id}',
                    'business': 'restaurant',
                    'name': str(banner_id),
                    'logo': {
                        'light': [{'size': 'large', 'logo_url': 'logo_url'}],
                        'dark': [{'size': 'large', 'logo_url': 'logo_url'}],
                    },
                },
            },
        )

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds_payload(*banners)

    eats_catalog.add_block({'id': '__open', 'list': places})
    yabs.set_page_id(PAGE_ID)
    yabs.set_response(yabs_response)

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={
            'latitude': 0,
            'longitude': 0,
            'blocks': [
                {
                    'block_id': '1',
                    'type': 'advert',
                    'experiments': [],
                    'advert_settings': {'format': 'classic'},
                },
            ],
        },
    )
    assert response.status_code == 200
    assert eats_catalog.times_called == 1
    assert feeds.times_called == 1
    assert yabs.times_called == 1

    payload = response.json()['payload']
    assert not payload[
        'banners'
    ], 'expected no advert banners to get in response'

    blocks = payload['blocks']
    if not expected_banners:
        assert not blocks
        return

    assert len(blocks) == 1
    block = blocks.pop(0)
    actual_banners = block['payload']['advert_banners']

    assert len(expected_banners) == len(actual_banners)
    for expected_banner, actual_banner in zip(
            expected_banners, actual_banners,
    ):
        assert expected_banner.banner_id == actual_banner['id']

        assert 'advertisement' in actual_banner['meta']
        advertisement = actual_banner['meta']['advertisement']

        assert expected_banner.view_url == advertisement['view_url']
        assert expected_banner.click_url == advertisement['click_url']


@experiments.feed(REQ_EXP)
@experiments.use_eats_catalog()
@experiments.yabs_parameters(page_id=PAGE_ID)
@pytest.mark.now('2022-11-11T04:20:00+00:00')
@pytest.mark.parametrize(
    'log_times_called',
    [
        pytest.param(0, id='log disabled'),
        pytest.param(
            1,
            marks=(
                pytest.mark.config(
                    EATS_COMMUNICATIONS_LOG_SETTINGS={
                        'log_enabled': True,
                        'probability_of_logging': 100,
                    },
                )
            ),
            id='log enabled',
        ),
    ],
)
async def test_search_log_response(
        taxi_eats_communications,
        eats_catalog,
        testpoint,
        mockserver,
        yabs,
        log_times_called,
):

    banner_ids = [1, 2, 3]
    banners = []
    places = []
    yabs_response = adverts.MetaBannersetResponse()

    for banner_id in banner_ids:
        banners.append(
            {
                'banner_id': banner_id,
                'experiment': REQ_EXP,
                'recipients': {'type': 'restaurant', 'places': [banner_id]},
                'priority': 10 + banner_id,
                'images': [
                    {'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'},
                ],
                'advert_settings': {
                    'enabled': True,
                    'direct': {
                        'campaign_id': f'campaign_{banner_id}',
                        'yandex_uid': f'passport_{banner_id}',
                        'banner_id': str(banner_id),
                    },
                },
            },
        )
        places.append(
            {
                'id': str(banner_id),
                'slug': f'place_{banner_id}',
                'brand': {
                    'id': str(banner_id),
                    'slug': 'brand_slug_{banner_id}',
                    'business': 'restaurant',
                    'name': str(banner_id),
                    'logo': {
                        'light': [{'size': 'large', 'logo_url': 'logo_url'}],
                        'dark': [{'size': 'large', 'logo_url': 'logo_url'}],
                    },
                },
            },
        )

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds_payload(*banners)

    eats_catalog.add_block({'id': '__open', 'list': places})
    yabs.set_page_id(PAGE_ID)
    yabs.set_response(yabs_response)

    log_message_fields = {
        'device_id': 'test_device',
        'yandex_uid': '12950',
        'user_id': '100500',
        'personal_phone_id': '444phoneid',
        'header': {
            'Content-Type': 'application/json; charset=utf-8',
            'Cookie': '',
            'X-Real-Ip': '',
            'user-agent': 'Python/3.7 aiohttp/3.5.4',
        },
        'response': {'common': {}},
        'timestamp': '2022-11-11T07:20:00+03:00',
        'url': '',
        'span_id': '',
        'trace_id': '',
        'request_id': '',
    }

    def parse_url(url):
        url_content = []
        content_idx = 0
        url_content.append('')
        key_value = ['', '']
        key_value_index = 0
        for char in url:

            if content_idx == 0:
                if char == '?':
                    content_idx += 1
                    url_content.append({})
                else:
                    url_content[0] += char

            else:
                if char == '&':
                    url_content[1][key_value[0]] = key_value[1]
                    key_value = ['', '']
                    key_value_index = 0
                elif char == '=':
                    key_value_index += 1
                else:
                    key_value[key_value_index] += char
        url_content[1][key_value[0]] = key_value[1]
        return url_content

    def check_url(url):
        url_content = parse_url(url)
        assert url_content[0] == '/meta_bannerset/1'

        checkable_content = {
            'charset': 'utf-8',
            'target-ref': 'testsuite',
            'force-uniformat': '1',
        }
        uncheckable_content = ['banner-set', 'imp-id', 'reqid']

        assert len(url_content[1]) == len(checkable_content) + len(
            uncheckable_content,
        )

        for key, value in url_content[1].items():
            if key in uncheckable_content:
                assert value
            elif key in checkable_content:
                assert value == checkable_content[key]
            else:
                assert False

    @testpoint('yt_yabs_log_message')
    def log_response(data):
        assert len(data) == len(log_message_fields)
        uncheckable_data = ['span_id', 'trace_id', 'request_id']
        for key, value in data.items():
            assert key in log_message_fields
            if key == 'url':
                check_url(value)
            elif key not in uncheckable_data:
                assert value == log_message_fields[key]
            else:
                assert value

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers=HEADERS,
        json={
            'latitude': 0,
            'longitude': 0,
            'blocks': [
                {
                    'block_id': '1',
                    'type': 'advert',
                    'experiments': [],
                    'advert_settings': {'format': 'classic'},
                },
            ],
        },
    )

    assert response.status_code == 200
    assert log_response.times_called == log_times_called
    assert feeds.times_called == 1


@experiments.feed(REQ_EXP)
@experiments.ADVERTS_OFF
async def test_switching_off_advertising(taxi_eats_communications, mockserver):
    """
    Проверяем, что эксперимент, выключающий рекламу, работает
    """

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds_payload(
            make_feeds_banner(
                10,
                REQ_EXP,
                [{'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'}],
                'double',
            ),
        )

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={
            'latitude': 0,
            'longitude': 0,
            'blocks': [
                {
                    'block_id': '1',
                    'type': 'advert',
                    'experiments': [REQ_EXP],
                    'advert_settings': {
                        'format': 'classic',
                        'include_banner_ids': ['10'],
                    },
                },
            ],
        },
    )

    assert feeds.times_called == 1
    assert response.status_code == 200
    data = response.json()

    data_blocks = data['payload']['blocks']
    assert not data_blocks


@experiments.feed(REQ_EXP)
@experiments.use_eats_catalog()
@experiments.yabs_parameters(page_id=PAGE_ID)
@pytest.mark.parametrize(
    'host',
    [
        pytest.param('/yabs', id='set default host'),
        pytest.param('/an/yandex', id='set host by experiment'),
    ],
)
async def test_yabs_host_by_experiment(
        taxi_eats_communications,
        mockserver,
        experiments3,
        eats_catalog,
        host: str,
):

    experiments3.add_experiment(
        match=experiments.ALWAYS,
        name='eats_communications_yabs_host',
        consumers=['eats-communications/layout-banners'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'host': mockserver.url(host)},
                'predicate': {'type': 'true'},
            },
        ],
    )
    await taxi_eats_communications.invalidate_caches()

    banner_ids = [1, 2, 3]
    banners = []
    places = []
    for banner_id in banner_ids:
        banners.append(
            {
                'banner_id': banner_id,
                'experiment': REQ_EXP,
                'recipients': {'type': 'restaurant', 'places': [banner_id]},
                'priority': 10 + banner_id,
                'images': [
                    {'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'},
                ],
                'advert_settings': {
                    'enabled': True,
                    'direct': {
                        'campaign_id': f'campaign_{banner_id}',
                        'yandex_uid': f'passport_{banner_id}',
                        'banner_id': str(banner_id),
                    },
                },
            },
        )
        places.append(
            {
                'id': str(banner_id),
                'slug': f'place_{banner_id}',
                'brand': {
                    'id': str(banner_id),
                    'slug': 'brand_slug_{banner_id}',
                    'business': 'restaurant',
                    'name': str(banner_id),
                    'logo': {
                        'light': [{'size': 'large', 'logo_url': 'logo_url'}],
                        'dark': [{'size': 'large', 'logo_url': 'logo_url'}],
                    },
                },
            },
        )

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds_payload(*banners)

    @mockserver.json_handler(f'{host}/meta_bannerset/{PAGE_ID}')
    def yabs(_):
        return mockserver.make_response(status=200, json={'common': {}})

    eats_catalog.add_block({'id': '__open', 'list': places})

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={
            'latitude': 0,
            'longitude': 0,
            'blocks': [
                {
                    'block_id': '1',
                    'type': 'advert',
                    'experiments': [],
                    'advert_settings': {'format': 'classic'},
                },
            ],
        },
    )
    assert response.status_code == 200
    assert eats_catalog.times_called == 1
    assert feeds.times_called == 1
    assert yabs.times_called == 1


@experiments.feed(REQ_EXP)
@experiments.use_eats_catalog()
@experiments.yabs_parameters(page_id=PAGE_ID)
async def test_yabs_headers(
        taxi_eats_communications, mockserver, eats_catalog,
):

    app_metrica_device_id = 'testsuite-app-metrica-device-id'
    app_metrica_uuid = 'testsuite-app-metrica-uuid'
    mobile_ifa = 'testsuite-mobile-ifa'

    banner_ids = [1, 2, 3]
    banners = []
    places = []
    for banner_id in banner_ids:
        banners.append(
            {
                'banner_id': banner_id,
                'experiment': REQ_EXP,
                'recipients': {'type': 'restaurant', 'places': [banner_id]},
                'priority': 10 + banner_id,
                'images': [
                    {'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'},
                ],
                'advert_settings': {
                    'enabled': True,
                    'direct': {
                        'campaign_id': f'campaign_{banner_id}',
                        'yandex_uid': f'passport_{banner_id}',
                        'banner_id': str(banner_id),
                    },
                },
            },
        )
        places.append(
            {
                'id': str(banner_id),
                'slug': f'place_{banner_id}',
                'brand': {
                    'id': str(banner_id),
                    'slug': 'brand_slug_{banner_id}',
                    'business': 'restaurant',
                    'name': str(banner_id),
                    'logo': {
                        'light': [{'size': 'large', 'logo_url': 'logo_url'}],
                        'dark': [{'size': 'large', 'logo_url': 'logo_url'}],
                    },
                },
            },
        )

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds_payload(*banners)

    @mockserver.json_handler(f'/yabs/meta_bannerset/{PAGE_ID}')
    def yabs(request):
        assert 'device-id' in request.query
        assert request.query['device-id'] == app_metrica_device_id

        assert 'uuid' in request.query
        assert request.query['uuid'] == app_metrica_uuid

        assert 'mobile-ifa' in request.query
        assert request.query['mobile-ifa'] == mobile_ifa

        return mockserver.make_response(status=200, json={'common': {}})

    eats_catalog.add_block({'id': '__open', 'list': places})

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
            'x-appmetrica-deviceid': app_metrica_device_id,
            'x-appmetrica-uuid': app_metrica_uuid,
            'x-mobile-ifa': mobile_ifa,
        },
        json={
            'latitude': 0,
            'longitude': 0,
            'blocks': [
                {
                    'block_id': '1',
                    'type': 'advert',
                    'experiments': [],
                    'advert_settings': {'format': 'classic'},
                },
            ],
        },
    )
    assert response.status_code == 200
    assert eats_catalog.times_called == 1
    assert feeds.times_called == 1
    assert yabs.times_called == 1
