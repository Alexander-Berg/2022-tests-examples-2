import json

import pytest

from tests_processing import util

TEST_TEAM = {
    'description': (
        'Группа разработки инфраструктуры пользовательских продуктов'
    ),
    'staff_groups': [
        'yandex_distproducts_browserdev_mobile_taxi_9720_dep95813',
    ],
}
MONITORING_TEAMS_SETTINGS = {
    'aggregation-interval': 60,
    'min-events': 0,
    'error-threshold': 50,
}
JUGGLER_RESPONSE = {
    'accepted_events': 1,
    'events': [{'code': 200}],
    'success': True,
}

OK_MESSAGE = 'pipelines, stages and handlers are working fine'


@pytest.mark.config(
    MONITORING_TEAMS_SETTINGS=MONITORING_TEAMS_SETTINGS,
    DEV_TEAMS={'test-team': TEST_TEAM},
)
@pytest.mark.parametrize(
    'fallback_activate, status', [(False, 'OK'), (True, 'CRIT')],
)
@pytest.mark.parametrize(
    'descr',
    [
        pytest.param(
            'Handlers failing:\n'
            '  100%	handler <- stage-1 <- default-pipeline\n',
            marks=[
                pytest.mark.processing_queue_config(
                    'handler.yaml',
                    fallback_resource_url=util.UrlMock('/fallback'),
                    scope='testsuite',
                    queue='example',
                ),
            ],
        ),
        pytest.param(
            'Stages failing:\n  100%	stage-1 <- default-pipeline\n',
            marks=[
                pytest.mark.processing_queue_config(
                    'stage.yaml',
                    fallback_resource_url=util.UrlMock('/fallback'),
                    scope='testsuite',
                    queue='example',
                ),
            ],
        ),
        pytest.param(
            'Pipelines failing:\n' '  100%	default-pipeline\n',
            marks=[
                pytest.mark.processing_queue_config(
                    'pipeline.yaml',
                    fallback_resource_url=util.UrlMock('/fallback'),
                    scope='testsuite',
                    queue='example',
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_basic_monitoring(
        taxi_processing,
        processing,
        mockserver,
        fallback_activate,
        status,
        descr,
        taxi_processing_monitor,
        use_ydb,
        use_fast_flow,
):
    @mockserver.json_handler('/fallback')
    def _mock_fallback(request):
        if fallback_activate:
            return mockserver.make_response(status=500)
        return {'result': 'ok'}

    item_id = '1'
    my_payload = {}
    if not fallback_activate:
        my_payload['failure'] = 'no'

    await processing.testsuite.example.send_event(
        item_id, payload=my_payload, expect_fail=fallback_activate,
    )

    metrics = await taxi_processing_monitor.get_metric('processing-ng')
    data = metrics['queue']['internals']['testsuite']['example']
    assert data.get('pipelines')
    assert data.get('stages')
    assert data.get('handlers')

    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert len(data['events']) == 1
        assert data['events'][0] == {
            'description': (
                f'{status}:\n{OK_MESSAGE if status == "OK" else descr}'
            ),
            'instance': '',
            'service': f'autogen_test-team_testsuite/example',
            'status': f'{status}',
        }
        return JUGGLER_RESPONSE

    await taxi_processing.run_periodic_task('testsuite/example-juggler-push')
    assert events_handler.times_called == 1


@pytest.mark.config(
    MONITORING_TEAMS_SETTINGS=MONITORING_TEAMS_SETTINGS,
    DEV_TEAMS={'test-team': TEST_TEAM},
)
@pytest.mark.processing_queue_config(
    'disabled_handler.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_monitoring_disabled_handler_monitoring(
        taxi_processing, processing, mockserver, use_ydb, use_fast_flow,
):
    item_id = '1'

    await processing.testsuite.example.handle_single_event(item_id, payload={})

    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert len(data['events']) == 1
        assert data['events'][0] == {
            'description': f'OK:\n{OK_MESSAGE}',
            'instance': '',
            'service': f'autogen_test-team_testsuite/example',
            'status': f'OK',
        }
        return JUGGLER_RESPONSE

    await taxi_processing.run_periodic_task('testsuite/example-juggler-push')
    assert events_handler.times_called == 1


@pytest.mark.config(
    MONITORING_TEAMS_SETTINGS=MONITORING_TEAMS_SETTINGS,
    DEV_TEAMS={'test-team': TEST_TEAM},
)
@pytest.mark.processing_queue_config(
    'without_handlers.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_monitoring_without_handlers_monitoring(
        taxi_processing, processing, mockserver, use_ydb, use_fast_flow,
):
    item_id = '1'

    await processing.testsuite.example.handle_single_event(item_id, payload={})

    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert not data['events']
        return JUGGLER_RESPONSE

    await taxi_processing.run_periodic_task('testsuite/example-juggler-push')
    assert events_handler.times_called == 1


@pytest.mark.config(
    MONITORING_TEAMS_SETTINGS=MONITORING_TEAMS_SETTINGS,
    DEV_TEAMS={'test-team': TEST_TEAM},
)
@pytest.mark.processing_queue_config(
    'two_handlers.yaml',
    fallback_resource_url=util.UrlMock('/fallback'),
    scope='testsuite',
    queue='example',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_monitoring_with_two_handlers(
        taxi_processing, processing, mockserver, use_ydb, use_fast_flow,
):
    item_id = '1'

    @mockserver.json_handler('/fallback')
    def mock_fallback(request):
        return mockserver.make_response(status=500)

    await processing.testsuite.example.handle_single_event(item_id, payload={})
    assert mock_fallback.times_called == 1

    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert data['events'][0] == {
            'description': (
                'CRIT:\nHandlers failing:\n'
                '  100%	handler-1 <- stage-1 <- default-pipeline\n'
            ),
            'instance': '',
            'service': f'autogen_test-team_testsuite/example',
            'status': f'CRIT',
        }
        return JUGGLER_RESPONSE

    await taxi_processing.run_periodic_task('testsuite/example-juggler-push')
    assert events_handler.times_called == 1
