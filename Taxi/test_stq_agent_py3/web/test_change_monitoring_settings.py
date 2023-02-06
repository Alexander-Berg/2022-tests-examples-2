import pytest


async def test_change_monitoring_settings_404(web_app_client):
    response = await web_app_client.put(
        '/queue/monitor_settings/',
        json={
            'queue_name': 'non_existent_queue',
            'thresholds': {'total': {'warning': 1, 'critical': 10}},
            'version': 0,
        },
    )
    assert response.status == 404


async def test_change_monitoring_settings_409(web_app_client, db):
    response = await web_app_client.put(
        '/queue/monitor_settings/',
        json={
            'queue_name': 'example_queue',
            'thresholds': {'total': {'warning': 1, 'critical': 10}},
            'version': 2,
        },
    )
    assert response.status == 409


async def test_change_monitoring_settings_200(web_app_client, db):
    response = await web_app_client.put(
        '/queue/monitor_settings/',
        json={
            'queue_name': 'example_queue',
            'thresholds': {'total': {'warning': 1, 'critical': 10}},
            'version': 3,
        },
    )
    assert response.status == 200
    assert (
        await db.stq_config.find_one(
            {'_id': 'example_queue'}, ['monitoring.thresholds'],
        )
    )['monitoring']['thresholds'] == {'total': {'warning': 1, 'critical': 10}}


@pytest.mark.parametrize(
    'queue, namespace', [('with_tplatform', 'lavka'), ('example_queue', None)],
)
async def test_monitor_settings_with_tplatform(
        web_app_client, queue, namespace,
):
    response = await web_app_client.put(
        '/queue/monitor_settings/',
        json={
            'queue_name': queue,
            'thresholds': {'total': {'warning': 1, 'critical': 10}},
            'version': 3,
        },
    )
    assert response.status == 200
    assert (await response.json()).get('tplatform_namespace') == namespace
