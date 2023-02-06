insert into test_data
    (test_id, description, schema_id, start_time, precedent_time,
     end_time, data, meta)
values
(1, 'description 1', 'test_schema_id',
 '2020-10-02 12:00:00.000000'::TIMESTAMPTZ,
 '2020-10-02 12:02:30.000000'::TIMESTAMPTZ,
 '2020-10-02 12:05:00.000000'::TIMESTAMPTZ,
 $$[
 {
    "timeseries": {
        "values": [1, 1, 1, 1],
        "timestamps": [
            1601640000000,
            1601640180000,
            1601640270000,
            1601640300000
        ]
    },
    "entry_point_id": "entry"
 }]$$::JSONB, $${}$$::JSON),
(3, 'description 2', 'test_schema_id_7',
 '2020-10-02 12:00:00.000000'::TIMESTAMPTZ,
 '2020-10-02 12:02:30.000000'::TIMESTAMPTZ,
 '2020-10-02 12:05:00.000000'::TIMESTAMPTZ,
 $$[
   {
     "timeseries": {
       "values": [1, 1, 1, 1],
       "timestamps": [
         1601640000000,
         1601640180000,
         1601640270000,
         1601640300000
       ]
     },
     "entry_point_id": "entry"
   }]$$::JSONB, $${}$$::JSON);

insert into test_cases
    (id, description, test_data_id, schema_id, out_point_id, start_time,
     end_time, check_type, check_params, is_enabled)
values
(default, '1 worst_state passed', 1,
 'test_schema_id', 'alert',
 '2020-10-02 12:00:00.000000'::TIMESTAMPTZ,
 '2020-10-02 12:02:30.000000'::TIMESTAMPTZ,
 'worst_state',
 $${"worst_state": "Critical"}$$::JSONB, true),
(default, '2 worst_state failed', 1,
 'test_schema_id', 'alert',
 '2020-10-02 12:00:00.000000'::TIMESTAMPTZ,
 '2020-10-02 12:00:30.000000'::TIMESTAMPTZ,
 'worst_state',
 $${"worst_state": "Warning",
     "should_reach_worst_state": true}$$::JSONB, true),
(
 default, '3 last_state passed', 1,
 'test_schema_id', 'alert',
 '2020-10-02 12:03:00.000000'::TIMESTAMPTZ,
 '2020-10-02 12:05:00.000000'::TIMESTAMPTZ,
 'last_state',
 $${"last_state": "Ok"}$$::JSONB, true),
(default,'4 disabled test object', 1,
 'test_schema_id_3', 'alert',
 '2020-10-02 14:53:00.000000'::TIMESTAMPTZ,
 '2020-10-02 16:54:00.000000'::TIMESTAMPTZ,
 'last_state',
 $${"worst_state": "Ok"}$$::JSONB, false),
(default,'5 wrong test object', 1,
 'test_schema_id_2', 'alert',
 '2020-10-02 14:53:00.000000'::TIMESTAMPTZ,
 '2020-10-02 16:54:00.000000'::TIMESTAMPTZ,
 'last_state',
 $${"worst_state": "Ok"}$$::JSONB, true),
(default,'6 no test data for that test', 2,
 'test_schema_id', 'alert',
 '2020-10-02 14:53:00.000000'::TIMESTAMPTZ,
 '2020-10-02 16:54:00.000000'::TIMESTAMPTZ,
 'last_state',
 $${"worst_state": "Ok"}$$::JSONB, true),
(default, '7 has_state passed', 3,
 'test_schema_id_7', 'alert',
 '2020-10-02 12:00:00.000000'::TIMESTAMPTZ,
 '2020-10-02 12:01:30.000000'::TIMESTAMPTZ,
 'has_alert',
 $${}$$::JSONB, true)
