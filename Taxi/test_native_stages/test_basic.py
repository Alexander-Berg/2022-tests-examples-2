import pytest

from .. import common


YT_LOGS = []
JS_PIPELINE_ACTIVITIES = []


@pytest.fixture(autouse=True)
def testpoint_service(testpoint):
    @testpoint('yt_logger::messages::calculations')
    def _handler(data_json):
        YT_LOGS.append(data_json)

    @testpoint('js-pipeline')
    def _handler2(data_json):
        JS_PIPELINE_ACTIVITIES.append(data_json['activity'])


@pytest.mark.config(ALL_CATEGORIES=['econom', 'business'])
@pytest.mark.now('2020-05-27T14:03:10')
async def test_native_stages_basic(taxi_surge_calculator, load_json):
    YT_LOGS.clear()
    JS_PIPELINE_ACTIVITIES.clear()

    request = {
        'point_a': [37.583369, 55.778821],
        'classes': ['econom', 'business'],
    }
    expected = {
        'zone_id': 'MSK-Yandex HQ',
        'user_layer': 'default',
        'experiment_id': 'a29e6a811131450f9a28337906594207',
        'experiment_name': 'default',
        'experiment_layer': 'default',
        'is_cached': False,
        'classes': [
            {
                'name': 'econom',
                'value_raw': 5.0,
                'surge': {'value': 1.0},
                'calculation_meta': {'reason': 'no'},
            },
            {
                'name': 'business',
                'value_raw': 11.0,
                'surge': {'value': 1.0},
                'calculation_meta': {'reason': 'no'},
            },
        ],
        'experiments': [],
        'experiment_errors': [],
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200, response.text
    actual = response.json()

    calculation_id = actual.pop('calculation_id', '')

    assert len(calculation_id) == 32

    common.sort_data(expected)
    common.sort_data(actual)

    assert actual == expected
    del YT_LOGS[0]['calculation']['$pipeline_id']

    expected_yt_logs = common.unescape_yt_logs(load_json('yt_logs.json'))
    expected_yt_logs[0]['calculation_id'] = calculation_id

    assert YT_LOGS == expected_yt_logs
    assert JS_PIPELINE_ACTIVITIES == ['run_pre_js_native_section']
