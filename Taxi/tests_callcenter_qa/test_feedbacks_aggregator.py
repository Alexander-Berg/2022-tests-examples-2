# pylint: disable=redefined-outer-name, import-only-modules, too-many-lines
# flake8: noqa F401
import pytest

from tests_callcenter_qa.utils import get_aggregator_config


@pytest.mark.now('2020-07-19T11:14:00.00Z')
@pytest.mark.parametrize(
    'num_of_buckets',
    (
        pytest.param(
            1,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError': {
                            'thresholds': [{'interval': 2, 'limit': 1}],
                        },
                    },
                ),
            ),
            id='successful_creation',
        ),
        pytest.param(
            1,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError': {
                            'thresholds': [{'interval': 6, 'limit': 2}],
                        },
                    },
                ),
            ),
            id='feedbacks_4',
        ),
        pytest.param(
            1,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError': {
                            'thresholds': [
                                {'interval': 30, 'limit': 2},
                                {'interval': 2, 'limit': 1},
                            ],
                        },
                    },
                ),
            ),
            id='feedbacks_all',
        ),
        pytest.param(
            2,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError': {
                            'thresholds': [{'interval': 3600, 'limit': 2}],
                        },
                        'ServerError2': {
                            'thresholds': [{'interval': 3600, 'limit': 2}],
                        },
                    },
                ),
            ),
            id='feedbacks_2_types',
        ),
        pytest.param(
            0,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError': {
                            'thresholds': [{'interval': 4, 'limit': 3}],
                        },
                    },
                ),
            ),
            id='feedbacks_low_limit',
        ),
        pytest.param(
            1,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError': {
                            'filters': [
                                {
                                    'keys': [
                                        {
                                            'path': 'feedback_info/project',
                                            'alias': 'project',
                                        },
                                    ],
                                    'values': [
                                        {
                                            'project': 'test_project',
                                            'thresholds': [
                                                {'interval': 6, 'limit': 1},
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ),
            ),
            id='one_filter',
        ),
        pytest.param(
            2,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError': {
                            'filters': [
                                {
                                    'keys': [
                                        {
                                            'path': 'feedback_info/project',
                                            'alias': 'project',
                                        },
                                    ],
                                    'values': [
                                        {
                                            'project': 'test_project',
                                            'thresholds': [
                                                {'interval': 6, 'limit': 1},
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                        'ServerError2': {
                            'filters': [
                                {
                                    'keys': [
                                        {
                                            'path': 'feedback_info/project',
                                            'alias': 'project',
                                        },
                                    ],
                                    'values': [
                                        {
                                            'project': 'test_project',
                                            'thresholds': [
                                                {'interval': 10, 'limit': 1},
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ),
            ),
            id='two_feedback_types_for_one_filter',
        ),
        pytest.param(
            2,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError': {
                            'filters': [
                                {
                                    'keys': [
                                        {
                                            'path': 'feedback_info/project',
                                            'alias': 'project',
                                        },
                                    ],
                                    'values': [
                                        {
                                            'project': 'test_project',
                                            'thresholds': [
                                                {'interval': 6, 'limit': 1},
                                            ],
                                        },
                                    ],
                                },
                            ],
                            'thresholds': [
                                {'interval': 30, 'limit': 2},
                                {'interval': 2, 'limit': 1},
                            ],
                        },
                    },
                ),
            ),
            id='filter_with_common_thresholds',
        ),
        pytest.param(
            2,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError': {
                            'filters': [
                                {
                                    'keys': [
                                        {
                                            'path': 'feedback_info/project',
                                            'alias': 'project',
                                        },
                                    ],
                                    'values': [
                                        {
                                            'project': 'test_project',
                                            'thresholds': [
                                                {'interval': 4, 'limit': 1},
                                            ],
                                        },
                                        {
                                            'project': 'test_project_2',
                                            'thresholds': [
                                                {'interval': 4, 'limit': 1},
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ),
            ),
            id='two_values_of_one_filter',
        ),
        pytest.param(
            0,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError3': {
                            'filters': [
                                {
                                    'keys': [
                                        {
                                            'path': 'feedback_info/project',
                                            'alias': 'project',
                                        },
                                    ],
                                    'values': [
                                        {
                                            'thresholds': [
                                                {'interval': 10, 'limit': 2},
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ),
            ),
            id='default_value_for_filter_with_too_big_limit',
        ),
        pytest.param(
            4,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError3': {
                            'filters': [
                                {
                                    'keys': [
                                        {
                                            'path': 'feedback_info/project',
                                            'alias': 'project',
                                        },
                                    ],
                                    'values': [
                                        {
                                            'thresholds': [
                                                {'interval': 10, 'limit': 1},
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ),
            ),
            id='default_value_for_filter',
        ),
        pytest.param(
            0,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError3': {
                            'filters': [
                                {
                                    'keys': [
                                        {
                                            'path': 'wrong_path',
                                            'alias': 'project',
                                        },
                                    ],
                                    'values': [
                                        {
                                            'thresholds': [
                                                {'interval': 10, 'limit': 2},
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ),
            ),
            id='wrong_key_path',
        ),
        pytest.param(
            2,
            marks=pytest.mark.config(
                CALLCENTER_QA_FEEDBACKS_AGGREGATION_SETTINGS=get_aggregator_config(
                    feedback_type_to_settings={
                        'ServerError': {
                            'filters': [
                                {
                                    'keys': [
                                        {
                                            'path': 'feedback_info/project',
                                            'alias': 'project',
                                        },
                                        {
                                            'path': 'call_info/queue',
                                            'alias': 'queue',
                                        },
                                    ],
                                    'values': [
                                        {
                                            'queue': 'disp_on_1',
                                            'project': 'test_project',
                                            'thresholds': [
                                                {'interval': 10, 'limit': 1},
                                            ],
                                        },
                                        {
                                            'project': 'test_project_2',
                                            'thresholds': [
                                                {'interval': 10, 'limit': 1},
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ),
            ),
            id='multiple_filtering',
        ),
    ),
)
@pytest.mark.pgsql('callcenter_qa', files=['prepare_feedback.sql'])
async def test_base(taxi_callcenter_qa, mockserver, num_of_buckets, testpoint):
    @testpoint('feedbacks_aggregator::completed')
    def task_finished(data):
        assert data == num_of_buckets

    async with taxi_callcenter_qa.spawn_task('distlock/feedbacks_aggregator'):
        await task_finished.wait_call()
