import datetime
import http
import time

import bson
import freezegun
import pymongo

from taxi.util import graphite


ENTITIES_COUNT = 10
TRUE_LAG = 1


async def prepare_entities(db, qc_client, entity_settings, entity_type):
    """"Populates count entities for entity_type
        in qc_entities with timestamps from now-ENTITIES_COUNT to now-1"""
    # устанавливаем data
    data = []
    for i in range(ENTITIES_COUNT):
        data.append(
            {'id': '{id}'.format(id=i), 'data': {'name': '{id}'.format(id=i)}},
        )
    response = await qc_client.post(
        '/api/v1/data/list', params={'type': entity_type}, json=data,
    )
    assert response.status == http.HTTPStatus.OK

    # устанавливаем state
    states = []
    for i in range(ENTITIES_COUNT):
        states.append({'id': '{id}'.format(id=i), 'enabled': True})
    # берём первый экзамен по списку
    exam_dict = entity_settings[entity_type]
    exam_code = next(iter(exam_dict['exams'].values()))['code']
    response = await qc_client.post(
        '/api/v1/state/list',
        params={'type': entity_type, 'exam': exam_code},
        json=states,
    )

    assert response.status == http.HTTPStatus.OK

    # устанавливаем state.modified_timestamp от 0 до ENTITIES_COUNT
    updates = []
    # используем текущее время
    now = datetime.datetime.now().timestamp()
    for i in range(ENTITIES_COUNT):
        updates.append(
            pymongo.operations.UpdateOne(
                filter={'entity_id': f'{i}', 'entity_type': entity_type},
                update={
                    '$set': {
                        'state.modified_timestamp': bson.timestamp.Timestamp(
                            int(now - i - TRUE_LAG), 0,
                        ),
                    },
                },
            ),
        )
    await db.qc_entities.bulk_write(updates)


@freezegun.freeze_time('2018-01-14 03:21:34', tz_offset=3)
async def test_metrics_sending(
        patch, qc_client, db, qc_cache, task_lag_metrics,
):
    entity_settings = qc_cache.entity_settings()
    for entity_type in entity_settings:
        await prepare_entities(db, qc_client, entity_settings, entity_type)
    # мокаем графит
    graphite_data = []

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    #  pylint: disable=unused-variable
    async def send_mock(metric, value, timestamp):
        graphite_data.append(
            {
                'metric': (
                    f'cluster.geo.taxi.service_stats.{graphite.ENV}.'
                    f'{metric}'
                ),
                'value': value,
                'timestamp': timestamp,
            },
        )

    # считаем метрики
    await task_lag_metrics()
    # асёртим
    graphite_timestamp = time.time()
    assert graphite_data == [
        {
            'metric': (
                f'cluster.geo.taxi.service_stats.{graphite.ENV}'
                '.qc.lags.quality_control_driver'
            ),
            'value': TRUE_LAG,
            'timestamp': graphite_timestamp,
        },
        {
            'metric': (
                f'cluster.geo.taxi.service_stats.{graphite.ENV}'
                '.qc.lags.quality_control_car'
            ),
            'value': TRUE_LAG,
            'timestamp': graphite_timestamp,
        },
    ]
