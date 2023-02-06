import pytest

from . import configs
from . import experiments


async def get_fallbacks_layout_count(taxi_eats_layout_constructor_monitor):
    metric = await taxi_eats_layout_constructor_monitor.get_metric(
        'layout-component',
    )
    return metric['fallbacks_layout_count']


@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_FALLBACK_LAYOUT={
        'fallback_enabled': True,
        'layout_slug': 'fallback_layout',
        'collection_layout_slug': '',
    },
)
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template',
    },
)
@pytest.mark.experiments3(filename='eats_layout_fallback.json')
async def test_eats_layout_fallback_not_in_db(
        taxi_eats_layout_constructor,
        mockserver,
        taxi_eats_layout_constructor_monitor,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return {}

    fallbacks_layout_count_old = await get_fallbacks_layout_count(
        taxi_eats_layout_constructor_monitor,
    )

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )
    assert response.status_code == 200

    fallbacks_layout_count = await get_fallbacks_layout_count(
        taxi_eats_layout_constructor_monitor,
    )
    assert fallbacks_layout_count - fallbacks_layout_count_old == 1


@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_FALLBACK_LAYOUT={
        'fallback_enabled': True,
        'layout_slug': 'fallback_layout',
        'collection_layout_slug': '',
    },
)
async def test_eats_layout_fallback_no_experiment(
        taxi_eats_layout_constructor,
        mockserver,
        taxi_eats_layout_constructor_monitor,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return {}

    fallbacks_layout_count_old = await get_fallbacks_layout_count(
        taxi_eats_layout_constructor_monitor,
    )

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )
    assert response.status_code == 200

    fallbacks_layout_count = await get_fallbacks_layout_count(
        taxi_eats_layout_constructor_monitor,
    )
    assert fallbacks_layout_count - fallbacks_layout_count_old == 1


@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_FALLBACK_LAYOUT={
        'fallback_enabled': True,
        'layout_slug': 'unknown',
        'collection_layout_slug': '',
    },
)
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template',
    },
)
async def test_eats_layout_fallback_wrong_fallback_layout(
        taxi_eats_layout_constructor,
        mockserver,
        taxi_eats_layout_constructor_monitor,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return {}

    fallbacks_layout_count_old = await get_fallbacks_layout_count(
        taxi_eats_layout_constructor_monitor,
    )

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )
    assert response.status_code == 500

    fallbacks_layout_count = await get_fallbacks_layout_count(
        taxi_eats_layout_constructor_monitor,
    )
    assert fallbacks_layout_count - fallbacks_layout_count_old == 0


@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_FALLBACK_LAYOUT={
        'fallback_enabled': True,
        'layout_slug': 'fallback_layout',
        'collection_layout_slug': 'fallback_layout',
    },
)
@configs.layout_experiment_name()
@pytest.mark.parametrize(
    'fallback_count',
    [
        pytest.param(
            0,
            marks=(experiments.layout('integer_overflow_and_carousel')),
            id='one widget - no fallback',
        ),
        pytest.param(
            1,
            marks=(experiments.layout('integer_overflow')),
            id='no widgets - fallback',
        ),
    ],
)
async def test_widget_create_error(
        taxi_eats_layout_constructor,
        mockserver,
        taxi_eats_layout_constructor_monitor,
        fallback_count,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        return {}

    fallbacks_layout_count_old = await get_fallbacks_layout_count(
        taxi_eats_layout_constructor_monitor,
    )

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )
    assert response.status_code == 200

    fallbacks_layout_count = await get_fallbacks_layout_count(
        taxi_eats_layout_constructor_monitor,
    )
    assert (
        fallbacks_layout_count - fallbacks_layout_count_old == fallback_count
    )
