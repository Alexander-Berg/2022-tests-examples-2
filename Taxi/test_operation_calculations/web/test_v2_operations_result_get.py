import http

import pytest


@pytest.mark.pgsql(
    'operation_calculations', files=['pg_operations_result.sql'],
)
@pytest.mark.parametrize(
    'task_id, expected_status, expected_content',
    (
        pytest.param(
            '61711eb7b7e4790047d4fe51',
            http.HTTPStatus.OK,
            {
                'task_id': '61711eb7b7e4790047d4fe51',
                'result': {
                    'total_result': {
                        'gmv': 1114358924.9066193,
                        'fact_subs': 16791461.800796755,
                        'plan_subs': 16791251.37679672,
                        'geo_subs_fact': 16773251.376796719,
                        'fact_nmfg_subs': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'do_x_get_y_subs_fact': 18000.0,
                    },
                    'sub_operation_results': [
                        {
                            'charts': [
                                {
                                    'gmv': 335101335.0612023,
                                    'trips': 5,
                                    'fact_subs': 5806560.396399658,
                                    'plan_subs': 5806592.796399659,
                                    'drivers_days': 92744,
                                    'fact_subs_gmv': 0.01732777458299042,
                                    'geo_subs_fact': 5806592.796399659,
                                    'plan_subs_gmv': 0.0,
                                    'fact_nmfg_subs': 0,
                                    'plan_nmfg_subs': 0,
                                    'do_x_get_y_subs_fact': 0.0,
                                    'drivers_days_with_nmfg': 0,
                                },
                                {
                                    'gmv': 227066786.16750032,
                                    'trips': 10,
                                    'fact_subs': 5310920.153099857,
                                    'plan_subs': 5310920.153099857,
                                    'drivers_days': 40506,
                                    'fact_subs_gmv': 0.023389242622133877,
                                    'geo_subs_fact': 5292920.153099857,
                                    'plan_subs_gmv': 0.0,
                                    'fact_nmfg_subs': 0,
                                    'plan_nmfg_subs': 0,
                                    'do_x_get_y_subs_fact': 18000.0,
                                    'drivers_days_with_nmfg': 0,
                                },
                                {
                                    'gmv': 68649574.82109995,
                                    'trips': 15,
                                    'fact_subs': 1981847.7821000025,
                                    'plan_subs': 1981847.7821000025,
                                    'drivers_days': 9469,
                                    'fact_subs_gmv': 0.028869046709534274,
                                    'geo_subs_fact': 1981847.7821000025,
                                    'plan_subs_gmv': 0.0,
                                    'fact_nmfg_subs': 0,
                                    'plan_nmfg_subs': 0,
                                    'do_x_get_y_subs_fact': 0.0,
                                    'drivers_days_with_nmfg': 0,
                                },
                            ],
                            'result': {
                                'gmv': 788931399.1483217,
                                'fact_subs': 15390964.172098145,
                                'plan_subs': 13520630.640199518,
                                'geo_subs_fact': 15372751.372098144,
                                'fact_nmfg_subs': 0.0,
                                'plan_nmfg_subs': 0,
                                'do_x_get_y_subs_fact': 18000.0,
                            },
                            'guarantees': [
                                {'guarantee': 75.0, 'count_trips': 5},
                                {'guarantee': 350.0, 'count_trips': 10},
                                {'guarantee': 825.0, 'count_trips': 15},
                            ],
                            'sub_operation_id': 1,
                            'warnings': [],
                        },
                        {
                            'charts': [
                                {
                                    'gmv': 335101335.0612023,
                                    'trips': 5,
                                    'fact_subs': 5806560.396399658,
                                    'plan_subs': 5806592.796399659,
                                    'drivers_days': 92744,
                                    'fact_subs_gmv': 0.01732777458299042,
                                    'geo_subs_fact': 5806592.796399659,
                                    'plan_subs_gmv': 0.0,
                                    'fact_nmfg_subs': 0,
                                    'plan_nmfg_subs': 0,
                                    'do_x_get_y_subs_fact': 0.0,
                                    'drivers_days_with_nmfg': 0,
                                },
                                {
                                    'gmv': 227066786.16750032,
                                    'trips': 10,
                                    'fact_subs': 5310920.153099857,
                                    'plan_subs': 5310920.153099857,
                                    'drivers_days': 40506,
                                    'fact_subs_gmv': 0.023389242622133877,
                                    'geo_subs_fact': 5292920.153099857,
                                    'plan_subs_gmv': 0.0,
                                    'fact_nmfg_subs': 0,
                                    'plan_nmfg_subs': 0,
                                    'do_x_get_y_subs_fact': 18000.0,
                                    'drivers_days_with_nmfg': 0,
                                },
                                {
                                    'gmv': 68649574.82109995,
                                    'trips': 15,
                                    'fact_subs': 1981847.7821000025,
                                    'plan_subs': 1981847.7821000025,
                                    'drivers_days': 9469,
                                    'fact_subs_gmv': 0.028869046709534274,
                                    'geo_subs_fact': 1981847.7821000025,
                                    'plan_subs_gmv': 0.0,
                                    'fact_nmfg_subs': 0,
                                    'plan_nmfg_subs': 0,
                                    'do_x_get_y_subs_fact': 0.0,
                                    'drivers_days_with_nmfg': 0,
                                },
                            ],
                            'result': {
                                'gmv': 788931399.1483217,
                                'fact_subs': 15390964.172098145,
                                'plan_subs': 13520630.640199518,
                                'geo_subs_fact': 15372751.372098144,
                                'fact_nmfg_subs': 0.0,
                                'plan_nmfg_subs': 0,
                                'do_x_get_y_subs_fact': 18000.0,
                            },
                            'guarantees': [
                                {'guarantee': 75.0, 'count_trips': 5},
                                {'guarantee': 350.0, 'count_trips': 10},
                                {'guarantee': 825.0, 'count_trips': 15},
                            ],
                            'sub_operation_id': 2,
                            'warnings': [],
                        },
                    ],
                },
            },
        ),
        pytest.param(
            '61711eb7b7e4790047d4feee',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'NotFound',
                'message': (
                    'result for task 61711eb7b7e4790047d4feee not found'
                ),
            },
        ),
        pytest.param(
            '61711eb7b7e4790047d4fe52',
            http.HTTPStatus.OK,
            {
                'error': 'ERROR: \n\nTraceback: [<FrameSummary file /home/dpano/arc-backend-py3/services/operation-calculations/operation_calculations/crontasks/run_nmfg_operations.py, line 75 in do_stuff>, <FrameSummary file /home/dpano/arc-backend-py3/services/operation-calculations/operation_calculations/crontasks/run_nmfg_operations.py, line 96 in process_task>, <FrameSummary file /home/dpano/arc-backend-py3/services/operation-calculations/operation_calculations/crontasks/run_nmfg_operations.py, line 160 in fetch_data>, <FrameSummary file /home/dpano/arc-backend-py3/taxi/pg/pool.py, line 230 in fetch>, <FrameSummary file /home/dpano/arc-backend-py3/taxi/pg/pool.py, line 200 in acquire>]',  # noqa: E501 pylint: disable=line-too-long
                'task_id': '61711eb7b7e4790047d4fe52',
            },
        ),
        pytest.param(
            '62541f18637ede004af0cbdc',
            http.HTTPStatus.OK,
            {
                'draft_info': {
                    'draft_id': 777777,
                    'is_multidraft': True,
                    'ticket': 'RUPRICING-78',
                },
                'result': {
                    'sub_operation_results': [
                        {
                            'charts': [
                                {
                                    'do_x_get_y_subs_fact': 0,
                                    'drivers_days': 0,
                                    'drivers_days_with_nmfg': 0,
                                    'fact_nmfg_subs': 0,
                                    'fact_subs': 0,
                                    'fact_subs_gmv': 0,
                                    'geo_subs_fact': 0,
                                    'gmv': 0,
                                    'plan_nmfg_subs': 0,
                                    'plan_subs': 0,
                                    'plan_subs_gmv': 0,
                                    'trips': 1,
                                },
                            ],
                            'guarantees': [
                                {'count_trips': 1, 'guarantee': 10},
                            ],
                            'result': {
                                'do_x_get_y_subs_fact': 0,
                                'fact_nmfg_subs': 0,
                                'fact_subs': 0,
                                'geo_subs_fact': 0,
                                'gmv': 0,
                                'plan_nmfg_subs': 0,
                                'plan_subs': 0,
                            },
                            'sub_operation_id': 0,
                            'warnings': [],
                        },
                    ],
                    'total_result': {
                        'do_x_get_y_subs_fact': 0,
                        'fact_nmfg_subs': 0,
                        'fact_subs': 0,
                        'geo_subs_fact': 0,
                        'gmv': 0,
                        'plan_nmfg_subs': 0,
                        'plan_subs': 0,
                    },
                },
                'task_id': '62541f18637ede004af0cbdc',
            },
        ),
    ),
)
async def test_v2_operations_result_get(
        web_app_client, task_id, expected_status, expected_content,
):

    response = await web_app_client.get(
        f'/v2/operations/result/', params={'task_id': task_id},
    )
    assert response.status == expected_status
    if response.status == 200:
        results = await response.json()
        assert results == expected_content
