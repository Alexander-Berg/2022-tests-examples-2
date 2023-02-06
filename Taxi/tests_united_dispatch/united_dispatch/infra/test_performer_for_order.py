import datetime

import pytest

from testsuite.utils import matching

CANDIDATE_ID = (
    'a3608f8f7ee84e0b9c21862beef7e48d_3a21d574bbdc488c9b62a07e6a9a4147'
)


def _make_performer_request(
        *,
        taxi_order_id,
        generation=1,
        version=1,
        wave=1,
        order_created_ts=1584378627.69,
):
    return {
        'order_id': taxi_order_id,
        'allowed_classes': ['cargo'],
        'lookup': {'generation': generation, 'version': version, 'wave': wave},
        'order': {'created': order_created_ts, 'nearest_zone': 'moscow'},
    }


@pytest.fixture(name='reset_stats')
async def _reset_stats(taxi_united_dispatch, testpoint):
    await taxi_united_dispatch.tests_control(reset_metrics=True)

    @testpoint('stage-lookup-stats::with-current-epoch')
    def _with_current_epoch(param):
        return {'with_current_epoch': True}

    yield


async def test_performer_not_found_no_waybill(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        taxi_united_dispatch_monitor,
        reset_stats,
):
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(taxi_order_id='unknown_waybill'),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'irrelevant'}

    stats = await taxi_united_dispatch_monitor.get_metric('lookup-stats')
    assert stats == {
        'event': {
            '$meta': {'solomon_children_labels': 'code'},
            'waybill_not_found': 1,
        },
        'per_planner': {'$meta': {'solomon_children_labels': 'planner_type'}},
    }


async def test_performer_not_found_empty_candidate(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        get_single_waybill,
        taxi_united_dispatch_monitor,
        reset_stats,
):
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    waybill = get_single_waybill()

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'],
        ),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'irrelevant'}

    stats = await taxi_united_dispatch_monitor.get_metric('lookup-stats')
    assert stats == {
        'per_planner': {
            '$meta': {'solomon_children_labels': 'planner_type'},
            'crutches': {
                '$meta': {'solomon_children_labels': 'state'},
                'candidate_not_found': {
                    'count': 1,
                    'lag': {
                        '$meta': {'solomon_children_labels': 'percentile'},
                        'p0': 0,
                        'p100': 0,
                        'p50': 0,
                        'p90': 0,
                        'p95': 0,
                        'p98': 0,
                        'p99': 0,
                        'p99_6': 0,
                        'p99_9': 0,
                    },
                },
            },
        },
        'event': {'$meta': {'solomon_children_labels': 'code'}},
    }


async def test_performer_not_found_reapeat_candidate(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_lookup_flow,
        get_single_waybill,
        taxi_united_dispatch_monitor,
        reset_stats,
        exp_performer_repeat_search,
):
    await exp_performer_repeat_search()

    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    waybill = get_single_waybill()
    set_waybill_lookup_flow(
        waybill_ref=waybill['id'], lookup_flow='united-dispatch',
    )
    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'],
        ),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'not_found'}

    stats = await taxi_united_dispatch_monitor.get_metric('lookup-stats')
    assert stats == {
        'per_planner': {
            '$meta': {'solomon_children_labels': 'planner_type'},
            'crutches': {
                '$meta': {'solomon_children_labels': 'state'},
                'candidate_not_found_yet': {
                    'count': 1,
                    'lag': {
                        '$meta': {'solomon_children_labels': 'percentile'},
                        'p0': 0,
                        'p100': 0,
                        'p50': 0,
                        'p90': 0,
                        'p95': 0,
                        'p98': 0,
                        'p99': 0,
                        'p99_6': 0,
                        'p99_9': 0,
                    },
                },
            },
        },
        'event': {'$meta': {'solomon_children_labels': 'code'}},
    }


@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_performer_found(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        get_single_waybill,
        taxi_united_dispatch_monitor,
        reset_stats,
        mocked_time,
):
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    waybill = get_single_waybill()
    set_waybill_candidate(waybill_ref=waybill['id'], performer_id=CANDIDATE_ID)
    mocked_time.sleep(10)

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'],
        ),
    )

    assert response.status_code == 200
    assert response.json()['candidate']['id'] == CANDIDATE_ID

    stats = await taxi_united_dispatch_monitor.get_metric('lookup-stats')

    assert stats == {
        'per_planner': {
            '$meta': {'solomon_children_labels': 'planner_type'},
            'crutches': {
                '$meta': {'solomon_children_labels': 'state'},
                'successful': {
                    'count': 1,
                    'lag': {
                        '$meta': {'solomon_children_labels': 'percentile'},
                        'p0': 10000,
                        'p100': 10000,
                        'p50': 10000,
                        'p90': 10000,
                        'p95': 10000,
                        'p98': 10000,
                        'p99': 10000,
                        'p99_6': 10000,
                        'p99_9': 10000,
                    },
                },
            },
        },
        'event': {'$meta': {'solomon_children_labels': 'code'}},
    }


async def test_performer_repeated(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        get_single_waybill,
):
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    waybill = get_single_waybill()
    set_waybill_candidate(waybill_ref=waybill['id'], performer_id=CANDIDATE_ID)

    first_response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'],
        ),
    )

    assert first_response.status_code == 200
    assert first_response.json()['candidate']['id'] == CANDIDATE_ID

    second_response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'],
            version=4,
            wave=4,
        ),
    )

    assert second_response.status_code == 200
    assert second_response.json()['candidate']['id'] == CANDIDATE_ID


async def test_performer_repeated_irrelevant(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        get_single_waybill,
):
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    waybill = get_single_waybill()
    set_waybill_candidate(waybill_ref=waybill['id'], performer_id=CANDIDATE_ID)

    first_response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'],
        ),
    )

    assert first_response.status_code == 200
    assert first_response.json()['candidate']['id'] == CANDIDATE_ID

    second_response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'], generation=2,
        ),
    )

    assert second_response.status_code == 200
    assert second_response.json() == {'message': 'irrelevant'}


@pytest.mark.config(
    UNITED_DISPATCH_REJECTED_CANDIDATES_SETTINGS={'enabled': True},
)
async def test_repeat_waybill_search(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        set_waybill_lookup_flow,
        get_single_waybill,
        exp_performer_repeat_search,
):
    await exp_performer_repeat_search()

    # Create waybill and set some candidate first, /performer-for-order should
    # return it

    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    waybill = get_single_waybill()
    set_waybill_candidate(waybill_ref=waybill['id'], performer_id=CANDIDATE_ID)
    set_waybill_lookup_flow(
        waybill_ref=waybill['id'], lookup_flow='united-dispatch',
    )

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'],
        ),
    )

    assert response.status_code == 200
    assert response.json()['candidate']['id'] == CANDIDATE_ID

    # Increase lookup version, this should trigger waybill update and mark
    # waybill for new search

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'], version=2,
        ),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'updated'}

    # Check that candidate was dropped and thus next call should say there is
    # no candidate yet

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'], version=2,
        ),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'not_found'}

    # Set candidate again, check that /performer-for-order will return it

    set_waybill_candidate(waybill_ref=waybill['id'], performer_id=CANDIDATE_ID)

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'], version=2,
        ),
    )

    assert response.status_code == 200
    assert response.json()['candidate']['id'] == CANDIDATE_ID


async def test_multiple_repeat_waybill_search(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        set_waybill_lookup_flow,
        get_single_waybill,
        exp_performer_repeat_search,
):
    await exp_performer_repeat_search()

    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    waybill = get_single_waybill()
    set_waybill_candidate(waybill_ref=waybill['id'], performer_id=CANDIDATE_ID)
    set_waybill_lookup_flow(
        waybill_ref=waybill['id'], lookup_flow='united-dispatch',
    )

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'],
        ),
    )

    assert response.status_code == 200
    assert response.json()['candidate']['id'] == CANDIDATE_ID

    # Increase lookup version, this should trigger waybill update and mark
    # waybill for new search

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'], version=2,
        ),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'updated'}

    # Set candidate and increase lookup version again, still should be updated
    set_waybill_candidate(waybill_ref=waybill['id'], performer_id=CANDIDATE_ID)

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'], version=3,
        ),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'updated'}

    # Set candidate again, check that /performer-for-order will return it

    set_waybill_candidate(waybill_ref=waybill['id'], performer_id=CANDIDATE_ID)

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'], version=3,
        ),
    )

    assert response.status_code == 200
    assert response.json()['candidate']['id'] == CANDIDATE_ID


@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='united_dispatch_should_rebuild_waybill',
    consumers=['united-dispatch/should-rebuild-waybill'],
    clauses=[],
    default_value={'should_rebuild': True},
    is_config=True,
)
async def test_united_dispatch_rebuild_waybill_stq_set(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        get_single_waybill,
        stq,
):
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    waybill = get_single_waybill()
    set_waybill_candidate(waybill_ref=waybill['id'], performer_id=CANDIDATE_ID)

    first_response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'],
        ),
    )

    assert first_response.status_code == 200
    assert first_response.json()['candidate']['id'] == CANDIDATE_ID
    assert not stq.united_dispatch_rebuild_waybill.has_calls

    second_response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id=waybill['waybill']['taxi_order_id'], generation=2,
        ),
    )

    assert second_response.status_code == 200
    assert second_response.json() == {'message': 'updated'}

    assert stq.united_dispatch_rebuild_waybill.has_calls
    assert stq.united_dispatch_rebuild_waybill.next_call()['kwargs'] == {
        'log_extra': {'_link': matching.AnyString()},
        'waybill_ref': waybill['id'],
    }


@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='united_dispatch_should_rebuild_waybill',
    consumers=['united-dispatch/should-rebuild-waybill'],
    clauses=[],
    default_value={'should_rebuild': True},
    is_config=True,
)
async def test_united_dispatch_rebuild_waybill_stq(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        get_single_waybill,
        mockserver,
        stq_runner,
        get_waybill,
):
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    waybill = get_single_waybill()

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/rebuild')
    def mock_v1_waybill_autoreorder(request):
        assert request.json == {'waybill_external_ref': waybill['id']}
        return mockserver.make_response(status=200, json={'result': 'OK'})

    await stq_runner.united_dispatch_rebuild_waybill.call(
        task_id='test',
        kwargs={
            'corp_client_ids': ['some_corp_client_id'],
            'waybill_ref': waybill['id'],
            'waybill_revision': waybill['revision'],
        },
    )
    assert mock_v1_waybill_autoreorder.has_calls
    updated_waybill = get_waybill(waybill['id'])
    assert updated_waybill['revision'] > waybill['revision']
    assert isinstance(updated_waybill['rebuilt_at'], datetime.datetime)


@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='united_dispatch_should_rebuild_waybill',
    consumers=['united-dispatch/should-rebuild-waybill'],
    clauses=[],
    default_value={'should_rebuild': True},
    is_config=True,
)
async def test_united_dispatch_rebuild_waybill_stq_autoreorder_failed(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        get_single_waybill,
        mockserver,
        stq_runner,
        get_waybill,
):
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    waybill = get_single_waybill()

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/rebuild')
    def mock_v1_waybill_autoreorder(request):
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'not_found'},
        )

    await stq_runner.united_dispatch_rebuild_waybill.call(
        task_id='test',
        kwargs={
            'corp_client_ids': ['some_corp_client_id'],
            'waybill_ref': waybill['id'],
            'waybill_revision': waybill['revision'],
        },
    )
    assert mock_v1_waybill_autoreorder.has_calls
    updated_waybill = get_waybill(waybill['id'])
    assert updated_waybill['revision'] == waybill['revision']


@pytest.mark.config(
    UNITED_DISPATCH_PERFORMER_FOR_ORDER_RELEVANCE_TTL={
        'request_irrelevant_after': 30,
    },
)
async def test_no_waybill_delayed(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        taxi_united_dispatch_monitor,
        reset_stats,
        mocked_time,
):
    mocked_time.set(datetime.datetime.now())

    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    order_created_ts = (
        mocked_time.now().replace(tzinfo=datetime.timezone.utc).timestamp()
    )

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id='unknown_waybill', order_created_ts=order_created_ts,
        ),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'delayed'}

    mocked_time.sleep(60)

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id='unknown_waybill', order_created_ts=order_created_ts,
        ),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'irrelevant'}

    stats = await taxi_united_dispatch_monitor.get_metric('lookup-stats')
    assert stats == {
        'event': {
            '$meta': {'solomon_children_labels': 'code'},
            'waybill_ref_not_found': 1,
            'waybill_not_found': 1,
            'cargo_dispatch_request': 1,
            'delayed': 1,
        },
        'per_planner': {'$meta': {'solomon_children_labels': 'planner_type'}},
    }


@pytest.mark.config(
    UNITED_DISPATCH_PERFORMER_FOR_ORDER_RELEVANCE_TTL={
        'request_irrelevant_after': 30,
    },
)
@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_cargo_dispatch_no_waybill_delayed(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        taxi_united_dispatch_monitor,
        reset_stats,
        mocked_time,
        mockserver,
):
    mocked_time.set(datetime.datetime.now())

    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    order_created_ts = (
        mocked_time.now().replace(tzinfo=datetime.timezone.utc).timestamp()
    )

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id='unknown_waybill', order_created_ts=order_created_ts,
        ),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'delayed'}

    mocked_time.sleep(60)

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id='unknown_waybill', order_created_ts=order_created_ts,
        ),
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'irrelevant'}

    stats = await taxi_united_dispatch_monitor.get_metric('lookup-stats')
    assert stats == {
        'event': {
            '$meta': {'solomon_children_labels': 'code'},
            'waybill_not_found': 1,
            'waybill_ref_not_found': 1,
            'delayed': 1,
            'cargo_dispatch_request': 1,
        },
        'per_planner': {'$meta': {'solomon_children_labels': 'planner_type'}},
    }


@pytest.mark.config(
    UNITED_DISPATCH_PERFORMER_FOR_ORDER_RELEVANCE_TTL={
        'request_irrelevant_after': 30,
    },
)
async def test_performer_found_in_cargo_dispatch(
        create_segment,
        taxi_united_dispatch,
        state_taxi_order_created,
        set_waybill_candidate,
        get_single_waybill,
        taxi_united_dispatch_monitor,
        reset_stats,
        mocked_time,
        mockserver,
        cargo_dispatch,
):
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_created()
    waybill = get_single_waybill()
    set_waybill_candidate(waybill_ref=waybill['id'], performer_id=CANDIDATE_ID)

    order_created_ts = (
        mocked_time.now().replace(tzinfo=datetime.timezone.utc).timestamp()
    )

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/find-ref')
    def _wrapper(request):
        return {'waybill_external_ref': waybill['id']}

    response = await taxi_united_dispatch.post(
        '/performer-for-order',
        json=_make_performer_request(
            taxi_order_id='unknown_order_id',
            order_created_ts=order_created_ts,
        ),
    )

    assert response.status_code == 200
    assert response.json()['candidate']['id'] == CANDIDATE_ID

    stats = await taxi_united_dispatch_monitor.get_metric('lookup-stats')

    assert stats == {
        'per_planner': {
            '$meta': {'solomon_children_labels': 'planner_type'},
            'crutches': {
                '$meta': {'solomon_children_labels': 'state'},
                'successful': {
                    'count': 1,
                    'lag': {
                        '$meta': {'solomon_children_labels': 'percentile'},
                        'p0': matching.any_integer,
                        'p100': matching.any_integer,
                        'p50': matching.any_integer,
                        'p90': matching.any_integer,
                        'p95': matching.any_integer,
                        'p98': matching.any_integer,
                        'p99': matching.any_integer,
                        'p99_6': matching.any_integer,
                        'p99_9': matching.any_integer,
                    },
                },
            },
        },
        'event': {
            '$meta': {'solomon_children_labels': 'code'},
            'cargo_dispatch_request': 1,
        },
    }
