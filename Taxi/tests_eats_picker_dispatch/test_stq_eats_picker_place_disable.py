import datetime
import math

import pytest
import pytz

from . import utils

REASON = 'place_disable_offset_time exceeded'
TEMPORARY_DISABLE_CODE = 100


@utils.periodic_dispatcher_config3()
@pytest.mark.now
async def test_stq_eats_picker_place_disable(
        places_toggled_metric_diff,
        stq_runner,
        places_environment,
        create_place,
        get_places,
        now,
):
    place_id = places_environment.create_places(1)[0]
    create_place(place_id=place_id, enabled=True)

    await stq_runner.eats_picker_place_disable.call(
        task_id=str(place_id),
        kwargs={
            'place_id': place_id,
            'reason': REASON,
            'polling_delay': 5,
            'polling_timeout': 600,
        },
    )

    place = get_places([place_id])[0]
    assert not place['enabled']
    assert place['auto_disabled_at'] == now.replace(tzinfo=pytz.UTC)
    assert places_environment.mock_places_disable.times_called == 1
    assert not places_environment.catalog_places[place_id]['enabled']
    assert not places_environment.core_places[place_id]['available']
    assert places_environment.mock_retrieve_places.times_called == 2
    assert places_environment.mock_retrieve_delivery_zones.times_called == 0
    metrics = await places_toggled_metric_diff()
    assert metrics == {str(place_id): {'times-disabled': 1}}


@utils.periodic_dispatcher_config3()
@pytest.mark.now
async def test_stq_eats_picker_place_disable_polling(
        places_toggled_metric_diff,
        mockserver,
        stq_runner,
        places_environment,
        create_place,
        get_places,
        now,
):
    place_id = places_environment.create_places(1)[0]
    create_place(place_id=place_id, enabled=True)

    @mockserver.json_handler('/eats-core/v1/places/disable')
    def mock_eats_core_places_disable(request):
        return {'payload': {'disabled_places': [place_id], 'errors': []}}

    places_environment.mock_places_disable = mock_eats_core_places_disable

    @mockserver.json_handler('/eats-core/v1/places/info')
    async def mock_eats_core_places_info(request):
        if mock_eats_core_places_info.times_called == 4:
            places_environment.disable_place(place_id, TEMPORARY_DISABLE_CODE)
        return await places_environment.mock_core_places_info(request)

    await stq_runner.eats_picker_place_disable.call(
        task_id=str(place_id),
        kwargs={
            'place_id': place_id,
            'reason': REASON,
            'polling_delay': 0,
            'polling_timeout': 600,
        },
    )

    assert places_environment.mock_places_disable.times_called == 1
    assert mock_eats_core_places_info.times_called == 5
    assert places_environment.mock_core_places_info.times_called == 5
    assert places_environment.mock_retrieve_places.times_called == 5
    place = get_places([place_id])[0]
    assert not place['enabled']
    assert place['auto_disabled_at'] == now.replace(tzinfo=pytz.UTC)
    metrics = await places_toggled_metric_diff()
    assert metrics == {str(place_id): {'times-disabled': 1}}


@utils.periodic_dispatcher_config3()
@pytest.mark.now
@pytest.mark.parametrize(
    'enabled_in_catalog, enabled_in_core, is_manually_disabled',
    [(True, None, True), (None, True, True), (None, None, False)],
)
async def test_stq_eats_picker_place_disable_bad_catalog_or_core_response(
        places_toggled_metric_diff,
        stq_runner,
        places_environment,
        create_place,
        get_places,
        now,
        enabled_in_catalog,
        enabled_in_core,
        is_manually_disabled,
):
    place_id = places_environment.create_places(
        1,
        dict(enabled=enabled_in_catalog),
        dict(available=enabled_in_core, disabled_details={'reason': 99}),
    )[0]
    create_place(place_id=place_id, enabled=True)

    await stq_runner.eats_picker_place_disable.call(
        task_id=str(place_id),
        kwargs={
            'place_id': place_id,
            'reason': REASON,
            'polling_delay': 0,
            'polling_timeout': 600,
        },
    )

    place = get_places([place_id])[0]
    metrics = await places_toggled_metric_diff()
    if is_manually_disabled:
        assert not place['enabled']
        assert place['auto_disabled_at'] == now.replace(tzinfo=pytz.UTC)
        assert places_environment.mock_retrieve_places.times_called == 2
        assert places_environment.mock_core_places_info.times_called == 2
        assert metrics == {str(place_id): {'times-disabled': 1}}
    else:
        assert place['enabled']
        assert place['auto_disabled_at'] is None
        assert places_environment.mock_retrieve_places.times_called == 1
        assert places_environment.mock_core_places_info.times_called == 1
        assert metrics == {str(place_id): {'disable-fails': 1}}


@utils.periodic_dispatcher_config3()
@pytest.mark.now
@pytest.mark.parametrize(
    'enabled_in_catalog, enabled_in_core, is_manually_disabled',
    [(True, False, False), (False, True, True), (False, False, False)],
)
async def test_stq_eats_picker_place_disable_already_disabled_in_cs_or_core(
        places_toggled_metric_diff,
        stq_runner,
        places_environment,
        create_place,
        get_places,
        now,
        enabled_in_catalog,
        enabled_in_core,
        is_manually_disabled,
):
    place_id = places_environment.create_places(
        1,
        dict(enabled=enabled_in_catalog),
        dict(available=enabled_in_core, disabled_details={'reason': 99}),
    )[0]
    auto_disabled_at = now.replace(tzinfo=pytz.UTC) - datetime.timedelta(
        seconds=3600,
    )
    create_place(
        place_id=place_id, enabled=False, auto_disabled_at=auto_disabled_at,
    )

    await stq_runner.eats_picker_place_disable.call(
        task_id=str(place_id),
        kwargs={
            'place_id': place_id,
            'reason': REASON,
            'polling_delay': 0,
            'polling_timeout': 600,
        },
    )

    place = get_places([place_id])[0]
    metrics = await places_toggled_metric_diff()
    assert not place['enabled']
    if is_manually_disabled:
        assert place['auto_disabled_at'] == now.replace(tzinfo=pytz.UTC)
        assert places_environment.mock_retrieve_places.times_called == 2
        assert places_environment.mock_core_places_info.times_called == 2
        assert metrics == {str(place_id): {'times-disabled': 1}}
    else:
        assert place['auto_disabled_at'] == auto_disabled_at
        assert places_environment.mock_retrieve_places.times_called == 1
        assert places_environment.mock_core_places_info.times_called == 1
        assert metrics == {}


@utils.periodic_dispatcher_config3()
async def test_stq_eats_picker_place_disable_core_fail(
        places_toggled_metric_diff,
        mockserver,
        stq_runner,
        places_environment,
        create_place,
        get_places,
):
    place_id = places_environment.create_places(1)[0]
    create_place(place_id=place_id, enabled=True)

    @mockserver.json_handler('/eats-core/v1/places/disable')
    def mock_eats_core_places_disable(request):
        return {'payload': {'disabled_places': [], 'errors': []}}

    places_environment.mock_places_disable = mock_eats_core_places_disable

    await stq_runner.eats_picker_place_disable.call(
        task_id=str(place_id),
        kwargs={
            'place_id': place_id,
            'reason': REASON,
            'polling_delay': 5,
            'polling_timeout': 600,
        },
    )

    place = get_places([place_id])[0]
    assert place['enabled']
    assert place['auto_disabled_at'] is None
    assert places_environment.mock_places_disable.times_called == 1
    assert places_environment.mock_retrieve_places.times_called == 1
    assert places_environment.mock_core_places_info.times_called == 1
    metrics = await places_toggled_metric_diff()
    assert metrics == {str(place_id): {'disable-fails': 1}}


@utils.periodic_dispatcher_config3()
@pytest.mark.now
async def test_stq_eats_picker_place_disable_timeout(
        taxi_eats_picker_dispatch,
        places_toggled_metric_diff,
        mockserver,
        mocked_time,
        testpoint,
        stq_runner,
        places_environment,
        create_place,
        get_places,
        now,
):
    polling_delay = 200
    polling_timeout = 600
    place_id = places_environment.create_places(1)[0]
    create_place(place_id=place_id, enabled=True)

    @mockserver.json_handler('/eats-core/v1/places/disable')
    def mock_eats_core_places_disable(request):
        return {'payload': {'disabled_places': [place_id], 'errors': []}}

    places_environment.mock_places_disable = mock_eats_core_places_disable

    @testpoint('eats_picker_dispatch::polling-delay')
    async def loop_finished(arg):
        mocked_time.sleep(polling_delay)
        await taxi_eats_picker_dispatch.invalidate_caches()

    await stq_runner.eats_picker_place_disable.call(
        task_id=str(place_id),
        kwargs={
            'place_id': place_id,
            'reason': REASON,
            'polling_delay': 0,
            'polling_timeout': polling_timeout,
        },
    )

    place = get_places([place_id])[0]
    assert place['enabled']
    assert place['auto_disabled_at'] is None
    loops = math.ceil(polling_timeout / polling_delay)
    assert loop_finished.times_called == loops
    assert places_environment.mock_retrieve_places.times_called == loops + 1
    assert places_environment.mock_places_disable.times_called == 1
    metrics = await places_toggled_metric_diff()
    assert metrics == {str(place_id): {'disable-fails': 1}}


@utils.periodic_dispatcher_config3()
@pytest.mark.now
async def test_stq_eats_picker_place_disable_invalidated_cs_response(
        places_toggled_metric_diff,
        mockserver,
        stq_runner,
        places_environment,
        create_place,
        get_places,
        now,
):
    place_id = places_environment.create_places(
        1, core_kwargs=dict(available=None),
    )[0]
    create_place(place_id=place_id, enabled=True)

    @mockserver.json_handler('/eats-core/v1/places/disable')
    def mock_eats_core_places_disable(request):
        return {'payload': {'disabled_places': [place_id], 'errors': []}}

    places_environment.mock_places_disable = mock_eats_core_places_disable

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    async def _mock_retrieve_places(request):
        response = await places_environment.mock_retrieve_places(request)
        catalog_place = places_environment.catalog_places[place_id]
        catalog_place['enabled'] = None
        return response

    await stq_runner.eats_picker_place_disable.call(
        task_id=str(place_id),
        kwargs={
            'place_id': place_id,
            'reason': REASON,
            'polling_delay': 0,
            'polling_timeout': 600,
        },
    )

    place = get_places([place_id])[0]
    assert place['enabled']
    assert place['auto_disabled_at'] is None
    assert places_environment.mock_retrieve_places.times_called == 2
    metrics = await places_toggled_metric_diff()
    assert metrics == {str(place_id): {'disable-fails': 1}}


@utils.periodic_dispatcher_config3()
@pytest.mark.now
async def test_stq_eats_picker_place_disable_catalog_storage_and_core_error(
        places_toggled_metric_diff,
        mockserver,
        stq_runner,
        places_environment,
        create_place,
        get_places,
):
    place_id = 1
    create_place(place_id=place_id, enabled=True)

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def mock_retrieve_places(request):
        return mockserver.make_response(status=500)

    await stq_runner.eats_picker_place_disable.call(
        task_id=str(place_id),
        kwargs={
            'place_id': place_id,
            'reason': REASON,
            'polling_delay': 0,
            'polling_timeout': 600,
        },
    )

    place = get_places([place_id])[0]
    assert place['enabled']
    assert place['auto_disabled_at'] is None
    assert mock_retrieve_places.times_called == 1
    assert places_environment.mock_retrieve_places.times_called == 0
    metrics = await places_toggled_metric_diff()
    assert metrics == {str(place_id): {'disable-fails': 1}}


@utils.periodic_dispatcher_config3()
@pytest.mark.now
async def test_stq_eats_picker_place_disable_catalog_storage_timeout(
        places_toggled_metric_diff,
        mockserver,
        stq_runner,
        places_environment,
        create_place,
        get_places,
        now,
):
    place_id = places_environment.create_places(
        1, core_kwargs=dict(available=None),
    )[0]
    create_place(place_id=place_id, enabled=True)

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    async def mock_retrieve_places(request):
        if mock_retrieve_places.times_called == 1:
            catalog_place = places_environment.catalog_places[place_id]
            catalog_place['enabled'] = None
            raise mockserver.TimeoutError()
        return await places_environment.mock_retrieve_places(request)

    await stq_runner.eats_picker_place_disable.call(
        task_id=str(place_id),
        kwargs={
            'place_id': place_id,
            'reason': REASON,
            'polling_delay': 0,
            'polling_timeout': 600,
        },
    )

    place = get_places([place_id])[0]
    assert not place['enabled']
    assert place['auto_disabled_at'] == now.replace(tzinfo=pytz.UTC)
    assert mock_retrieve_places.times_called == 3
    assert places_environment.mock_retrieve_places.times_called == 2
    metrics = await places_toggled_metric_diff()
    assert metrics == {str(place_id): {'times-disabled': 1}}
