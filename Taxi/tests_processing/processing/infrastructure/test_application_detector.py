import pytest


@pytest.mark.processing_queue_config(
    'queue.yaml', scope='testsuite', queue='example',
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
async def test_application_detector(processing, use_ydb, use_fast_flow):
    result = await processing.testsuite.example.handle_single_event(
        'item_id_1',
        pipeline='default-pipeline',
        initial_state={
            'user-aget': (
                'yandex-taxi/3.96.0.60672 Android/8.0.0 (samsung; SM-G930F)'
            ),
        },
        stage_id='single-stage',
    )
    app_vars = result['app_vars']
    assert app_vars == {
        'app_brand': 'yataxi',
        'app_build': 'release',
        'app_name': 'android',
        'app_ver1': '3',
        'app_ver2': '96',
        'app_ver3': '0',
        'platform_ver1': '8',
        'platform_ver2': '0',
        'platform_ver3': '0',
    }
