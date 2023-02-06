import datetime

import pytest


@pytest.fixture
def mongodb_collections():
    return ['antifraud_stat']


@pytest.mark.now('2018-07-18T11:20:00')
async def test_metric_storage(web_context):
    name = 'check-card.success'

    web_context.metrics.event(name)
    web_context.metrics.event(name)
    await web_context.metrics.metric_storage.run()

    res = await web_context.mongo.antifraud_stat.find().to_list(None)
    assert len(res) == 1
    doc = res[0]
    doc.pop('_id')
    assert doc == {
        'created': datetime.datetime(2018, 7, 18, 11, 20),
        'metrics': {'check-card_success': 2},
    }


@pytest.mark.parametrize(
    'series,expected_extra',
    [
        (['check-card.success'], []),
        (['check-card.success', 'extra'], ['extra']),
        (['1', '2'], ['1', '2']),
        (None, {}),
    ],
)
@pytest.mark.now('2018-07-18T11:21:42')
@pytest.mark.filldb(antifraud_stat='metric_send')
async def test_metric_send(web_context, mockserver, series, expected_extra):
    @mockserver.json_handler('/solomon/unittests')
    def mock_solomon(request):
        expected_sensors = [
            {
                'labels': {
                    'application': 'antifraud',
                    'metric_name': 'check-card.success',
                },
                'kind': 'IGAUGE',
                'value': 55,
            },
            {
                'labels': {
                    'application': 'antifraud',
                    'metric_name': 'check-card.fail',
                },
                'kind': 'IGAUGE',
                'value': 66,
            },
            {
                'labels': {
                    'application': 'antifraud',
                    'metric_name': 'check-card',
                },
                'kind': 'IGAUGE',
                'value': 121,
            },
        ]
        for extra in expected_extra:
            expected_sensors.append(
                {
                    'labels': {
                        'application': 'antifraud',
                        'metric_name': extra,
                    },
                    'kind': 'IGAUGE',
                    'value': 0,
                },
            )

        def get_sensor_name(sensor):
            return sensor['labels']['metric_name']

        expected_sensors = sorted(expected_sensors, key=get_sensor_name)
        provided_sensors = sorted(
            request.json.pop('sensors'), key=get_sensor_name,
        )
        assert expected_sensors == provided_sensors
        assert request.json == {'ts': 1531912800}
        return {}

    if series:
        web_context.metrics.add_series(series)

    await web_context.metrics.metric_sender.run()
    assert mock_solomon.times_called == 1
