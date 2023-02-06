import json

import pytest

_OEP_PIPELINES_FOR_ORCH = [
    {
        'description': 'description_test',
        'st_ticket': '',
        'source': {'name': 'wind-board-rides'},
        'number_of_threads': 1,
        'root': {
            'output': {'sink_name': 'atlas_wind_order'},
            'operations': [
                {
                    'name': 'extract_event_data',
                    'operation_variant': {
                        'operation_name': 'replace_event_data',
                        'type': 'mapper',
                        'arguments': {
                            'src_type': 'stringified_json',
                            'src': ['data'],
                        },
                    },
                },
                {
                    'name': 'set_success_flg',
                    'operation_variant': {
                        'operation_name': 'set_integer_value',
                        'type': 'mapper',
                        'options': [
                            {
                                'filters': [
                                    {
                                        'operation_name': 'field_check',
                                        'type': 'filter',
                                        'arguments': {
                                            'key': 'completeTime',
                                            'policy': 'is_not_null',
                                        },
                                    },
                                    {
                                        'operation_name': 'field_check',
                                        'type': 'filter',
                                        'arguments': {
                                            'key': 'ridingTime',
                                            'policy': 'is_not_null',
                                        },
                                    },
                                    {
                                        'operation_name': 'field_check',
                                        'type': 'filter',
                                        'arguments': {
                                            'key': 'unlockingTime',
                                            'policy': 'is_not_null',
                                        },
                                    },
                                    {
                                        'operation_name': 'field_check',
                                        'type': 'filter',
                                        'arguments': {
                                            'key': 'lockingTime',
                                            'policy': 'is_not_null',
                                        },
                                    },
                                    {
                                        'operation_name': 'field_check',
                                        'type': 'filter',
                                        'arguments': {
                                            'key': 'lockedTime',
                                            'policy': 'is_not_null',
                                        },
                                    },
                                ],
                                'arguments': {
                                    'value': 1,
                                    'dst_key': 'success_flg',
                                },
                            },
                            {
                                'filters': [],
                                'arguments': {
                                    'value': 0,
                                    'dst_key': 'success_flg',
                                },
                            },
                        ],
                    },
                },
                {
                    'name': 'copy-fields-with-new-name',
                    'operation_variant': {
                        'operation_name': 'copy_fields_to_subobject',
                        'type': 'mapper',
                        'arguments': {
                            'src_keys_mapping': [
                                'rideId ride_id',
                                'status status_code',
                                'startLatitude start_lat',
                                'startLongitude start_lon',
                                'endLatitude end_lat',
                                'endLongitude end_lon',
                                'rideCost ride_lcy_cost',
                                'city city_id',
                            ],
                        },
                    },
                },
                {
                    'name': 'replace_negative_city_id_with_zero',
                    'operation_variant': {
                        'operation_name': 'set_integer_value',
                        'type': 'mapper',
                        'options': [
                            {
                                'filters': [
                                    {
                                        'operation_name': 'number_compare',
                                        'type': 'filter',
                                        'arguments': {
                                            'lhs_key': 'city_id',
                                            'rhs_value': 0,
                                            'operator': 'less',
                                        },
                                    },
                                ],
                                'arguments': {
                                    'value': 0,
                                    'dst_key': 'city_id',
                                },
                            },
                            {
                                'filters': [
                                    {
                                        'operation_name': 'field_check',
                                        'type': 'filter',
                                        'arguments': {
                                            'key': 'city_id',
                                            'policy': 'is_null',
                                        },
                                    },
                                ],
                                'arguments': {
                                    'value': 0,
                                    'dst_key': 'city_id',
                                },
                            },
                        ],
                    },
                },
                {
                    'name': 'flat_created_at',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                        'arguments': {
                            'flat_key': 'created_at',
                            'recursive_keys': ['created_at', '$v'],
                        },
                    },
                },
                {
                    'name': 'flat_updated_at',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                        'arguments': {
                            'flat_key': 'updated_at',
                            'recursive_keys': ['updated_at', '$v'],
                        },
                    },
                },
                {
                    'name': 'flat_riding_time',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                        'arguments': {
                            'flat_key': 'ridingTime',
                            'recursive_keys': ['ridingTime', '$v'],
                        },
                    },
                },
                {
                    'name': 'flat_complete_time',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                        'arguments': {
                            'flat_key': 'completeTime',
                            'recursive_keys': ['completeTime', '$v'],
                        },
                    },
                },
                {
                    'name': 'flat_unlocking_time',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                        'arguments': {
                            'flat_key': 'unlockingTime',
                            'recursive_keys': ['unlockingTime', '$v'],
                        },
                    },
                },
                {
                    'name': 'flat_locking_time',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                        'arguments': {
                            'flat_key': 'lockingTime',
                            'recursive_keys': ['lockingTime', '$v'],
                        },
                    },
                },
                {
                    'name': 'flat_locked_time',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                        'arguments': {
                            'flat_key': 'lockedTime',
                            'recursive_keys': ['lockedTime', '$v'],
                        },
                    },
                },
                {
                    'name': 'set_dttm_utc_1_min',
                    'operation_variant': {
                        'operation_name': 'timestamp',
                        'type': 'mapper',
                        'arguments': {
                            'to': 'dttm_utc_1_min',
                            'from': 'created_at',
                            'custom': '%Y-%m-%dT%H:%M:%S',
                            'format': 'custom',
                        },
                    },
                },
                {
                    'name': 'normalize_updated_at',
                    'operation_variant': {
                        'operation_name': 'timestamp',
                        'type': 'mapper',
                        'arguments': {
                            'to': 'updated_at',
                            'from': 'updated_at',
                            'custom': '%Y-%m-%dT%H:%M:%S',
                            'format': 'custom',
                        },
                    },
                },
                {
                    'name': 'set_ts_1_min',
                    'operation_variant': {
                        'operation_name': 'timestamp',
                        'type': 'mapper',
                        'arguments': {
                            'to': 'ts_1_min',
                            'from': 'created_at',
                            'format': 'seconds',
                        },
                    },
                },
                {
                    'name': 'set_ts_1_min_start',
                    'operation_variant': {
                        'operation_name': 'timestamp',
                        'type': 'mapper',
                        'arguments': {
                            'to': 'ts_1_min_start',
                            'from': 'ridingTime',
                            'from_not_exists_policy': 'epoch',
                            'format': 'seconds',
                        },
                    },
                },
                {
                    'name': 'set_ts_1_min_end',
                    'operation_variant': {
                        'operation_name': 'timestamp',
                        'type': 'mapper',
                        'options': [
                            {
                                'filters': [
                                    {
                                        'operation_name': 'field_check',
                                        'type': 'filter',
                                        'arguments': {
                                            'key': 'completeTime',
                                            'policy': 'is_not_null',
                                        },
                                    },
                                ],
                                'arguments': {
                                    'to': 'ts_1_min_end',
                                    'from': 'completeTime',
                                    'format': 'seconds',
                                },
                            },
                            {
                                'filters': [],
                                'arguments': {
                                    'to': 'ts_1_min_end',
                                    'from': 'ridingTime',
                                    'from_not_exists_policy': 'epoch',
                                    'format': 'seconds',
                                },
                            },
                        ],
                    },
                },
                {
                    'name': 'set-quadkey-start',
                    'operation_variant': {
                        'arguments': {
                            'lat_src': 'start_lat',
                            'lon_src': 'start_lon',
                            'zoom': 18,
                            'dst': 'quadkey_start',
                        },
                        'operation_name': 'atlas::lonlat_keys_to_quadkey',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'set-quadkey-end',
                    'operation_variant': {
                        'arguments': {
                            'lat_src': 'end_lat',
                            'lon_src': 'end_lon',
                            'zoom': 18,
                            'dst': 'quadkey_end',
                        },
                        'operation_name': 'atlas::lonlat_keys_to_quadkey',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'set-city-name',
                    'operation_variant': {
                        'arguments': {'src': 'city_id', 'dst': 'city'},
                        'operation_name': 'atlas::wind_cities',
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'filter-fields-for-sink',
                    'operation_variant': {
                        'arguments': {
                            'leave_keys_list': [
                                'dttm_utc_1_min',  # DateTime,
                                'city',  # LowCardinality(String),
                                'ride_id',  # String
                                'updated_at',  # DateTime
                                'ts_1_min',  # UInt32
                                'status_code',  # UInt8
                                'ts_1_min_start',  # UInt32
                                'quadkey_start',  # String
                                'start_lat',  # Nullable(Float64)
                                'start_lon',  # Nullable(Float64)
                                'ts_1_min_end',  # UInt32
                                'quadkey_end',  # String
                                'end_lat',  # Nullable(Float64)
                                'end_lon',  # Nullable(Float64)
                                'success_flg',  # UInt8
                                'ride_lcy_cost',  # Float32
                                'city_id',  # UInt32 CODEC(ZSTD(1))
                            ],
                        },
                        'operation_name': 'filter_fields',
                        'type': 'mapper',
                    },
                },
            ],
        },
        'name': 'wind-board-rides',
    },
]


@pytest.mark.config(
    ORDER_EVENTS_PRODUCER_ATLAS_WIND_CITIES={
        '__default__': {'ru_name': 'Другое'},
        '1': {'en_name': 'Bad Vilbel'},
        '2': {'ru_name': 'Берлин', 'en_name': 'Berlin'},
    },
)
@pytest.mark.parametrize(
    'wind_data, expected_sink_event',
    [
        pytest.param(
            {
                'created_at': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-07-31T18:47:36.567000',
                },
                'city': 2,
                'rideId': 'bb02bf371e97',
                'updated_at': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-12-30T09:31:46.521025',
                },
                'status': 5,
                'ridingTime': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-07-31T18:47:38',
                },
                'startLatitude': 40.4264625,
                'startLongitude': -3.7010872,
                'completeTime': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-07-31T19:48:41',
                },
                'endLatitude': 40.4240084,
                'endLongitude': -3.682818,
                'unlockingTime': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-07-31T18:47:36',
                },
                'lockedTime': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-07-31T19:48:38',
                },
                'lockingTime': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-07-31T19:47:41',
                },
                'rideCost': 900,
            },
            {
                'city_id': 2,
                'city': 'Берлин',
                'dttm_utc_1_min': '2019-07-31T18:47:36',
                'end_lat': 40.4240084,
                'end_lon': -3.682818,
                'quadkey_end': '033111012132002132',
                'quadkey_start': '033111012123113000',
                'ride_id': 'bb02bf371e97',
                'ride_lcy_cost': 900,
                'start_lat': 40.4264625,
                'start_lon': -3.7010872,
                'status_code': 5,
                'success_flg': 1,
                'ts_1_min': 1564598856,
                'ts_1_min_end': 1564602521,
                'ts_1_min_start': 1564598858,
                'updated_at': '2019-12-30T09:31:46',
            },
            id='all data',
        ),
        pytest.param(
            {
                'created_at': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-07-31T18:47:36.567000',
                },
                'city': -1,
                'rideId': 'bb02bf371e97',
                'updated_at': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-12-30T09:31:46.521025',
                },
                'status': 5,
                'startLatitude': 40.4264625,
                'startLongitude': -3.7010872,
                'endLatitude': 40.4240084,
                'endLongitude': -3.682818,
                'rideCost': 900,
            },
            {
                'city_id': 0,
                'city': 'Другое',
                'dttm_utc_1_min': '2019-07-31T18:47:36',
                'end_lat': 40.4240084,
                'end_lon': -3.682818,
                'quadkey_end': '033111012132002132',
                'quadkey_start': '033111012123113000',
                'ride_id': 'bb02bf371e97',
                'ride_lcy_cost': 900,
                'start_lat': 40.4264625,
                'start_lon': -3.7010872,
                'status_code': 5,
                'success_flg': 0,
                'ts_1_min': 1564598856,
                'ts_1_min_end': 0,
                'ts_1_min_start': 0,
                'updated_at': '2019-12-30T09:31:46',
            },
            id='minimal data',
        ),
        pytest.param(
            {
                'created_at': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-07-31T18:47:36.567000',
                },
                'city': 2,
                'rideId': 'bb02bf371e97',
                'updated_at': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-12-30T09:31:46.521025',
                },
                'status': 5,
                'ridingTime': None,
                'startLatitude': 40.4264625,
                'startLongitude': -3.7010872,
                'completeTime': None,
                'endLatitude': 40.4240084,
                'endLongitude': -3.682818,
                'unlockingTime': None,
                'lockedTime': None,
                'lockingTime': None,
                'rideCost': 900,
            },
            {
                'city_id': 2,
                'city': 'Берлин',
                'dttm_utc_1_min': '2019-07-31T18:47:36',
                'end_lat': 40.4240084,
                'end_lon': -3.682818,
                'quadkey_end': '033111012132002132',
                'quadkey_start': '033111012123113000',
                'ride_id': 'bb02bf371e97',
                'ride_lcy_cost': 900,
                'start_lat': 40.4264625,
                'start_lon': -3.7010872,
                'status_code': 5,
                'success_flg': 0,
                'ts_1_min': 1564598856,
                'ts_1_min_end': 0,
                'ts_1_min_start': 0,
                'updated_at': '2019-12-30T09:31:46',
            },
            id='null time',
        ),
        pytest.param(
            {
                'created_at': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-07-31T18:47:36.567000',
                },
                'city': 1,
                'rideId': 'bb02bf371e97',
                'updated_at': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-12-30T09:31:46.521025',
                },
                'status': 5,
                'startLatitude': 40.4264625,
                'startLongitude': -3.7010872,
                'endLatitude': 40.4240084,
                'endLongitude': -3.682818,
                'rideCost': 900,
            },
            {
                'city_id': 1,
                'city': 'Bad Vilbel',
                'dttm_utc_1_min': '2019-07-31T18:47:36',
                'end_lat': 40.4240084,
                'end_lon': -3.682818,
                'quadkey_end': '033111012132002132',
                'quadkey_start': '033111012123113000',
                'ride_id': 'bb02bf371e97',
                'ride_lcy_cost': 900,
                'start_lat': 40.4264625,
                'start_lon': -3.7010872,
                'status_code': 5,
                'success_flg': 0,
                'ts_1_min': 1564598856,
                'ts_1_min_end': 0,
                'ts_1_min_start': 0,
                'updated_at': '2019-12-30T09:31:46',
            },
            id='city en fallback',
        ),
        pytest.param(
            {
                'created_at': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-07-31T18:47:36.567000',
                },
                'rideId': 'bb02bf371e97',
                'updated_at': {
                    '$a': {'raw_type': 'datetime'},
                    '$v': '2019-12-30T09:31:46.521025',
                },
                'status': 5,
                'startLatitude': 40.4264625,
                'startLongitude': -3.7010872,
                'endLatitude': 40.4240084,
                'endLongitude': -3.682818,
                'rideCost': 900,
            },
            {
                'city_id': 0,
                'city': 'Другое',
                'dttm_utc_1_min': '2019-07-31T18:47:36',
                'end_lat': 40.4240084,
                'end_lon': -3.682818,
                'quadkey_end': '033111012132002132',
                'quadkey_start': '033111012123113000',
                'ride_id': 'bb02bf371e97',
                'ride_lcy_cost': 900,
                'start_lat': 40.4264625,
                'start_lon': -3.7010872,
                'status_code': 5,
                'success_flg': 0,
                'ts_1_min': 1564598856,
                'ts_1_min_end': 0,
                'ts_1_min_start': 0,
                'updated_at': '2019-12-30T09:31:46',
            },
            id='no city id',
        ),
    ],
)
async def test_atlas_sink(
        taxi_order_events_producer,
        testpoint,
        wind_data,
        expected_sink_event,
        taxi_config,
        taxi_eventus_orchestrator_mock,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('clickhouse-sink-sender::atlas_wind_order')
    def sink_write(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, _OEP_PIPELINES_FOR_ORCH,
    )

    await taxi_order_events_producer.run_task('invalidate-seq_num')

    lb_message = {'data': json.dumps(wind_data)}

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'wind-board-rides',
                'data': json.dumps(lb_message),
                'topic': 'smth',
                'cookie': 'cookie_for_atlas_sink',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_atlas_sink'

    events = (await sink_write.wait_call())['data']

    assert events == [expected_sink_event]
