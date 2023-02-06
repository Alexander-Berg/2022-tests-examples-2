import mock
import dmp_suite.datetime_utils as dtu
from dmp_suite.maintenance.monitoring.solomon import (
    SolomonClient,
    DummySolomonClient
)


POST_FN = 'dmp_suite.maintenance.monitoring.solomon._post_data'
LOGGER = 'dmp_suite.maintenance.monitoring.solomon.logger'


def get_dttm_ts(dttm_str):
    dttm = dtu.parse_datetime(dttm_str)
    ts = dtu.timestamp(dttm)
    return dttm, ts


url = 'localhost:34400'
common_labels = dict(app='dwh', component='test')
dttm1, ts1 = get_dttm_ts('2019-11-30 13:51:27')
dttm2, ts2 = get_dttm_ts('2020-02-23 21:07:19')
sensor_values = [
    {'ts': ts1, 'value': 1, 'labels': dict(sensor='sensor1')},
    {'ts': ts1, 'value': 2.3, 'labels': dict(sensor='sensor2', l1='t1')},
    {'ts': ts1, 'value': -3.0, 'labels': dict(sensor='sensor3', l2='t2', l3='t3')},
    {'ts': ts2, 'value': 4, 'labels': dict(sensor='sensor1', l4='t4', l5='t5', l6='t6')},
    {'ts': ts2, 'value': 5.1, 'labels': dict(sensor='sensor2', l7='t7', l8='t8')},
    {'ts': ts2, 'value': -6.7, 'labels': dict(sensor='sensor3', l9='t9')},
    {'ts': ts2, 'value': 7, 'labels': dict(sensor='sensorN')},
]


@mock.patch(LOGGER)
@mock.patch(POST_FN)
def test_solomon_single_mode(post_fn, logger):

    client = SolomonClient(url, **common_labels)
    client.send('sensor1', 1, dttm1)
    client.send('sensor2', 2.3, dttm1, l1='t1')
    client.send('sensor3', -3.0, dttm1, l2='t2', l3='t3')
    client.send('sensor1', 4, dttm2, l4='t4', l5='t5', l6='t6')
    client.send('sensor2', 5.1, dttm2, l7='t7', l8='t8')
    client.send('sensor3', -6.7, dttm2, l9='t9')
    client.send('sensorN', 7, dttm2)

    post_fn.assert_has_calls([
        mock.call(url, {'commonLabels': common_labels, 'sensors': [val]})
        for val in sensor_values
    ])

    logger.debug.assert_has_calls([
        mock.call("Push to Solomon: %i values with common labels %s", 1, common_labels)
        for _ in sensor_values
    ])


@mock.patch(LOGGER)
@mock.patch(POST_FN)
def test_solomon_batch_mode(post_fn, logger):

    with SolomonClient(url, batch_size=3, **common_labels) as client:
        client.send('sensor1', 1, dttm1)
        client.send('sensor2', 2.3, dttm1, l1='t1')
        client.send('sensor3', -3.0, dttm1, l2='t2', l3='t3')
        client.send('sensor1', 4, dttm2, l4='t4', l5='t5', l6='t6')
        client.send('sensor2', 5.1, dttm2, l7='t7', l8='t8')
        client.send('sensor3', -6.7, dttm2, l9='t9')
        client.send('sensorN', 7, dttm2)

    post_fn.assert_has_calls([
        mock.call(url, {'commonLabels': common_labels, 'sensors': sensor_values[:3]}),
        mock.call(url, {'commonLabels': common_labels, 'sensors': sensor_values[3:6]}),
        mock.call(url, {'commonLabels': common_labels, 'sensors': sensor_values[6:]}),
    ])

    logger.debug.assert_has_calls([
        mock.call("Push to Solomon: %i values with common labels %s", 3, common_labels),
        mock.call("Push to Solomon: %i values with common labels %s", 3, common_labels),
        mock.call("Push to Solomon: %i values with common labels %s", 1, common_labels)
    ])


@mock.patch(LOGGER)
@mock.patch(POST_FN)
def test_dummy_solomon_batch_mode(post_fn, logger):

    with DummySolomonClient(url, **common_labels) as client:
        client.send('sensor1', 1, dttm1)
        client.send('sensor2', 2.3, dttm1, l1='t1')
        client.send('sensor3', -3.0, dttm1, l2='t2', l3='t3')
        client.send('sensor1', 4, dttm2, l4='t4', l5='t5', l6='t6')
        client.send('sensor2', 5.1, dttm2, l7='t7', l8='t8')
        client.send('sensor3', -6.7, dttm2, l9='t9')
        client.send('sensorN', 7, dttm2)

    post_fn.assert_not_called()
    logger.debug.assert_called_with(
        "Push to Solomon: %i values with common labels %s", 7, common_labels
    )
