import pytest

YT_LOGS = []


@pytest.fixture(name='testpoint_service')
def _testpoint_service(testpoint):
    @testpoint('yt_logger::messages::calculations')
    def _handler(data_json):
        YT_LOGS.append(data_json)


@pytest.mark.parametrize(
    'intent,expected_classes',
    [
        ('surge_sampling', ['business', 'econom']),
        ('price_calculation', ['business', 'econom', 'vip']),
    ],
)
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business', 'vip'],
    SURGE_CACHE_SETTINGS={
        'ENABLED': True,
        'GEOHASH_SIZE': 7,
        'TTL_SEC': 120,
        'EXT_MAX_TTL_SEC': 120,
        'PROLONG_BY_USER_TTL_SEC': 1,
    },
    SURGE_CALCULATOR_OMIT_UNNEEDED_CATEGORIES=True,
)
async def test_omit_categories(
        taxi_surge_calculator, intent, expected_classes, testpoint_service,
):
    YT_LOGS.clear()
    request = {
        'point_a': [37.583369, 55.778821],
        'classes': ['econom', 'business'],
        'intent': intent,
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200

    assert YT_LOGS
    calculated_classes = sorted(
        list(YT_LOGS[0]['calculation']['classes'].keys()),
    )
    assert calculated_classes == expected_classes


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business', 'vip'],
    SURGE_CALCULATOR_OMIT_UNNEEDED_CATEGORIES=True,
)
async def test_calculate_dependency(taxi_surge_calculator, testpoint_service):
    YT_LOGS.clear()
    request = {
        'point_a': [37.583369, 55.778821],
        'classes': ['econom', 'vip'],
        'intent': 'surge_sampling',
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200

    assert YT_LOGS
    calculated_classes = sorted(
        list(YT_LOGS[0]['calculation']['classes'].keys()),
    )
    # vip depends on business
    assert calculated_classes == ['business', 'econom', 'vip']


@pytest.mark.config(
    ALL_CATEGORIES=[], SURGE_CALCULATOR_OMIT_UNNEEDED_CATEGORIES=True,
)
async def test_add_base_class(taxi_surge_calculator, testpoint_service):
    YT_LOGS.clear()
    request = {'point_a': [37.583369, 55.778821], 'classes': []}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200

    assert YT_LOGS
    calculated_classes = sorted(
        list(YT_LOGS[0]['calculation']['classes'].keys()),
    )
    assert calculated_classes == ['econom']
