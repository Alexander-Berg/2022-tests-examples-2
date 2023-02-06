import pytest
from collections import defaultdict
from itertools import combinations


@pytest.fixture
async def base_test_run(
        run_watchers,
        rt_robot_execute,
        testpoint,
        dummy_router,
        create_segment,
        create_candidate,
        num_expected_segments,
        expected_segments,
        equivalent_segments,
):
    async def runner():
        @testpoint('ld::candidates::returned_segments')
        def returned_segments(data):
            assert 'segments' in data
            assert len(data['segments']) == num_expected_segments
            if expected_segments is not None:
                assert sorted(
                    [s['segment_id'] for s in data['segments']],
                ) == sorted(expected_segments)
            # check equivalency classes for each pair of segments

            for s1, s2 in combinations(data['segments'], 2):
                same_hashes = (
                    s1['hash'] is not None
                    and s2['hash'] is not None
                    and s1['hash'] == s2['hash']
                )
                same_classes = False
                for equivalency_class in equivalent_segments:
                    if (
                            s1['segment_id'] in equivalency_class
                            and s2['segment_id'] in equivalency_class
                    ):
                        same_classes = True
                        break
                assert (
                    same_hashes == same_classes
                ), f"{s1['segment_id']}, {s2['segment_id']}"

        # examples of eda claims: https://tariff-editor.taxi.yandex-team.ru/corp-claims?corp_client_id=4decd14f25424e8b82b6d3e4f56d23b2
        # examples of lavka claims: https://tariff-editor.taxi.yandex-team.ru/corp-claims?corp_client_id=8183ed5340e14ea1ab061b0df7f0cd32
        # to get segment info, use the instructions from https://wiki.yandex-team.ru/taxi/backend/devtools/#kakdernutruchkuvprode
        # taxi-tvm-curl -e production -s logistic-dispatcher cargo-dispatch --socks5 localhost:1080 -X POST -H "Content-Type: application/json" http://cargo-dispatch.taxi.yandex.net/v1/segment/info?segment_id=SEGMENT_ID
        segment_courier_1 = create_segment(
            segment_id='segment_courier_1',
            additional_taxi_requirements={'taxi_classes': ['courier']},
        )

        segment_courier_2 = create_segment(
            segment_id='segment_courier_2',
            additional_taxi_requirements={'taxi_classes': ['courier']},
        )

        segment_courier_3 = create_segment(
            segment_id='segment_courier_3',
            additional_taxi_requirements={'taxi_classes': ['courier']},
            max_route_distance_courier=10000,
        )

        segment_express_1 = create_segment(
            segment_id='segment_express_1',
            additional_taxi_requirements={'taxi_classes': ['express']},
        )

        segment_lavka_1 = create_segment(
            segment_id='segment_lavka_1',
            employer='grocery',
            additional_taxi_requirements={
                'taxi_classes': ['lavka'],
                'dispatch_requirements': {
                    'soft_requirements': [
                        {
                            'logistic_group': '1',
                            'performers_restriction_type': 'group_only',
                            'shift_type': 'eats',
                            'type': 'performer_group',
                        },
                    ],
                },
            },
        )

        segment_lavka_2 = create_segment(
            segment_id='segment_lavka_2',
            employer='grocery',
            additional_taxi_requirements={
                'taxi_classes': ['lavka'],
                'dispatch_requirements': {
                    'soft_requirements': [
                        {
                            'logistic_group': '1',
                            'performers_restriction_type': 'group_only',
                            'shift_type': 'eats',
                            'type': 'performer_group',
                        },
                    ],
                },
            },
            custom_context={
                'delivery_flags': {'assign_rover': 'false'}
            },
        )

        segment_lavka_3 = create_segment(
            segment_id='segment_lavka_3',
            employer='grocery',
            additional_taxi_requirements={
                'taxi_classes': ['lavka'],
                'dispatch_requirements': {
                    'soft_requirements': [
                        {
                            'logistic_group': '1',
                            'performers_restriction_type': 'group_only',
                            'shift_type': 'eats',
                            'type': 'performer_group',
                        },
                    ],
                },
            },
            custom_context={
                'delivery_flags': {'assign_rover': 'true'}
            },
        )

        candidate_courier = create_candidate(
            dbid_uuid='courier_1',
            tariff_classes=['courier'],
            position=[55, 37],
        )

        await rt_robot_execute('segments_journal')
        await rt_robot_execute('p2p_allocation')

        assert returned_segments.times_called == 1

    return runner


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'candidates.same_request_shrinking.enabled': 'true',
        'candidates.restore_duplicated_tasks.enabled': 'false',
        'candidates.optimize_queries_for_all.enabled': 'false',
    },
)
@pytest.mark.parametrize(
    'num_expected_segments,expected_segments,equivalent_segments',
    [(6, None, [{'segment_lavka_1', 'segment_lavka_2'}])],
)
async def test_basic(base_test_run):
    await base_test_run()


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'candidates.same_request_shrinking.enabled': 'true',
        'candidates.restore_duplicated_tasks.enabled': 'true',
        'candidates.optimize_queries_for_all.enabled': 'false',
    },
)
@pytest.mark.parametrize(
    'num_expected_segments,expected_segments,equivalent_segments',
    [
        (
            7,
            [
                'segment_courier_1',
                'segment_courier_2',
                'segment_courier_3',
                'segment_express_1',
                'segment_lavka_1',
                'segment_lavka_2',
                'segment_lavka_3',
            ],
            [{'segment_lavka_1', 'segment_lavka_2'}],
        ),
    ],
)
async def test_restore_duplicated_tasks(base_test_run):
    await base_test_run()


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'candidates.same_request_shrinking.enabled': 'true',
        'candidates.restore_duplicated_tasks.enabled': 'true',
        'candidates.optimize_queries_for_all.enabled': 'true',
    },
)
@pytest.mark.parametrize(
    'num_expected_segments,expected_segments,equivalent_segments',
    [
        (
            7,
            [
                'segment_courier_1',
                'segment_courier_2',
                'segment_courier_3',
                'segment_express_1',
                'segment_lavka_1',
                'segment_lavka_2',
                'segment_lavka_3',
            ],
            [
                {'segment_lavka_1', 'segment_lavka_2'},
                {'segment_courier_1', 'segment_courier_2'},
            ],
        ),
    ],
)
async def test_restore_duplicated_tasks_and_optimize_queries_for_all(
        base_test_run,
):
    await base_test_run()


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'candidates.same_request_shrinking.enabled': 'true',
        'candidates.restore_duplicated_tasks.enabled': 'false',
        'candidates.optimize_queries_for_all.enabled': 'true',
    },
)
@pytest.mark.parametrize(
    'num_expected_segments,expected_segments,equivalent_segments',
    [
        (
            5,
            None,
            [
                {'segment_lavka_1', 'segment_lavka_2'},
                {'segment_courier_1', 'segment_courier_2'},
            ],
        ),
    ],
)
async def test_restore_optimize_for_all_without_restore_duplicated_tasks(
        base_test_run,
):
    await base_test_run()
