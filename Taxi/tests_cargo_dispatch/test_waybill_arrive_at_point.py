# pylint: disable=W0102

import datetime

import pytest

from testsuite.utils import matching


@pytest.fixture(name='dispatch_arrive_at_point')
def _dispatch_arrive_at_point(
        taxi_cargo_dispatch, get_point_execution_by_visit_order,
):
    async def _wrapper(
            waybill_external_ref: str, visit_order: int = 1, support=None,
    ):
        point = await get_point_execution_by_visit_order(
            waybill_ref=waybill_external_ref, visit_order=visit_order,
        )

        request_body = {
            'last_known_status': 'new',
            'idempotency_token': '123456',
            'point_id': point['claim_point_id'],
            'performer_info': {'driver_id': '789', 'park_id': 'park_id_1'},
        }

        if support:
            request_body['support'] = support

        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/arrive-at-point',
            params={'waybill_external_ref': waybill_external_ref},
            json=request_body,
            headers={'Accept-Language': 'ru', 'X-Remote-Ip': '0.0.0.0'},
        )
        return response

    return _wrapper


async def test_happy_path(
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        stq,
):
    mock_claims_arrive_at_point()
    response = await dispatch_arrive_at_point('waybill_fb_3')
    assert response.status_code == 200

    response_body = response.json()
    assert response_body['new_status'] == 'pickup_confirmation'
    assert 'waybill_info' in response_body

    assert not stq.cargo_waybill_auto_confirm_exchange.times_called


async def test_conflict(
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        mockserver,
):
    mock_claims_arrive_at_point(
        response=mockserver.make_response(
            status=409,
            json={'code': 'state_mismatch', 'message': 'initation conflict'},
        ),
    )
    response = await dispatch_arrive_at_point('waybill_fb_3')
    assert response.status_code == 409


async def test_send_driver(
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    mock_claims_arrive_at_point(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'last_known_status': 'new',
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_arrive_at_point(waybill_ref)
    assert response.status_code == 200


async def test_wrong_point_id(
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
):
    """
    Previous point was not resolved yet
    """
    mock_claims_arrive_at_point()
    response = await dispatch_arrive_at_point('waybill_fb_3', visit_order=2)
    assert response.status_code == 409


async def test_batch_order(
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_smart_1',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    mock_claims_arrive_at_point(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_arrive_at_point(waybill_ref)
    assert response.status_code == 200


@pytest.mark.now('2020-10-10T10:00:00+00:00')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_auto_confirm_exchange_settings',
    consumers=['cargo-dispatch/auto-confirm-exchange'],
    clauses=[],
    default_value={
        'enabled': True,
        'settings': {
            'delay_seconds': 120,
            'ticket': 'SUPPORT-1',
            'comment': 'Autocomplete',
        },
    },
)
@pytest.mark.parametrize(
    'custom_context',
    [
        # If delay_after_promise_seconds is not specified in experiment,
        # then delay_seconds must be used regardless of custom_context.
        pytest.param(None),
        pytest.param({'place_id': '123', 'region_id': 345}),
        pytest.param({'promise_max_at': '2020-10-10T09:00:00+00:00'}),
        pytest.param({'promise_max_at': '2020-10-10T11:00:00+00:00'}),
    ],
)
async def test_autocomplete(
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        stq,
        custom_context,
        experiments3,
):
    exp3_recorder = experiments3.record_match_tries(
        'cargo_auto_confirm_exchange_settings',
    )

    # Prepare waybill
    seg_3 = happy_path_claims_segment_db.get_segment('seg3')
    seg_3.json['custom_context'] = custom_context

    mock_claims_exchange_confirm()
    response = await dispatch_confirm_point('waybill_fb_3', visit_order=1)
    assert response.status_code == 200

    mock_claims_arrive_at_point()
    response = await dispatch_arrive_at_point('waybill_fb_3', visit_order=2)
    assert response.status_code == 200

    point = await get_point_execution_by_visit_order(
        waybill_ref='waybill_fb_3', visit_order=2,
    )

    assert stq.cargo_waybill_auto_confirm_exchange.times_called == 1
    stq_call = stq.cargo_waybill_auto_confirm_exchange.next_call()
    assert stq_call['id'] == 'point_{}_waybill_ref_waybill_fb_3'.format(
        point['claim_point_id'],
    )
    assert stq_call['kwargs']['claim_point_id'] == point['claim_point_id']
    assert stq_call['kwargs']['waybill_ref'] == 'waybill_fb_3'
    assert stq_call['kwargs']['ticket'] == 'SUPPORT-1'
    assert stq_call['kwargs']['comment'] == 'Autocomplete'
    # now + delay_seconds
    assert stq_call['eta'] == datetime.datetime(2020, 10, 10, 10, 2, 0)

    if custom_context and custom_context.get('region_id', None):
        match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
        assert match_tries[0].kwargs['region_id'] == 345


@pytest.mark.now('2020-10-10T10:00:00+00:00')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_auto_confirm_exchange_settings',
    consumers=['cargo-dispatch/auto-confirm-exchange'],
    clauses=[],
    default_value={
        'enabled': True,
        'settings': {
            'delay_seconds': 120,
            'delay_after_promise_seconds': 60,
            'ticket': 'SUPPORT-1',
            'comment': 'Autocomplete',
        },
    },
)
@pytest.mark.parametrize(
    'custom_context,expected_eta',
    [
        # custom_context is not found.
        # Fallback to delay_seconds.
        pytest.param(None, datetime.datetime(2020, 10, 10, 10, 2, 0)),
        # promise_max_at is not found.
        # Fallback to delay_seconds.
        pytest.param(
            {'place_id': '123'}, datetime.datetime(2020, 10, 10, 10, 2, 0),
        ),
        # now + delay_seconds is later than
        # promise_time + delay_after_promise_seconds. Use delay_seconds.
        pytest.param(
            {'promise_max_at': '2020-10-10T10:00:59+00:00'},
            datetime.datetime(2020, 10, 10, 10, 2, 0),
        ),
        # promise_time + delay_after_promise_seconds is later than
        # now + delay_seconds. Use delay_after_promise_seconds.
        pytest.param(
            {'promise_max_at': '2020-10-10T10:01:01+00:00'},
            datetime.datetime(2020, 10, 10, 10, 2, 1),
        ),
    ],
)
async def test_autocomplete_after_promise(
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        stq,
        custom_context,
        expected_eta,
):
    # Prepare waybill
    seg_3 = happy_path_claims_segment_db.get_segment('seg3')
    seg_3.json['custom_context'] = custom_context

    mock_claims_exchange_confirm()
    response = await dispatch_confirm_point('waybill_fb_3', visit_order=1)
    assert response.status_code == 200

    mock_claims_arrive_at_point()
    response = await dispatch_arrive_at_point('waybill_fb_3', visit_order=2)
    assert response.status_code == 200

    point = await get_point_execution_by_visit_order(
        waybill_ref='waybill_fb_3', visit_order=2,
    )

    assert stq.cargo_waybill_auto_confirm_exchange.times_called == 1
    stq_call = stq.cargo_waybill_auto_confirm_exchange.next_call()
    assert stq_call['id'] == 'point_{}_waybill_ref_waybill_fb_3'.format(
        point['claim_point_id'],
    )
    assert stq_call['kwargs']['claim_point_id'] == point['claim_point_id']
    assert stq_call['kwargs']['waybill_ref'] == 'waybill_fb_3'
    assert stq_call['kwargs']['ticket'] == 'SUPPORT-1'
    assert stq_call['kwargs']['comment'] == 'Autocomplete'
    assert stq_call['eta'] == expected_eta


@pytest.mark.config(
    CARGO_DISPATCH_PULL_DISPATCH_FILTERS={
        'enabled': True,
        'filters': {'__default__': False, 'auto_close': True},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_auto_confirm_exchange_settings',
    consumers=['cargo-dispatch/auto-confirm-exchange'],
    clauses=[],
    default_value={
        'enabled': True,
        'settings': {
            'delay_seconds': 100,
            'ticket': 'SUPPORT-1',
            'comment': 'Autocomplete',
        },
    },
)
async def test_autocomplete_pull_dispatch(
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        stq,
):

    waybill_ref = 'waybill_smart_1'
    # Prepare segments
    seg_1 = happy_path_claims_segment_db.get_segment('seg1')
    seg_1.json['custom_context'] = {'dispatch_type': 'pull-dispatch'}
    seg_1.set_point_visit_status('p1', 'visited')
    seg_1.set_point_visit_status('p2', 'visited')
    seg_1.set_point_visit_status('p3', 'visited')
    seg_1.set_point_visit_status('p4', 'visited')

    seg_2 = happy_path_claims_segment_db.get_segment('seg2')
    seg_2.json['custom_context'] = {'dispatch_type': 'pull-dispatch'}
    seg_2.set_point_visit_status('p1', 'visited')

    mock_claims_arrive_at_point()
    response = await dispatch_arrive_at_point(waybill_ref, visit_order=6)
    assert response.status_code == 200

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=6,
    )

    assert stq.cargo_waybill_auto_confirm_exchange.times_called == 1
    stq_call = stq.cargo_waybill_auto_confirm_exchange.next_call()
    assert stq_call['id'] == 'point_{}_waybill_ref_{}'.format(
        point['claim_point_id'], waybill_ref,
    )
    assert stq_call['kwargs']['claim_point_id'] == point['claim_point_id']
    assert stq_call['kwargs']['waybill_ref'] == waybill_ref
    assert stq_call['kwargs']['ticket'] == 'SUPPORT-1'
    assert stq_call['kwargs']['comment'] == 'Autocomplete'


@pytest.mark.config(
    CARGO_DISPATCH_PULL_DISPATCH_FILTERS={
        'enabled': True,
        'filters': {
            '__default__': False,
            'auto_close': True,
            'has_parcel': True,
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_auto_confirm_exchange_settings',
    consumers=['cargo-dispatch/auto-confirm-exchange'],
    clauses=[],
    default_value={
        'enabled': True,
        'settings': {
            'delay_seconds': 100,
            'ticket': 'SUPPORT-1',
            'comment': 'Autocomplete',
        },
    },
)
async def test_autocomplete_has_parcel(
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        stq,
):
    waybill_ref = 'waybill_smart_1'
    # Prepare segments
    seg_1 = happy_path_claims_segment_db.get_segment('seg1')
    seg_1.json['custom_context'] = {
        'dispatch_type': 'pull-dispatch',
        'lavka_has_market_parcel': True,
    }
    seg_1.set_point_visit_status('p1', 'visited')
    seg_1.set_point_visit_status('p2', 'visited')
    seg_1.set_point_visit_status('p3', 'visited')
    seg_1.set_point_visit_status('p4', 'visited')

    seg_2 = happy_path_claims_segment_db.get_segment('seg2')
    seg_2.json['custom_context'] = {'dispatch_type': 'pull-dispatch'}
    seg_2.set_point_visit_status('p1', 'visited')

    mock_claims_arrive_at_point()
    response = await dispatch_arrive_at_point(waybill_ref, visit_order=6)
    assert response.status_code == 200

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=6,
    )

    assert stq.cargo_waybill_auto_confirm_exchange.times_called == 1
    stq_call = stq.cargo_waybill_auto_confirm_exchange.next_call()
    assert stq_call['id'] == 'point_{}_waybill_ref_{}'.format(
        point['claim_point_id'], waybill_ref,
    )
    assert stq_call['kwargs']['claim_point_id'] == point['claim_point_id']
    assert stq_call['kwargs']['waybill_ref'] == waybill_ref
    assert stq_call['kwargs']['ticket'] == 'SUPPORT-1'
    assert stq_call['kwargs']['comment'] == 'Autocomplete'


@pytest.mark.config(
    CARGO_DISPATCH_PULL_DISPATCH_FILTERS={
        'enabled': True,
        'filters': {
            '__default__': False,
            'auto_close': True,
            'has_parcel': True,
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_auto_confirm_exchange_settings',
    consumers=['cargo-dispatch/auto-confirm-exchange'],
    clauses=[],
    default_value={
        'enabled': True,
        'settings': {
            'delay_seconds': 100,
            'ticket': 'SUPPORT-1',
            'comment': 'Autocomplete',
        },
    },
)
async def test_autocomplete_no_market_parcel(
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        mock_claims_exchange_confirm,
        dispatch_confirm_point,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        stq,
):
    waybill_ref = 'waybill_smart_1'
    # Prepare segments
    seg_1 = happy_path_claims_segment_db.get_segment('seg1')
    seg_1.json['custom_context'] = {'dispatch_type': 'pull-dispatch'}
    seg_1.set_point_visit_status('p1', 'visited')
    seg_1.set_point_visit_status('p2', 'visited')
    seg_1.set_point_visit_status('p3', 'visited')
    seg_1.set_point_visit_status('p4', 'visited')

    seg_2 = happy_path_claims_segment_db.get_segment('seg2')
    seg_2.json['custom_context'] = {'dispatch_type': 'pull-dispatch'}
    seg_2.set_point_visit_status('p1', 'visited')

    mock_claims_arrive_at_point()
    response = await dispatch_arrive_at_point(waybill_ref, visit_order=6)
    assert response.status_code == 200


class _RemoveIfMatched:
    """Matches any string."""

    def __init__(self, items: list):
        self.items = items

    def __repr__(self):
        return '<_RemoveIfMatched>' + str(self.items)

    def __eq__(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        return False


@pytest.mark.parametrize(
    'mark_identical_source_points_as_arrived', [False, True],
)
async def test_batch_order_multiple_pickups_at_same_place_id(
        taxi_cargo_dispatch,
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        get_point_execution_by_visit_order,
        happy_path_claims_segment_db,
        experiments3,
        mark_identical_source_points_as_arrived,
        waybill_ref='waybill_smart_1',
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_dispatch_waybill_arrived_at_point_settings',
        consumers=['cargo-dispatch/waybill-arrived-at-point-settings'],
        clauses=[],
        default_value={
            'mark_identical_source_points_as_arrived': (
                mark_identical_source_points_as_arrived
            ),
        },
    )
    await taxi_cargo_dispatch.invalidate_caches()

    custom_context = {'place_id': 11534}
    point_ids = []
    for segment_id in ['seg1', 'seg2']:
        segment = happy_path_claims_segment_db.get_segment(segment_id)
        segment.json['custom_context'].update(custom_context)
        for point in segment.json['points']:
            if point['segment_point_type'] == 'source':
                point_ids.append(point['claim_point_id'])

    handler = mock_claims_arrive_at_point(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'point_id': _RemoveIfMatched(point_ids),
        },
    )
    response = await dispatch_arrive_at_point(waybill_ref)

    assert response.status_code == 200
    assert handler.has_calls
    if mark_identical_source_points_as_arrived:
        assert handler.times_called == 3
        assert not point_ids
    else:
        assert handler.times_called == 1
        assert len(point_ids) == 2


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_dispatch_waybill_arrived_at_point_settings',
    consumers=['cargo-dispatch/waybill-arrived-at-point-settings'],
    clauses=[],
    default_value={'mark_identical_source_points_as_arrived': True},
)
@pytest.mark.parametrize(
    [
        'corp_client_ids_list',
        'coordinates_list',
        'are_identical_points_marked',
    ],
    [
        pytest.param(
            [None, None], [[1, 2], [2, 3]], False, id='Distant coordinates',
        ),
        pytest.param(
            ['corp_client_id_56789012345678912', None],
            [[1, 2], [2, 3]],
            False,
            id='Different corp_client_ids',
        ),
        pytest.param(
            [
                'corp_client_id_56789012345678912',
                'corp_client_id_56789012345678912',
            ],
            [[1, 2], [1, 2]],
            True,
            id='Same corp_client_ids and source coordinates',
        ),
        pytest.param(
            [None, None],
            [[1, 2], [1, 2]],
            True,
            id='Two c2c segments with same source coordinates',
        ),
    ],
)
async def test_mark_same_source_points_arrived(
        dispatch_arrive_at_point,
        happy_path_claims_segment_db,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        corp_client_ids_list,
        coordinates_list,
        are_identical_points_marked,
        waybill_ref='waybill_smart_1',
):
    for i, segment_id in enumerate(['seg1', 'seg2']):
        segment = happy_path_claims_segment_db.get_segment(segment_id)

        if corp_client_ids_list is not None:
            segment.json['corp_client_id'] = corp_client_ids_list[i]

        segment.set_point_coordinates('p1', coordinates_list[i])

    handler = mock_claims_arrive_at_point(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'point_id': matching.any_integer,
        },
    )
    response = await dispatch_arrive_at_point(waybill_ref)
    assert response.status_code == 200

    expected_times_called = 2 if are_identical_points_marked else 1
    assert handler.times_called == expected_times_called


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_dispatch_waybill_arrived_at_point_settings',
    consumers=['cargo-dispatch/waybill-arrived-at-point-settings'],
    clauses=[],
    default_value={
        'mark_identical_source_points_as_arrived': False,
        'mark_identical_return_points_as_arrived': True,
    },
)
async def test_mark_same_return_points_arrived(
        dispatch_arrive_at_point,
        happy_path_claims_segment_db,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        waybill_ref='waybill_smart_1',
        corp_client_id='corp_client_id_56789012345678912',
        coordinates=[1, 2],
):
    points = [
        ('seg1', 'p1', 'visited'),
        ('seg1', 'p2', 'visited'),
        ('seg1', 'p3', 'skipped'),
        ('seg1', 'p4', 'skipped'),
        ('seg1', 'p5', 'skipped'),
        ('seg2', 'p1', 'visited'),
        ('seg2', 'p2', 'skipped'),
    ]
    for (segment_id, point_id, point_status) in points:
        happy_path_claims_segment_db.set_segment_point_visit_status(
            segment_id, point_id, point_status, is_caused_by_user=True,
        )
    for (segment_id, point_id) in [('seg1', 'p6'), ('seg2', 'p3')]:
        happy_path_claims_segment_db.get_segment(
            segment_id,
        ).set_point_coordinates(point_id, coordinates)

    handler = mock_claims_arrive_at_point(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'point_id': matching.any_integer,
        },
    )
    response = await dispatch_arrive_at_point(waybill_ref, visit_order=8)
    assert response.status_code == 200
    assert handler.times_called == 2


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_patch_setcar_version_settings',
    consumers=['cargo/patch-setcar-version-settings'],
    clauses=[],
    default_value={
        'update_on_performer_found': False,
        'update_on_arrive_at_point_with_support': True,
    },
)
@pytest.mark.parametrize('with_support', [False, True])
async def test_update_setcar_state_version(
        with_support,
        dispatch_arrive_at_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        stq,
):
    support = None
    if with_support:
        support = {'ticket': 'TICKET-123', 'comment': 'some comment'}

    mock_claims_arrive_at_point()
    response = await dispatch_arrive_at_point('waybill_fb_3', 1, support)
    assert response.status_code == 200

    response_body = response.json()
    assert response_body['new_status'] == 'pickup_confirmation'
    assert 'waybill_info' in response_body

    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called
        == with_support
    )
    if with_support:
        stq_call = (
            stq.cargo_increment_and_update_setcar_state_version.next_call()
        )
        assert stq_call['kwargs'] == {
            'cargo_order_id': matching.AnyString(),
            'driver_profile_id': '789',
            'park_id': 'park_id_1',
            'log_extra': {'_link': matching.AnyString()},
        }
