import datetime

import pytest


@pytest.mark.now('2020-09-07T12:00:00+03:00')
async def test_service_resource_usage_stat_save(taxi_hejmdal, pgsql):
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('distlock/digest_preparer')

    cursor = pgsql['hejmdal'].cursor()
    query = """
            select service_id, period_start, period_end,
            stat_data from service_stats where stat_id='cpu_low_usage'
            and service_id=2
    """
    cursor.execute(query)
    db_res = cursor.fetchall()

    assert len(db_res) == 1
    db_row = db_res[0]
    assert len(db_row) == 4
    assert db_row[0] == 2
    assert db_row[1] == datetime.datetime(2020, 8, 31, 9, 0, 0)
    assert db_row[2] == datetime.datetime(2020, 9, 7, 9, 0, 0)
    assert len(db_row[3]) == 1
    assert abs(db_row[3]['not_ok_percent'] - 71) < 1


@pytest.mark.now('2020-09-07T12:00:00+03:00')
async def test_service_resource_usage_handler(taxi_hejmdal, mocked_time):
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('distlock/digest_preparer')
    await taxi_hejmdal.invalidate_caches(
        clean_update=False, cache_names=['service-stats-cache'],
    )

    response = await taxi_hejmdal.get(
        '/v1/analytics/service_resource_usage', params={'service_id': 2},
    )

    assert response.status_code == 200
    cpu_usage_link1 = (
        'https://yasm.yandex-team.ru/chart/itype=test_service2;'
        'hosts=test_service_host_name_1;signals=%7Bquant(portoi'
        'nst-cpu_limit_usage_perc_hgram%2C%20med)%7D/?from=1598'
        '864400000&to=1599469200000'
    )
    ram_usage_link1 = (
        'https://yasm.yandex-team.ru/chart/itype=test_service2;'
        'hosts=test_service_host_name_1;signals=%7Bquant(portoi'
        'nst-memory_anon_unevict_limit_usage_perc_hgram%2C%20m'
        'ed)%7D/?from=1598864400000&to=1599469200000'
    )
    assert response.json() == {
        'cpu_usage': {
            'high_usage': {
                'not_ok_time_prc': 0,
                'period': {
                    'start': '2020-08-31T09:00:00+00:00',
                    'end': '2020-09-07T09:00:00+00:00',
                },
            },
            'low_usage': {
                'not_ok_time_prc': 71,
                'period': {
                    'start': '2020-08-31T09:00:00+00:00',
                    'end': '2020-09-07T09:00:00+00:00',
                },
            },
            'usage_graph_link': cpu_usage_link1,
        },
        'ram_usage': {
            'high_usage': {
                'not_ok_time_prc': 0,
                'period': {
                    'start': '2020-08-31T09:00:00+00:00',
                    'end': '2020-09-07T09:00:00+00:00',
                },
            },
            'low_usage': {
                'not_ok_time_prc': 0,
                'period': {
                    'start': '2020-08-31T09:00:00+00:00',
                    'end': '2020-09-07T09:00:00+00:00',
                },
            },
            'usage_graph_link': ram_usage_link1,
        },
    }

    mocked_time.set(datetime.datetime(2020, 9, 14, 9, 0, 0))
    await taxi_hejmdal.run_task('distlock/digest_preparer')
    await taxi_hejmdal.invalidate_caches(
        clean_update=False, cache_names=['service-stats-cache'],
    )

    response = await taxi_hejmdal.get(
        '/v1/analytics/service_resource_usage', params={'service_id': 2},
    )

    assert response.status_code == 200
    cpu_usage_link2 = (
        'https://yasm.yandex-team.ru/chart/itype=test_service2;'
        'hosts=test_service_host_name_1;signals=%7Bquant(portoi'
        'nst-cpu_limit_usage_perc_hgram%2C%20med)%7D/?from=1599'
        '469200000&to=1600074000000'
    )
    ram_usage_link2 = (
        'https://yasm.yandex-team.ru/chart/itype=test_service2;'
        'hosts=test_service_host_name_1;signals=%7Bquant(portoi'
        'nst-memory_anon_unevict_limit_usage_perc_hgram%2C%20me'
        'd)%7D/?from=1599469200000&to=1600074000000'
    )
    assert response.json() == {
        'cpu_usage': {
            'high_usage': {
                'not_ok_time_prc': 0,
                'period': {
                    'start': '2020-09-07T09:00:00+00:00',
                    'end': '2020-09-14T09:00:00+00:00',
                },
            },
            'low_usage': {
                'not_ok_time_prc': 0,
                'period': {
                    'start': '2020-09-07T09:00:00+00:00',
                    'end': '2020-09-14T09:00:00+00:00',
                },
            },
            'usage_graph_link': cpu_usage_link2,
        },
        'ram_usage': {
            'high_usage': {
                'not_ok_time_prc': 0,
                'period': {
                    'start': '2020-09-07T09:00:00+00:00',
                    'end': '2020-09-14T09:00:00+00:00',
                },
            },
            'low_usage': {
                'not_ok_time_prc': 0,
                'period': {
                    'start': '2020-09-07T09:00:00+00:00',
                    'end': '2020-09-14T09:00:00+00:00',
                },
            },
            'usage_graph_link': ram_usage_link2,
        },
    }


@pytest.mark.now('2020-09-07T12:00:00+03:00')
async def test_db_resource_usage_handler(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('distlock/digest_preparer')
    await taxi_hejmdal.invalidate_caches(
        clean_update=False, cache_names=['service-stats-cache'],
    )

    response = await taxi_hejmdal.get(
        '/v1/analytics/service_resource_usage', params={'service_id': 3},
    )

    assert response.status_code == 200
    cpu_usage_link1 = """https://solomon.yandex-team.ru/admin/projects/internal-mdb/autoGraph?expression=100%20*%20%7Bcontainer%3D'test_pg_host_name_1%7Ctest_pg_host_name_2'%2Chost%3D'by_cid_container'%2Cname%3D'%2Fporto%2Fcpu_usage'%7D%20%2F%20%7Bcontainer%3D'test_pg_host_name_1%7Ctest_pg_host_name_2'%2Chost%3D'by_cid_container'%2Cname%3D'%2Fporto%2Fcpu_limit'%7D&b=2020-08-31T09%3A00%3A00Z&e=2020-09-07T09%3A00%3A00Z"""  # noqa: E501 pylint: disable=line-too-long
    ram_usage_link1 = """https://solomon.yandex-team.ru/admin/projects/internal-mdb/autoGraph?expression=100%20*%20%7Bcontainer%3D'test_pg_host_name_1%7Ctest_pg_host_name_2'%2Chost%3D'by_cid_container'%2Cname%3D'%2Fporto%2Fanon_usage'%7D%20%2F%20%7Bcontainer%3D'test_pg_host_name_1%7Ctest_pg_host_name_2'%2Chost%3D'by_cid_container'%2Cname%3D'%2Fporto%2Fanon_limit'%7D&b=2020-08-31T09%3A00%3A00Z&e=2020-09-07T09%3A00%3A00Z"""  # noqa: E501 pylint: disable=line-too-long
    assert response.json() == {
        'cpu_usage': {
            'high_usage': {
                'not_ok_time_prc': 0,
                'period': {
                    'start': '2020-08-31T09:00:00+00:00',
                    'end': '2020-09-07T09:00:00+00:00',
                },
            },
            'low_usage': {
                'not_ok_time_prc': 0,
                'period': {
                    'start': '2020-08-31T09:00:00+00:00',
                    'end': '2020-09-07T09:00:00+00:00',
                },
            },
            'usage_graph_link': cpu_usage_link1,
        },
        'ram_usage': {
            'high_usage': {
                'not_ok_time_prc': 71,
                'period': {
                    'start': '2020-08-31T09:00:00+00:00',
                    'end': '2020-09-07T09:00:00+00:00',
                },
            },
            'low_usage': {
                'not_ok_time_prc': 0,
                'period': {
                    'start': '2020-08-31T09:00:00+00:00',
                    'end': '2020-09-07T09:00:00+00:00',
                },
            },
            'usage_graph_link': ram_usage_link1,
        },
    }
