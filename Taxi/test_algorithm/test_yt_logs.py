# pylint: disable=W0621
import pytest

from .. import common

YT_LOGS = []


@pytest.fixture
def testpoint_service(testpoint):
    @testpoint('yt_logger::messages::calculations')
    def _handler(data_json):
        YT_LOGS.append(data_json)


@pytest.mark.now('2020-07-06T00:00:00+00:00')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'uberx'],
    SURGE_ENABLE_SURCHARGE=True,
    SURGE_APPLY_BOUNDS_TO_LINEAR_DEPENDENCY_WITH_BASE_TABLE=True,
)
async def test_yt_logs(
        taxi_surge_calculator, load_json, taxi_config, testpoint_service,
):
    YT_LOGS.clear()

    expected_result = common.convert_response(
        load_json('expected_result.old.json'),
        {'experiment_id': 'b66bf587447b401a9e365c1cdffa4ba5'},
    )
    expected_yt_logs = load_json('yt_logs.json')

    req = {
        'tariffs': ['econom', 'uberx'],
        'point_a': [37.58829620633788, 55.77425398624534],
        'tariff_zone': 'moscow',
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=req)

    assert response.status == 200, response.text

    actual_response = response.json()
    calculation_id = actual_response.pop('calculation_id', '')

    assert len(calculation_id) == 32
    expected_yt_logs[0]['calculation_id'] = calculation_id
    del YT_LOGS[-1]['timestamp']

    common.sort_data(actual_response)
    assert actual_response == expected_result

    # check native algorithm logs
    taxi_config.set_values({'SURGE_NATIVE_FALLBACK_FORCE': True})
    await taxi_surge_calculator.invalidate_caches()

    response = await taxi_surge_calculator.post('/v1/calc-surge', json=req)

    assert response.status == 200, response.text

    actual_response = response.json()
    calculation_id = actual_response.pop('calculation_id', '')

    assert len(calculation_id) == 32
    expected_yt_logs[1]['calculation_id'] = calculation_id
    expected_yt_logs[1]['calculation']['response'][
        'calculation_id'
    ] = calculation_id
    del YT_LOGS[-1]['timestamp']
    del YT_LOGS[0]['calculation']['$pipeline_id']

    assert YT_LOGS == expected_yt_logs
