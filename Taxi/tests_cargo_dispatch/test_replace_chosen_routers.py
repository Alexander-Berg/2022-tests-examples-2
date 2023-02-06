import pytest

from testsuite.utils import matching


@pytest.fixture(name='set_up_replace_chosen_routers_exp')
async def _set_up_replace_chosen_routers_exp(
        taxi_cargo_dispatch, experiments3,
):
    async def wrapper(
            affected_segment_id: str,
            replaced_segment_routers: list,
            new_segment_routers: list,
    ):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_dispatch_replace_chosen_routers',
            consumers=['cargo-dispatch/route_building_init'],
            clauses=[
                {
                    'title': 'Clause #0',
                    'predicate': {
                        'init': {
                            'predicates': [
                                {
                                    'init': {
                                        'arg_name': 'segment_id',
                                        'set': [affected_segment_id],
                                        'set_elem_type': 'string',
                                    },
                                    'type': 'in_set',
                                },
                            ],
                        },
                        'type': 'all_of',
                    },
                    'value': {
                        'replaced_segment_routers': replaced_segment_routers,
                        'new_segment_routers': new_segment_routers,
                    },
                },
            ],
            default_value={
                'replaced_segment_routers': [],
                'new_segment_routers': [],
            },
        )
        await taxi_cargo_dispatch.invalidate_caches()

    return wrapper


async def test_replacing_router(
        happy_path_state_routers_chosen,
        run_choose_routers,
        get_admin_segment_info,
        get_segment_info,
        experiments3,
        run_replace_chosen_routers,
        set_up_replace_chosen_routers_exp,
        segment_id='seg1',
        best_router_id='smart_router',
        new_router_id='super_router',
        new_router_priority=2,
        new_router_autoreorder_flow='newway',
):
    seginfo = await get_segment_info(segment_id)
    assert seginfo['dispatch']['best_router_id'] == best_router_id

    await set_up_replace_chosen_routers_exp(
        affected_segment_id=segment_id,
        replaced_segment_routers=[best_router_id],
        new_segment_routers=[
            {
                'router_id': new_router_id,
                'priority': new_router_priority,
                'autoreorder_flow': new_router_autoreorder_flow,
            },
        ],
    )

    result = await run_replace_chosen_routers()
    assert result == {
        'replaced-routers-count': 1,
        'new-routers-count': 1,
        'updated-segments-count': 1,
        'failed-segments-count': 0,
    }

    admin_seginfo = await get_admin_segment_info(segment_id)
    assert admin_seginfo['dispatch']['admin_extra']['routers'] == [
        {
            'autoreorder_flow': 'newway',
            'id': 'super_router',
            'is_deleted': False,
            'matched_experiment': {
                'clause_index': '0',
                'name': 'cargo_dispatch_replace_chosen_routers',
            },
            'priority': 2,
            'source': 'cargo-dispatch-replace-chosen-routers',
        },
        {
            'autoreorder_flow': 'newway',
            'id': 'smart_router',
            'is_deleted': True,
            'matched_experiment': {
                'clause_index': '0',
                'name': 'segment_routers',
            },
            'priority': 10,
            'source': 'cargo-dispatch-choose-routers',
        },
        {
            'autoreorder_flow': 'newway',
            'id': 'fallback_router',
            'is_deleted': False,
            'matched_experiment': {
                'clause_index': '0',
                'name': 'segment_routers',
            },
            'priority': 100,
            'source': 'cargo-dispatch-choose-routers',
        },
    ]

    seginfo = await get_segment_info(segment_id)
    assert seginfo['dispatch']['best_router_id'] == new_router_id
    assert seginfo['dispatch']['routers'] == [
        {
            'id': new_router_id,
            'is_deleted': False,
            'source': matching.AnyString(),
            'priority': new_router_priority,
            'autoreorder_flow': new_router_autoreorder_flow,
        },
        {
            'autoreorder_flow': 'newway',
            'is_deleted': False,
            'id': 'fallback_router',
            'priority': 100,
            'source': 'cargo-dispatch-choose-routers:segment_routers:0',
        },
    ]


async def test_segment_with_all_replaced_routers_becomes_resolved(
        happy_path_state_routers_chosen,
        mock_claim_bulk_update_state,
        taxi_cargo_dispatch_monitor,
        taxi_cargo_dispatch,
        run_choose_routers,
        run_notify_claims,
        get_segment_info,
        experiments3,
        run_replace_chosen_routers,
        set_up_replace_chosen_routers_exp,
        segment_id='seg1',
):
    await set_up_replace_chosen_routers_exp(
        affected_segment_id=segment_id,
        replaced_segment_routers=['smart_router', 'fallback_router'],
        new_segment_routers=[],
    )

    result = await run_replace_chosen_routers()
    assert result == {
        'replaced-routers-count': 2,
        'new-routers-count': 0,
        'updated-segments-count': 0,
        'failed-segments-count': 1,
    }

    seginfo = await get_segment_info(segment_id)
    assert seginfo['dispatch']['status'] == 'resolved'

    # claim should be notifyed
    await run_notify_claims()
    stats = await taxi_cargo_dispatch_monitor.get_metric(
        'cargo-dispatch-notify-claims',
    )
    assert stats['stats']['segments-notified-count'] == 1

    assert mock_claim_bulk_update_state.handler.times_called == 1


@pytest.mark.parametrize(
    'replaced_routers',
    [
        pytest.param(['smart_router'], id='Remove single router'),
        pytest.param(
            ['smart_router', 'fallback_router'], id='Remove all routers',
        ),
    ],
)
async def test_proposing_waybill_from_replaced_router(
        happy_path_state_routers_chosen,
        mock_claim_bulk_update_state,
        request_waybill_propose,
        waybill_from_segments,
        experiments3,
        run_replace_chosen_routers,
        set_up_replace_chosen_routers_exp,
        replaced_routers: list,
        segment_id='seg1',
        smart_router='smart_router',
):
    await set_up_replace_chosen_routers_exp(
        affected_segment_id=segment_id,
        replaced_segment_routers=replaced_routers,
        new_segment_routers=[],
    )

    await run_replace_chosen_routers()

    waybill = await waybill_from_segments(
        smart_router, 'waybill_smart_1', segment_id,
    )
    response = await request_waybill_propose(waybill)
    assert response.status_code == 400
    assert response.json()['code'] == 'nonexistent_segment'


async def test_adding_new_router_updates_journal(
        happy_path_state_routers_chosen,
        mock_claim_bulk_update_state,
        run_segments_journal_mover,
        read_segment_journal,
        experiments3,
        run_replace_chosen_routers,
        set_up_replace_chosen_routers_exp,
        segment_id='seg1',
        replaced_router_id='smart_router',
        new_router_id='super_router',
        new_router_priority=2,
        new_router_autoreorder_flow='newway',
):
    await run_segments_journal_mover()
    response = await read_segment_journal(new_router_id)
    assert response['events'] == []

    await set_up_replace_chosen_routers_exp(
        affected_segment_id=segment_id,
        replaced_segment_routers=[replaced_router_id],
        new_segment_routers=[
            {
                'router_id': new_router_id,
                'priority': new_router_priority,
                'autoreorder_flow': new_router_autoreorder_flow,
            },
        ],
    )

    result = await run_replace_chosen_routers()
    assert result == {
        'replaced-routers-count': 1,
        'new-routers-count': 1,
        'updated-segments-count': 1,
        'failed-segments-count': 0,
    }

    await run_segments_journal_mover()
    response = await read_segment_journal(new_router_id)
    assert len(response['events']) == 1
