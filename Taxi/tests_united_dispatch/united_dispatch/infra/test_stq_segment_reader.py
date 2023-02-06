async def test_modified_classes(
        state_waybill_proposed, create_segment, propositions_manager,
):
    """
        Check classes taken from modified classes instead of taxi_classes.
    """
    create_segment(
        modified_classes=['eda'], crutches={'force_crutch_builder': True},
    )
    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 1
    assert set(
        propositions_manager.propositions[0]['taxi_order_requirements'][
            'taxi_classes'
        ],
    ) == {'eda'}


async def test_not_need_to_substitute_tariffs(
        state_waybill_proposed, create_segment, propositions_manager,
):
    """
        Check classes taken from modified classes instead of
        tariffs_substitution.
    """
    create_segment(
        modified_classes=['eda'],
        tariffs_substitution=['courer', 'express'],
        crutches={'force_crutch_builder': True},
    )
    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 1
    assert set(
        propositions_manager.propositions[0]['taxi_order_requirements'][
            'taxi_classes'
        ],
    ) == {'eda'}


async def test_tariffs_substitution(
        state_waybill_proposed, create_segment, propositions_manager,
):
    """
        Check classes taken from tariffs_substitution instead of taxi_classes.
    """
    create_segment(
        tariffs_substitution=['courier', 'express'],
        crutches={'force_crutch_builder': True},
    )
    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 1
    assert set(
        propositions_manager.propositions[0]['taxi_order_requirements'][
            'taxi_classes'
        ],
    ) == {'courier', 'express'}


async def test_taxi_requirements(
        state_waybill_proposed, create_segment, propositions_manager,
):
    """
        Check additional requirements passed to proposal.
    """
    create_segment(
        taxi_requirements={'some_property': 'property'},
        crutches={'force_crutch_builder': True},
    )
    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 1
    assert (
        propositions_manager.propositions[0]['taxi_order_requirements'][
            'some_property'
        ]
        == 'property'
    )


async def test_segment_executors_specific_shard(
        create_segment,
        state_segments_replicated,
        list_segment_executors,
        exp_segment_executors_selector,
        exp_planner_shard,
):
    """
        Check specific shard is chosen for segment.
    """
    segment = create_segment()

    await exp_planner_shard(shard='moscow')
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'eats', 'is_active': False},
            {'planner_type': 'delivery', 'is_active': False},
        ],
    )
    await state_segments_replicated()

    segment_executors = list_segment_executors(segment.id)
    assert [e['planner_shard'] for e in segment_executors] == [
        'moscow',
        'moscow',
    ]


async def test_waybill_building_not_awaited(
        create_segment,
        state_segments_replicated,
        get_segment,
        exp_segment_executors_selector,
):
    """
        Check no proposition till waybill_building_awaited is set.
    """
    segment = create_segment(waybill_building_awaited=False)
    await exp_segment_executors_selector()
    await state_segments_replicated()

    pg_segment = get_segment(segment.id)
    assert pg_segment is None  # segment ignored till next journal event


async def test_segment_status_resolved(
        cargo_dispatch,
        create_segment,
        state_segments_replicated,
        get_segment,
        exp_segment_executors_selector,
        list_segment_executors,
        update_segment_executor_record,
        resolution='cancelled_by_user',
):
    """
        Check status is set to resolved for known segment.
    """
    segment = create_segment(crutches={'force_crutch_builder': True})
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'eats', 'is_active': True},
            {'planner_type': 'delivery', 'is_active': False},
        ],
    )
    await state_segments_replicated()

    assert get_segment(segment.id)  # check stored
    assert get_segment(segment.id)['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [
        (e['planner_type'], e['status'], e['execution_order'])
        for e in segment_executors
    ] == [('eats', 'active', 0), ('delivery', 'idle', 1)]

    update_segment_executor_record(
        segment.id, execution_order=0, new_status='idle',
    )
    update_segment_executor_record(
        segment.id, execution_order=1, new_status='active',
    )

    cargo_dispatch.segments.set_resolution(
        segment_id=segment.id, resolution=resolution,
    )
    await state_segments_replicated()

    db_segment = get_segment(segment.id)
    assert db_segment['status'] == 'resolved'

    segment_executors = list_segment_executors(segment.id)
    assert [
        (e['planner_type'], e['status'], e['execution_order'])
        for e in segment_executors
    ] == [('eats', 'finished', 0), ('delivery', 'finished', 1)]


async def test_journal_resolved_segment_first(
        create_segment,
        state_segments_replicated,
        get_segment,
        exp_segment_executors_selector,
        list_segment_executors,
        resolution='cancelled_by_user',
):
    """
        Check terminal status is set for segment even on first event.
    """
    segment = create_segment(resolution=resolution)
    await exp_segment_executors_selector(
        executors=[{'planner_type': 'delivery', 'is_active': True}],
    )
    await state_segments_replicated()

    db_segment = get_segment(segment.id)  # check stored
    assert db_segment['status'] == 'resolved'

    segment_executors = list_segment_executors(segment.id)
    assert [
        (e['planner_type'], e['status'], e['execution_order'])
        for e in segment_executors
    ] == [('delivery', 'finished', 0)]


async def test_waybill_version_increased(
        create_segment,
        state_segments_replicated,
        state_waybill_proposed,
        cargo_dispatch,
        get_segment,
        exp_segment_executors_selector,
):
    """
        Check restart proposition building on waybill_building_version
        increase.
    """
    segment = create_segment(
        waybill_building_version=1, crutches={'force_crutch_builder': True},
    )
    await state_waybill_proposed()

    pg_segment = get_segment(segment.id)
    assert pg_segment['waybill_ref']  # some proposition was set

    cargo_dispatch.segments.inc_waybill_building_version(segment.id)
    await exp_segment_executors_selector()
    await state_segments_replicated()

    pg_segment = get_segment(segment.id, waybill_building_version=2)
    assert pg_segment['waybill_ref'] is None
    assert pg_segment['waybill_building_version'] == 2


async def test_segment_was_already_chosen(
        create_segment,
        state_segments_replicated,
        cargo_dispatch,
        get_segment,
        exp_segment_executors_selector,
        list_segment_executors,
):
    """
        Check segment status for segment with waybill from other router.
    """
    segment = create_segment(waybill_building_version=1)

    await exp_segment_executors_selector(
        executors=[{'planner_type': 'delivery', 'is_active': True}],
    )

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment  # check stored
    assert db_segment['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['active']

    cargo_dispatch.segments.set_proposition(
        segment_id=segment.id,
        external_ref='logistic-dispatch/'
        + '4dd56b19-e8a2-47eb-b5f2-fe1d6eef15fb',
    )

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment['status'] == 'another_router_chosen'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['finished']


async def test_segment_have_this_router(
        create_segment,
        state_segments_replicated,
        cargo_dispatch,
        get_segment,
        exp_segment_executors_selector,
        list_segment_executors,
):
    """
        Check segment status for segment with waybill from other router.
    """
    segment = create_segment(waybill_building_version=1)

    await exp_segment_executors_selector(
        executors=[{'planner_type': 'delivery', 'is_active': True}],
    )

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment  # check stored
    assert db_segment['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['active']

    cargo_dispatch.segments.set_routers(
        segment_id=segment.id,
        routers=[
            {
                'id': 'united-dispatch',
                'source': 'cargo-dispatch-choose-routers',
                'matched_experiment': {
                    'name': 'segment_routers',
                    'clause_index': '20',
                },
                'priority': 1,
                'autoreorder_flow': 'newway',
            },
        ],
    )

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['active']


async def test_segment_have_several_routers(
        create_segment,
        state_segments_replicated,
        cargo_dispatch,
        get_segment,
        exp_segment_executors_selector,
        list_segment_executors,
):
    """
        Check segment status for segment with waybill from other router.
    """
    segment = create_segment(waybill_building_version=1)

    await exp_segment_executors_selector(
        executors=[{'planner_type': 'delivery', 'is_active': True}],
    )

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment  # check stored
    assert db_segment['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['active']

    cargo_dispatch.segments.set_routers(
        segment_id=segment.id,
        routers=[
            {
                'id': 'united-dispatch',
                'source': 'cargo-dispatch-choose-routers',
                'matched_experiment': {
                    'name': 'segment_routers',
                    'clause_index': '20',
                },
                'priority': 1,
                'autoreorder_flow': 'newway',
            },
            {
                'id': 'fallback_router',
                'source': 'cargo-dispatch-choose-routers',
                'matched_experiment': {
                    'name': 'segment_routers',
                    'clause_index': '20',
                },
                'priority': 1,
                'autoreorder_flow': 'newway',
            },
        ],
    )

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['active']


async def test_segment_have_unknown_routers(
        create_segment,
        state_segments_replicated,
        cargo_dispatch,
        get_segment,
        exp_segment_executors_selector,
        list_segment_executors,
):
    """
        Check segment status for segment with waybill from other router.
    """
    segment = create_segment(waybill_building_version=1)

    await exp_segment_executors_selector(
        executors=[{'planner_type': 'delivery', 'is_active': True}],
    )

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment  # check stored
    assert db_segment['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['active']

    cargo_dispatch.segments.set_routers(segment_id=segment.id, routers=None)

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['active']


async def test_segment_have_other_routers(
        create_segment,
        state_segments_replicated,
        cargo_dispatch,
        get_segment,
        exp_segment_executors_selector,
        list_segment_executors,
):
    """
        Check segment status for segment with waybill from other router.
    """
    segment = create_segment(waybill_building_version=1)

    await exp_segment_executors_selector(
        executors=[{'planner_type': 'delivery', 'is_active': True}],
    )

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment  # check stored
    assert db_segment['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['active']

    cargo_dispatch.segments.set_routers(
        segment_id=segment.id,
        routers=[
            {
                'id': 'fallback_router',
                'source': 'cargo-dispatch-choose-routers',
                'matched_experiment': {
                    'name': 'segment_routers',
                    'clause_index': '20',
                },
                'priority': 1,
                'autoreorder_flow': 'newway',
            },
        ],
    )

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment['status'] == 'another_router_chosen'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['finished']


async def test_segment_have_no_routers(
        create_segment,
        state_segments_replicated,
        cargo_dispatch,
        get_segment,
        exp_segment_executors_selector,
        list_segment_executors,
):
    """
        Check segment status for segment with waybill from other router.
    """
    segment = create_segment(waybill_building_version=1)

    await exp_segment_executors_selector(
        executors=[{'planner_type': 'delivery', 'is_active': True}],
    )

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment  # check stored
    assert db_segment['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['active']

    cargo_dispatch.segments.set_routers(segment_id=segment.id, routers=[])

    await state_segments_replicated()

    db_segment = get_segment(segment.id, waybill_building_version=1)
    assert db_segment['status'] == 'another_router_chosen'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['finished']


async def test_segment_status_after_waybill_version_increase(
        create_segment,
        state_segments_replicated,
        cargo_dispatch,
        get_segment,
        exp_segment_executors_selector,
        list_segment_executors,
):
    """
        Check segment status on waybill_building_version
        increase.
    """
    segment = create_segment(waybill_building_version=1)
    cargo_dispatch.segments.set_proposition(
        segment_id=segment.id,
        external_ref='logistic-dispatch/'
        + '4dd56b19-e8a2-47eb-b5f2-fe1d6eef15fb',
    )

    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'eats', 'is_active': True},
            {'planner_type': 'delivery', 'is_active': False},
        ],
    )

    await state_segments_replicated()

    pg_segment = get_segment(segment.id)
    assert pg_segment['status'] == 'another_router_chosen'

    segment_executors = list_segment_executors(segment.id)
    assert [(e['planner_type'], e['status']) for e in segment_executors] == [
        ('eats', 'finished'),
        ('delivery', 'finished'),
    ]

    cargo_dispatch.segments.inc_waybill_building_version(segment.id)
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'fallback', 'is_active': True},
            {'planner_type': 'eats', 'is_active': False},
            {'planner_type': 'grocery', 'is_active': False},
        ],
    )
    await state_segments_replicated()

    pg_segment = get_segment(segment.id, waybill_building_version=2)
    assert pg_segment['waybill_ref'] is None
    assert pg_segment['waybill_building_version'] == 2
    assert pg_segment['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [(e['planner_type'], e['status']) for e in segment_executors] == [
        ('eats', 'active'),
        ('delivery', 'idle'),
    ]


async def test_segment_status_after_double_read(
        create_segment,
        state_waybill_proposed,
        state_segments_replicated,
        cargo_dispatch,
        get_segment,
        exp_segment_executors_selector,
        list_segment_executors,
):
    """
        Check segment status is not changed after double read
        increase.
    """
    await exp_segment_executors_selector(
        executors=[{'planner_type': 'crutches', 'is_active': True}],
    )

    segment = create_segment(
        waybill_building_version=1, crutches={'force_crutch_builder': True},
    )
    await state_waybill_proposed()

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['finished']

    pg_segment = get_segment(segment.id)
    assert pg_segment['status'] == 'executing'

    cargo_dispatch.segments.inc_revision(segment.id)
    await state_segments_replicated()

    pg_segment = get_segment(segment.id, waybill_building_version=1)
    assert pg_segment['waybill_ref']
    assert pg_segment['waybill_building_version'] == 1
    assert pg_segment['status'] == 'executing'

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['finished']


async def test_finish_segment_chosed_by_other_router(
        create_segment,
        state_segments_replicated,
        cargo_dispatch,
        get_segment,
        exp_segment_executors_selector,
        list_segment_executors,
):
    """
        Check segment status is resolved after finishing
        segment, chosed by another router
    """
    segment = create_segment(
        waybill_building_version=1, crutches={'force_crutch_builder': True},
    )
    cargo_dispatch.segments.set_proposition(
        segment_id=segment.id,
        external_ref='logistic-dispatch/'
        + '4dd56b19-e8a2-47eb-b5f2-fe1d6eef15fb',
    )

    await exp_segment_executors_selector(
        executors=[{'planner_type': 'delivery', 'is_active': True}],
    )

    await state_segments_replicated()

    assert (
        get_segment(segment.id, waybill_building_version=1)['status']
        == 'another_router_chosen'
    )

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['finished']

    cargo_dispatch.segments.set_resolution(
        segment_id=segment.id, resolution='resolved',
    )
    await state_segments_replicated()

    assert (
        get_segment(segment.id, waybill_building_version=1)['status']
        == 'resolved'
    )

    segment_executors = list_segment_executors(segment.id)
    assert [e['status'] for e in segment_executors] == ['finished']


async def test_cargo_claims_external_order_id_passed(
        create_segment,
        state_segments_replicated,
        get_segment,
        exp_segment_executors_selector,
):
    """
        Check external_order_id passed from cargo-dispatch API
    """
    segment = create_segment(crutches={'force_crutch_builder': True})

    await exp_segment_executors_selector()

    await state_segments_replicated()

    segment = get_segment(segment.id)
    external_order_ids = [
        p.get('external_order_id')
        for p in segment['segment_info']['segment']['points']
    ]
    assert external_order_ids == ['1234-5678', None, '1234-5678']
