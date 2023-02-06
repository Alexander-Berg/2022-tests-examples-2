import json

from dateutil import parser
# pylint: disable=import-error
import eats_restapp_marketing_cache.models as ermc_models
import pytest

from eats_catalog import adverts
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog.catalog_for_full_text_search import search_utils


@pytest.mark.now('2022-03-21T14:20:00+03:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_advert_rest_metric(
        taxi_eats_catalog,
        catalog_for_full_text_search,
        eats_catalog_storage,
        yabs,
        statistics,
):
    # EDACAT-2883: метрика записывающая количетво рекламных ресторанов
    # в выдаче по региону
    # стоит в начале тестов потому что иначе записывает все метрики сессии
    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2022-03-21T09:00:00+03:00'),
            end=parser.parse('2022-03-21T23:00:00+03:00'),
        ),
    ]

    for place_id in [1, 2, 3, 4, 5]:
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                region=storage.Region(region_id=42),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=working_intervals,
            ),
        )

    banners = [1, 2, 3]
    for banner_id in banners:
        yabs.add_banner(adverts.create_yabs_service_banner(banner_id))

    block_id = 'adverts'

    async with statistics.capture(taxi_eats_catalog) as capture:
        response = await catalog_for_full_text_search(
            blocks=[{'id': block_id, 'type': 'open', 'advert_settings': {}}],
        )
    assert response.status_code == 200

    zero_metric = 'zero.advert-places.open.213'
    non_zero_metric = 'non-zero.advert-places.open.213'

    print(capture.statistics, capture.statistics.keys())

    assert zero_metric in capture.statistics, capture.statistics.keys()
    assert capture.statistics[zero_metric] == 3
    assert non_zero_metric in capture.statistics, capture.statistics.keys()
    assert capture.statistics[non_zero_metric] == 3


@pytest.mark.now('2022-03-21T14:20:00+03:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_advert_block(
        catalog_for_full_text_search, eats_catalog_storage, yabs,
):
    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2022-03-21T09:00:00+03:00'),
            end=parser.parse('2022-03-21T23:00:00+03:00'),
        ),
    ]

    for place_id in [1, 2, 3, 4, 5]:
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=working_intervals,
            ),
        )

    banners = [1, 2, 3]
    for banner_id in banners:
        yabs.add_banner(adverts.create_yabs_service_banner(banner_id))

    block_id = 'adverts'
    response = await catalog_for_full_text_search(
        blocks=[{'id': block_id, 'type': 'open', 'advert_settings': {}}],
    )
    assert response.status_code == 200

    expected_slugs = [f'place_{banner_id}' for banner_id in banners]

    block = search_utils.find_block(block_id, response.json())
    assert len(block) == len(banners)

    for place, slug in zip(block, expected_slugs):
        assert place['slug'] == slug
        assert 'advertisement' in place


@pytest.mark.now('2022-04-08T13:10:00+03:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings()
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_advert_block_pass_yabs_headers(
        catalog_for_full_text_search, eats_catalog_storage, yabs,
):
    """
    EDACAT-2695: проверяет, что в БК из поиска отправляются нужные заголовки
    и праметры пользователя.
    """

    cookie = 'testsuite_cookie'
    request_id = 'testsuite_request_id'
    mobile_ifa = 'testsuite_mobile_ifa'
    appmetrica_uuid = 'testsuite_appmetrica_uuid'
    useragent = 'testsuite-agent'

    @yabs.request_assertion
    def _assert_user_params(request):
        assert request.headers['cookie'] == cookie
        assert request.headers['user-agent'] == useragent
        assert request.query['reqid'] == request_id
        assert request.query['mobile-ifa'] == mobile_ifa
        assert request.query['uuid'] == appmetrica_uuid

    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2022-04-08T09:00:00+03:00'),
            end=parser.parse('2022-04-08T23:00:00+03:00'),
        ),
    ]

    for place_id in [1, 2, 3, 4, 5]:
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=working_intervals,
            ),
        )

    banners = [1, 2, 3]
    for banner_id in banners:
        yabs.add_banner(adverts.create_yabs_service_banner(banner_id))

    block_id = 'adverts'
    response = await catalog_for_full_text_search(
        blocks=[{'id': block_id, 'type': 'open', 'advert_settings': {}}],
        cookie=cookie,
        x_request_id=request_id,
        x_mobile_ifa=mobile_ifa,
        x_appmetrica_uuid=appmetrica_uuid,
        useragent=useragent,
    )
    assert response.status_code == 200
    assert yabs.times_called == 1


@pytest.mark.now('2022-04-08T13:10:00+03:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings(adverts.YabsSettings())
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
@pytest.mark.parametrize(
    'yabs_called, log_called, blocks',
    (
        pytest.param(
            0,
            1,
            0,
            marks=[
                experiments.DISABLE_ADVERTS,
                pytest.mark.config(
                    EATS_CATALOG_LOG_SETTINGS={
                        'advert_places_params': {'enabled': True},
                    },
                ),
            ],
            id='adverts_is_off',
        ),
        pytest.param(
            1,
            0,
            1,
            marks=[
                pytest.mark.config(
                    EATS_CATALOG_LOG_SETTINGS={
                        'advert_places_params': {'enabled': True},
                    },
                ),
            ],
            id='adverts_is_on',
        ),
        pytest.param(
            0,
            0,
            0,
            marks=[
                experiments.DISABLE_ADVERTS,
                pytest.mark.config(
                    EATS_CATALOG_LOG_SETTINGS={
                        'advert_places_params': {'enabled': False},
                    },
                ),
            ],
            id='adverts_is_off_logging_is_off',
        ),
        pytest.param(
            0,
            0,
            0,
            marks=[
                experiments.DISABLE_ADVERTS,
                pytest.mark.config(
                    EATS_CATALOG_LOG_SETTINGS={
                        'advert_places_params': {
                            'enabled': True,
                            'ratio': 0.0,
                        },
                    },
                ),
            ],
            id='adverts_is_off_sampling_is_on',
        ),
        pytest.param(
            0,
            1,
            0,
            marks=[
                experiments.DISABLE_ADVERTS,
                pytest.mark.config(
                    EATS_CATALOG_LOG_SETTINGS={
                        'advert_places_params': {
                            'enabled': True,
                            'ratio': 1.0,
                        },
                    },
                ),
            ],
            id='adverts_is_off_sampling_is_off',
        ),
    ),
)
async def test_advert_places_log(
        testpoint,
        catalog_for_full_text_search,
        eats_catalog_storage,
        yabs,
        yabs_called,
        log_called,
        blocks: int,
):
    cookie = 'testsuite_cookie'
    request_id = 'testsuite_request_id'
    device_id = 'testsuite_device_id'
    mobile_ifa = 'testsuite_mobile_ifa'
    appmetrica_uuid = 'testsuite_appmetrica_uuid'
    useragent = 'testsuite-agent'

    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2022-04-08T09:00:00+03:00'),
            end=parser.parse('2022-04-08T23:00:00+03:00'),
        ),
    ]

    places = [1, 2, 3, 4, 5]

    for place_id in places:
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=working_intervals,
            ),
        )

    banners = [1, 2, 3]
    for banner_id in banners:
        yabs.add_banner(adverts.create_yabs_service_banner(banner_id))

    @testpoint('yt_log_advert_places')
    def _yt_log_advert_places(message):
        data = message['data']
        assert data['request_id'] == request_id
        assert data['device_id'] == device_id
        assert data['trace_id'] != ''
        assert sorted(data['advert_places']) == sorted([1, 2, 3])

    block_id = 'adverts'
    response = await catalog_for_full_text_search(
        blocks=[{'id': block_id, 'type': 'open', 'advert_settings': {}}],
        cookie=cookie,
        x_request_id=request_id,
        x_device_id=device_id,
        x_mobile_ifa=mobile_ifa,
        x_appmetrica_uuid=appmetrica_uuid,
        useragent=useragent,
    )

    response_json = response.json()
    assert response.status_code == 200
    assert yabs.times_called == yabs_called
    assert _yt_log_advert_places.times_called == log_called
    response_blocks = response_json['blocks']
    assert len(response_blocks) == blocks
    if response_blocks:
        assert len(response_blocks[0]['list']) == len(banners)


@pytest.mark.now('2022-04-08T13:10:00+03:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings(adverts.YabsSettings())
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
async def test_catalog_yabs_log(
        testpoint, catalog_for_full_text_search, eats_catalog_storage, yabs,
):
    'EDACAT-3091: тестирует наличие позиции в логе'
    cookie = 'testsuite_cookie'
    request_id = 'testsuite_request_id'
    device_id = 'testsuite_device_id'
    mobile_ifa = 'testsuite_mobile_ifa'
    appmetrica_uuid = 'testsuite_appmetrica_uuid'
    useragent = 'testsuite-agent'

    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2022-04-08T09:00:00+03:00'),
            end=parser.parse('2022-04-08T23:00:00+03:00'),
        ),
    ]

    places = [1, 2, 3, 4, 5]

    for place_id in places:
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=working_intervals,
            ),
        )

    banners = [1, 2, 3]
    for banner_id in banners:
        yabs.add_banner(adverts.create_yabs_service_banner(banner_id))

    @testpoint('yt_log_catalog_yabs')
    def _yt_log_catalog_yabs(message):
        data = message['data']
        assert data['request_id'] == request_id
        assert data['device_id'] == device_id
        assert data['trace_id'] != ''
        assert data['position'] == {'lat': 55.802998, 'lon': 37.591503}

    block_id = 'adverts'
    response = await catalog_for_full_text_search(
        blocks=[{'id': block_id, 'type': 'open', 'advert_settings': {}}],
        cookie=cookie,
        x_request_id=request_id,
        x_device_id=device_id,
        x_mobile_ifa=mobile_ifa,
        x_appmetrica_uuid=appmetrica_uuid,
        useragent=useragent,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert yabs.times_called == 1
    assert _yt_log_catalog_yabs.times_called == 1
    response_blocks = response_json['blocks']
    assert len(response_blocks[0]['list']) == len(banners)


@pytest.mark.now('2022-04-08T13:10:00+03:00')
@experiments.advertisements(source='yabs')
@experiments.yabs_settings(
    adverts.YabsSettings(
        coefficients=adverts.Coefficients(
            relevance_multiplier=1, send_relevance=True,
        ),
    ),
)
@pytest.mark.eats_restapp_marketing_cache(
    place_banners=[
        ermc_models.PlaceBanner(place_id=1, banner_id=1),
        ermc_models.PlaceBanner(place_id=2, banner_id=2),
        ermc_models.PlaceBanner(place_id=3, banner_id=3),
    ],
)
@pytest.mark.parametrize(
    'expected_additional_banners',
    [
        pytest.param(
            [
                {
                    'banner_id': 1,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': str(1.0 / 5.0), 'C': 0},
                },
                {
                    'banner_id': 2,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': str(1.0 / 4.0), 'C': 0},
                },
                {
                    'banner_id': 3,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': str(1.0 / 3.0), 'C': 0},
                },
            ],
            marks=(
                experiments.eats_catalog_yabs_coefficients(
                    source='organic',
                    coefficients=adverts.Coefficients(
                        relevance_multiplier=1, send_relevance=True,
                    ),
                )
            ),
            id='organic position relevance',
        ),
        pytest.param(
            [
                {
                    'banner_id': 1,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': '8.0', 'C': 0},
                },
                {
                    'banner_id': 2,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': '9.0', 'C': 0},
                },
                {
                    'banner_id': 3,
                    'ignore_context': True,
                    'value_coefs': {'A': 1.0, 'B': '10.0', 'C': 0},
                },
            ],
            marks=(
                experiments.eats_catalog_yabs_coefficients(
                    source='none',
                    coefficients=adverts.Coefficients(
                        relevance_multiplier=1, send_relevance=True,
                    ),
                )
            ),
            id='umlass relevance',
        ),
    ],
)
@experiments.USE_UMLAAS
async def test_advert_places_log_with_umlaas(
        testpoint,
        catalog_for_full_text_search,
        eats_catalog_storage,
        yabs,
        mockserver,
        expected_additional_banners,
):
    # EDACAT-3044: проверяет что в yabs
    # передается релевантность ресторана
    # равная 1 / позиция в выдаче
    cookie = 'testsuite_cookie'
    request_id = 'testsuite_request_id'
    device_id = 'testsuite_device_id'
    mobile_ifa = 'testsuite_mobile_ifa'
    appmetrica_uuid = 'testsuite_appmetrica_uuid'
    useragent = 'testsuite-agent'

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'available_blocks': [],
            'result': [
                {
                    'id': 5,
                    'relevance': 12.0,
                    'type': 'ranking',
                    'predicted_times': {'min': 1, 'max': 10},
                    'blocks': [],
                },
                {
                    'id': 4,
                    'relevance': 11.0,
                    'type': 'ranking',
                    'predicted_times': {'min': 5, 'max': 15},
                    'blocks': [],
                },
                {
                    'id': 3,
                    'relevance': 10.0,
                    'type': 'ranking',
                    'predicted_times': {'min': 30, 'max': 40},
                    'blocks': [],
                },
                {
                    'id': 2,
                    'relevance': 9.0,
                    'type': 'ranking',
                    'predicted_times': {'min': 30, 'max': 30},
                    'blocks': [],
                },
                {
                    'id': 1,
                    'relevance': 8.0,
                    'type': 'ranking',
                    'predicted_times': {'min': 30, 'max': 40},
                    'blocks': [],
                },
            ],
        }

    def yabs_assert_callback(request):
        assert 'additional-banners' in request.query
        assert (
            json.loads(request.query['additional-banners'])
            == expected_additional_banners
        )

    yabs.assert_callback = yabs_assert_callback

    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2022-04-08T09:00:00+03:00'),
            end=parser.parse('2022-04-08T23:00:00+03:00'),
        ),
    ]

    places = [1, 2, 3, 4, 5]

    for place_id in places:
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=working_intervals,
            ),
        )

    banners = [1, 2, 3]
    for banner_id in banners:
        yabs.add_banner(adverts.create_yabs_service_banner(banner_id))

    block_id = 'adverts'
    response = await catalog_for_full_text_search(
        blocks=[{'id': block_id, 'type': 'open', 'advert_settings': {}}],
        cookie=cookie,
        x_request_id=request_id,
        x_device_id=device_id,
        x_mobile_ifa=mobile_ifa,
        x_appmetrica_uuid=appmetrica_uuid,
        useragent=useragent,
    )
    response_json = response.json()
    assert umlaas_eats.times_called == 1
    assert response.status_code == 200
    assert yabs.times_called == 1
    assert len(response_json['blocks']) == 1
    assert len(response_json['blocks'][0]['list']) == 3
