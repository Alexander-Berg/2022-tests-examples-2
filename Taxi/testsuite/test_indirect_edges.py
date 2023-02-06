import pytest


@pytest.fixture
async def base_test_run(
        run_watchers,
        rt_robot_execute,
        testpoint,
        create_segment,
        create_candidate,
        dummy_router,
        expected_whitelist,
        expected_direct_edges,
        expected_filtered_edges,
):
    """
    Here we have to move the test body into a separate fixture because taxi config is defined in @pytest.mark.config
     (config invalidation is not supported in LD client yet)
    """

    async def runner():
        def get_edges_from_response(edges):
            return [(e['segment_id'], e['contractor_id']) for e in edges]

        @testpoint('ld::p2p::indirect_edges_employer_class_whitelist')
        def indirect_edges_employer_class_whitelist(data):
            assert sorted(expected_whitelist) == sorted(data['whitelist'])

        @testpoint('ld::p2p::direct_edges')
        def direct_edges(data):
            assert 'direct_edges' in data
            assert sorted(expected_direct_edges) == sorted(
                get_edges_from_response(data['direct_edges']),
            )

        @testpoint('ld::p2p::filtered_by_direct_edges')
        def filtered_by_direct_edges(data):
            assert 'edges_filtered_by_direct_edges' in data
            assert sorted(expected_filtered_edges) == sorted(
                get_edges_from_response(
                    data['edges_filtered_by_direct_edges'],
                ),
            )

        @testpoint('test_indirect_edges::restore_edges')
        def restore_edges(data):
            # send a signal to the service
            return {}

        segment_default_courier = create_segment(
            segment_id='segment_default_courier',
            additional_taxi_requirements={'taxi_classes': ['courier']},
        )
        segment_default_express = create_segment(
            segment_id='segment_default_express',
            additional_taxi_requirements={'taxi_classes': ['express']},
        )

        # taxi classes for segment_eats and segment_food_retail are not realistic (in practice, 'eda'+'courier'+'express' are used)
        # they are chosen for testing purposes
        segment_eats = create_segment(
            segment_id='segment_eats',
            employer='eats',
            additional_taxi_requirements={'taxi_classes': ['eda', 'courier']},
        )
        segment_food_retail = create_segment(
            segment_id='segment_food_retail',
            employer='food_retail',
            additional_taxi_requirements={
                'taxi_classes': ['express'],
            },  # will be assigned to 'eda_3' and 'express_2'
        )

        candidate_courier = create_candidate(
            dbid_uuid='courier_1',
            tariff_classes=['courier'],
            position=[55, 37],
        )

        candidate_express = create_candidate(
            dbid_uuid='express_2',
            tariff_classes=['express'],
            position=[55, 37],
        )
        candidate_eats = create_candidate(
            dbid_uuid='eda_3', tariff_classes=['eda'], position=[55, 37],
        )
        await rt_robot_execute('segments_journal')
        await rt_robot_execute('p2p_allocation')

        # assert transfer_context_preparation_candidates.times_called
        assert indirect_edges_employer_class_whitelist.times_called
        assert direct_edges.times_called
        assert filtered_by_direct_edges.times_called
        assert restore_edges.times_called

    return runner


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'planner.ban_indirect_edges.enabled': 'false',
    },
)
@pytest.mark.parametrize(
    'expected_whitelist,expected_direct_edges,expected_filtered_edges',
    [([], [], [])],
)
async def test_no_ban(base_test_run):
    await base_test_run()


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'planner.ban_indirect_edges.enabled': 'true',
        'planner.ban_indirect_edges.employer_class_whitelist': (
            'eats:eda,food_retail:eda,some_unknown_employer:some_unknown_class'
        ),
    },
)
@pytest.mark.parametrize(
    'expected_whitelist,expected_direct_edges,expected_filtered_edges',
    [
        (
            [
                ['eats', 'eda'],
                ['food_retail', 'eda'],
                ['some_unknown_employer', 'some_unknown_class'],
            ],
            [
                ('segment_default_courier', 'courier_1'),
                ('segment_default_express', 'express_2'),
                ('segment_eats', 'courier_1'),
                ('segment_eats', 'eda_3'),
                ('segment_food_retail', 'express_2'),
            ],
            [
                ('segment_default_courier', 'express_2'),
                ('segment_default_courier', 'eda_3'),
                ('segment_default_express', 'courier_1'),
                ('segment_default_express', 'eda_3'),
                ('segment_eats', 'express_2'),
                ('segment_food_retail', 'courier_1'),
            ],
        ),
    ],
)
async def test_with_ban(base_test_run):
    await base_test_run()


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'planner.ban_indirect_edges.enabled': 'true',
    },
)
@pytest.mark.parametrize(
    'expected_whitelist,expected_direct_edges,expected_filtered_edges',
    [
        (
            [['eats', 'eda'], ['food_retail', 'eda'], ['grocery', 'lavka']],
            [
                ('segment_default_courier', 'courier_1'),
                ('segment_default_express', 'express_2'),
                ('segment_eats', 'courier_1'),
                ('segment_eats', 'eda_3'),
                ('segment_food_retail', 'express_2'),
            ],
            [
                ('segment_default_courier', 'express_2'),
                ('segment_default_courier', 'eda_3'),
                ('segment_default_express', 'courier_1'),
                ('segment_default_express', 'eda_3'),
                ('segment_eats', 'express_2'),
                ('segment_food_retail', 'courier_1'),
            ],
        ),
    ],
)
async def test_with_ban_check_defaults(base_test_run):
    await base_test_run()
