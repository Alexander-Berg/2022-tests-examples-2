import pytest

from operation_calculations.generated.cron import run_cron
import operation_calculations.geosubventions.storage as storage_lib


@pytest.mark.pgsql(
    'operation_calculations',
    files=[
        'gp_data_v2.sql',
        'pg_operations_params.sql',
        'pg_operations_status.sql',
    ],
)
@pytest.mark.now('2020-01-01T01:00:00')
async def test_run_nmfg_operations(web_context, web_app_client):
    await run_cron.main(
        ['operation_calculations.crontasks.run_nmfg_operations', '-t', '0'],
    )
    storage = storage_lib.GeoSubventionsStorage(web_context)
    task_result = await storage.get_nmfg_task_result(
        '61711eb7b7e4790047d4fe50',
    )
    assert task_result['sub_operations_results'] == {
        'sub_operation_results': [
            {
                'charts': [
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 5,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 2.5,
                        'drivers_days_with_nmfg': 2.5,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0.0,
                        'geo_subs_fact': 0.0,
                        'gmv': 5875.0,
                        'plan_nmfg_subs': 4712.5,
                        'plan_subs': 4712.5,
                        'plan_subs_gmv': 0.8021276595744681,
                        'trips': 10,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 15,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 20,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 25,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 30,
                    },
                ],
                'guarantees': [
                    {'count_trips': 5, 'guarantee': 2020.0},
                    {'count_trips': 10, 'guarantee': 4235.0},
                    {'count_trips': 15, 'guarantee': 6655.0},
                    {'count_trips': 20, 'guarantee': 9275.0},
                    {'count_trips': 25, 'guarantee': 12095.0},
                    {'count_trips': 30, 'guarantee': 15110.0},
                ],
                'result': {
                    'do_x_get_y_subs_fact': 0.0,
                    'fact_nmfg_subs': 2.1399999999999997,
                    'fact_subs': 2.1399999999999997,
                    'geo_subs_fact': 0.0,
                    'gmv': 88125.0,
                    'plan_nmfg_subs': 4712.5,
                    'plan_subs': 4712.5,
                    'subgmv_global': 0.0499,
                    'subgmv_local': 0.0535,
                },
                'sub_operation_id': 0,
                'warnings': [],
            },
            {
                'charts': [
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 5,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 2.5,
                        'drivers_days_with_nmfg': 2.5,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0.0,
                        'geo_subs_fact': 0.0,
                        'gmv': 5875.0,
                        'plan_nmfg_subs': 937.5,
                        'plan_subs': 937.5,
                        'plan_subs_gmv': 0.1595744680851064,
                        'trips': 10,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 15,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 20,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 25,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 30,
                    },
                ],
                'conflicts': [
                    {
                        'common_drivers': 2.5,
                        'common_gmv': 5875.0,
                        'conflict_operation_id': 2,
                    },
                ],
                'guarantees': [
                    {'count_trips': 5, 'guarantee': 1265.0},
                    {'count_trips': 10, 'guarantee': 2725.0},
                    {'count_trips': 15, 'guarantee': 4390.0},
                    {'count_trips': 20, 'guarantee': 6255.0},
                    {'count_trips': 25, 'guarantee': 8320.0},
                    {'count_trips': 30, 'guarantee': 10580.0},
                ],
                'result': {
                    'do_x_get_y_subs_fact': 0.0,
                    'fact_nmfg_subs': 0.0,
                    'fact_subs': 0.0,
                    'geo_subs_fact': 0.0,
                    'gmv': 5875.0,
                    'plan_nmfg_subs': 937.5,
                    'plan_subs': 937.5,
                    'subgmv_global': 0.0099,
                    'subgmv_local': 0.1596,
                },
                'sub_operation_id': 1,
                'warnings': [],
            },
            {
                'charts': [
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 5,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 2.5,
                        'drivers_days_with_nmfg': 2.5,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0.0,
                        'geo_subs_fact': 0.0,
                        'gmv': 5875.0,
                        'plan_nmfg_subs': 937.5,
                        'plan_subs': 937.5,
                        'plan_subs_gmv': 0.1595744680851064,
                        'trips': 10,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 15,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 20,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 25,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 30,
                    },
                ],
                'conflicts': [
                    {
                        'common_drivers': 2.5,
                        'common_gmv': 5875.0,
                        'conflict_operation_id': 1,
                    },
                ],
                'guarantees': [
                    {'count_trips': 5, 'guarantee': 1265.0},
                    {'count_trips': 10, 'guarantee': 2725.0},
                    {'count_trips': 15, 'guarantee': 4390.0},
                    {'count_trips': 20, 'guarantee': 6255.0},
                    {'count_trips': 25, 'guarantee': 8320.0},
                    {'count_trips': 30, 'guarantee': 10580.0},
                ],
                'result': {
                    'do_x_get_y_subs_fact': 0.0,
                    'fact_nmfg_subs': 0.0,
                    'fact_subs': 0.0,
                    'geo_subs_fact': 0.0,
                    'gmv': 5875.0,
                    'plan_nmfg_subs': 937.5,
                    'plan_subs': 937.5,
                    'subgmv_global': 0.0099,
                    'subgmv_local': 0.1596,
                },
                'sub_operation_id': 2,
                'warnings': [],
            },
            {
                'charts': [
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 5,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 5.0,
                        'drivers_days_with_nmfg': 5.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0.0,
                        'geo_subs_fact': 0.0,
                        'gmv': 11750.0,
                        'plan_nmfg_subs': 950.0,
                        'plan_subs': 950.0,
                        'plan_subs_gmv': 0.08085106382978724,
                        'trips': 10,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 15,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 20,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 25,
                    },
                    {
                        'do_x_get_y_subs_fact': 0.0,
                        'drivers_days': 0.0,
                        'drivers_days_with_nmfg': 0.0,
                        'fact_nmfg_subs': 0.0,
                        'fact_subs': 0.0,
                        'fact_subs_gmv': 0,
                        'geo_subs_fact': 0.0,
                        'gmv': 0.0,
                        'plan_nmfg_subs': 0.0,
                        'plan_subs': 0.0,
                        'plan_subs_gmv': 0,
                        'trips': 30,
                    },
                ],
                'guarantees': [
                    {'count_trips': 5, 'guarantee': 1170.0},
                    {'count_trips': 10, 'guarantee': 2540.0},
                    {'count_trips': 15, 'guarantee': 4110.0},
                    {'count_trips': 20, 'guarantee': 5875.0},
                    {'count_trips': 25, 'guarantee': 7845.0},
                    {'count_trips': 30, 'guarantee': 10015.0},
                ],
                'result': {
                    'do_x_get_y_subs_fact': 0.0,
                    'fact_nmfg_subs': 2.1399999999999997,
                    'fact_subs': 2.1399999999999997,
                    'geo_subs_fact': 0.0,
                    'gmv': 94000.0,
                    'plan_nmfg_subs': 950.0,
                    'plan_subs': 950.0,
                    'subgmv_global': 0.0101,
                    'subgmv_local': 0.0101,
                },
                'sub_operation_id': 3,
                'warnings': ['No drivers with that tag'],
            },
        ],
        'total_result': {
            'do_x_get_y_subs_fact': 10.0,
            'fact_nmfg_subs': 0.856,
            'fact_subs': 0.856,
            'geo_subs_fact': 0.0,
            'gmv': 37743.0,
            'plan_nmfg_subs': 3015.0,
            'plan_subs': 3025.0,
            'subgmv': 0.0799,
        },
    }