ALL_RPS_RESPONSE = {
    'vector': [
        {
            'timeseries': {
                'alias': 'all_rps',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [1, 2, 12],
            },
        },
        {
            'timeseries': {
                'alias': 'all_rps',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_taxi_yandex_net',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [1, 2, 15],
            },
        },
        {
            'timeseries': {
                'alias': 'all_rps',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net_view_POST',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [1, 1, 1],
            },
        },
        {
            'timeseries': {
                'alias': 'all_rps',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net_view2_GET',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [0, 1, 11],
            },
        },
    ],
}

BAD_RPS_RESPONSE = {
    'vector': [
        {
            'timeseries': {
                'alias': 'bad_rps',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [0.1, 0.4, 3.4],
            },
        },
        {
            'timeseries': {
                'alias': 'bad_rps',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_taxi_yandex_net',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [0.1, 0.4, 3.4],
            },
        },
        {
            'timeseries': {
                'alias': 'bad_rps',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net_view_POST',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [0.1, 0.1, 0.1],
            },
        },
        {
            'timeseries': {
                'alias': 'bad_rps',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net_view2_GET',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [0, 0.3, 3.3],
            },
        },
    ],
}

TIMINGS_P95_RESPONSE = {
    'vector': [
        {
            'timeseries': {
                'alias': 'timings_p95',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'sensor': 'ok_request_timings',
                    'percentile': '95',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [30.3, 20.1, 50.2],
            },
        },
        {
            'timeseries': {
                'alias': 'timings_p95',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'sensor': 'ok_request_timings',
                    'percentile': '95',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_taxi_yandex_net',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [30.3, 20.1, 50.2],
            },
        },
        {
            'timeseries': {
                'alias': 'timings_p95',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'sensor': 'ok_request_timings',
                    'percentile': '95',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net_view_POST',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [30.3, 20.1, 50.2],
            },
        },
        {
            'timeseries': {
                'alias': 'timings_p95',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'sensor': 'ok_request_timings',
                    'percentile': '95',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net_view2_GET',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [30.3, 20.1, 50.2],
            },
        },
    ],
}

TIMINGS_P98_RESPONSE = {
    'vector': [
        {
            'timeseries': {
                'alias': 'timings_p98',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'sensor': 'ok_request_timings',
                    'percentile': '95',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [60.3, 40.1, 100.2],
            },
        },
        {
            'timeseries': {
                'alias': 'timings_p98',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'sensor': 'ok_request_timings',
                    'percentile': '95',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_taxi_yandex_net',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [60.3, 40.1, 100.2],
            },
        },
        {
            'timeseries': {
                'alias': 'timings_p98',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'sensor': 'ok_request_timings',
                    'percentile': '95',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net_view_POST',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [60.3, 40.1, 100.2],
            },
        },
        {
            'timeseries': {
                'alias': 'timings_p98',
                'kind': 'DGAUGE',
                'labels': {
                    'host': 'cluster',
                    'cluster': 'production',
                    'project': 'taxi',
                    'service': 'dorblu',
                    'sensor': 'ok_request_timings',
                    'percentile': '95',
                    'group': 'dorblu_rtc_hejmdal_dirlink',
                    'object': 'hejmdal_yandex_net_view2_GET',
                },
                'timestamps': [1570643581000, 1570643641000, 1570643701000],
                'values': [60.3, 40.1, 100.2],
            },
        },
    ],
}


async def test_handles_health(taxi_hejmdal, mockserver):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('services_component/invalidate')

    @mockserver.json_handler(
        '/solomon-sensors/api/v2/projects/taxi/sensors/data',
    )
    def _mock_solomon_sensors_data(request, *args, **kwargs):
        if 'sensor="*_rps"' in request.json['program']:
            return ALL_RPS_RESPONSE
        if (
                'sensor="4*_rps|errors_rps|timeouts_rps"'
                in request.json['program']
        ):
            return BAD_RPS_RESPONSE
        if 'percentile="95"' in request.json['program']:
            return TIMINGS_P95_RESPONSE
        if 'percentile="98"' in request.json['program']:
            return TIMINGS_P98_RESPONSE
        return {}

    response = await taxi_hejmdal.post(
        'v1/health/handles/states',
        params={'service_id': 139, 'env': 'stable'},
    )

    table = response.json()['table']
    assert len(table) == 4

    assert table[0]['domain_name'] == 'hejmdal.taxi.yandex.net'
    assert table[0]['status_color'] == '#FFD100'
    assert table[0]['rps_status'] == {
        'avg_by_hour': 6.0,
        'current': 15.0,
        'status_color': '#FFD100',
    }
    assert table[0]['timings_p95_status'] == {
        'avg_by_hour': 33.53333333333334,
        'current': 50.2,
        'status_color': '#63FF00',
    }
    assert table[0]['timings_p98_status'] == {
        'avg_by_hour': 66.86666666666667,
        'current': 100.2,
        'status_color': '#63FF00',
    }
    assert table[0]['bad_rps_status'] == {
        'avg_by_hour': 21.666666666666668,
        'current': 22.666666666666664,
        'status_color': '#0DFF00',
    }

    assert table[1]['domain_name'] == 'hejmdal.yandex.net'
    assert table[1]['status_color'] == '#FFF600'
    assert table[1]['rps_status'] == {
        'avg_by_hour': 5.0,
        'current': 12.0,
        'status_color': '#FFF600',
    }
    assert table[1]['timings_p95_status'] == {
        'avg_by_hour': 33.53333333333334,
        'current': 50.2,
        'status_color': '#5CFF00',
    }
    assert table[1]['timings_p98_status'] == {
        'avg_by_hour': 66.86666666666667,
        'current': 100.2,
        'status_color': '#5CFF00',
    }
    assert table[1]['bad_rps_status'] == {
        'avg_by_hour': 26.0,
        'current': 28.333333333333332,
        'status_color': '#17FF00',
    }

    assert table[2]['domain_name'] == 'view2_GET'
    assert table[2]['status_color'] == '#FDFF00'
    assert table[2]['rps_status'] == {
        'avg_by_hour': 4.0,
        'current': 11.0,
        'status_color': '#FDFF00',
    }
    assert table[2]['timings_p95_status'] == {
        'avg_by_hour': 33.53333333333334,
        'current': 50.2,
        'status_color': '#57FF00',
    }
    assert table[2]['timings_p98_status'] == {
        'avg_by_hour': 66.86666666666667,
        'current': 100.2,
        'status_color': '#57FF00',
    }
    assert table[2]['bad_rps_status'] == {
        'avg_by_hour': 30.0,
        'current': 30.0,
        'status_color': '#00FF00',
    }

    assert table[3]['domain_name'] == 'view_POST'
    assert table[3]['status_color'] == '#11FF00'
    assert table[3]['rps_status'] == {
        'avg_by_hour': 1.0,
        'current': 1.0,
        'status_color': '#00FF00',
    }
    assert table[3]['timings_p95_status'] == {
        'avg_by_hour': 33.53333333333334,
        'current': 50.2,
        'status_color': '#11FF00',
    }
    assert table[3]['timings_p98_status'] == {
        'avg_by_hour': 66.86666666666667,
        'current': 100.2,
        'status_color': '#11FF00',
    }
    assert table[3]['bad_rps_status'] == {
        'avg_by_hour': 10.000000000000002,
        'current': 10.0,
        'status_color': '#00FF00',
    }
