INSERT INTO archiving.rules as rules
(
    rule_name,
    group_name,
    source_type,
    ttl_info,
    period,
    sleep_delay,
    task_info
)
VALUES
(
    'test_foo_1', 'foo', 'bar',
    '{"duration_default": 100, "field": "updated"}'::jsonb,
    300, 2, null
),
(
    'test_foo_2', 'foo', 'bar',
    '{"duration_default": 100, "field": "updated"}'::jsonb,
    300, 2, null
),
(
    'test_foo_3', 'foo', 'bar',
    '{"duration_default": 100, "field": "updated"}'::jsonb,
    300, 2, null
),
(
    'test_abc', 'abc', 'bar',
    '{"duration_default": 123, "field": "updated"}'::jsonb,
    300, 2, null
);

INSERT INTO archiving.last_run
(
    rule_name,
    shard_alias,
    last_run
)
VALUES
(
    'test_foo_1',
    '_no_shards',
    '[]'::jsonb
),
(
    'test_foo_2',
    '_no_shards',
    '[{
        "task_id": "test_link",
        "removed": 24,
        "status": "in_progress",
        "start_time": "2019-01-01T06:00:00+03:00",
        "sync_time": "2019-01-01T09:00:00+03:00"
    }]'::jsonb
),
(
    'test_abc',
    '_no_shards',
    '[{
        "task_id": "test_link1",
        "removed": 2031,
        "status": "finished",
        "start_time": "2019-01-01T06:00:00+03:00",
        "sync_time": "2019-01-01T09:00:00+03:00"
      }, {
        "task_id": "test_link2",
        "removed": 2031,
        "status": "finished",
        "start_time": "2019-01-01T06:00:00+03:00",
        "sync_time": "2019-01-01T10:00:00+03:00"
      }, {
        "task_id": "test_link3",
        "removed": 20312,
        "status": "exception",
        "start_time": "2019-01-01T06:00:00+03:00",
        "sync_time": "2019-01-01T11:00:00+03:00"
      }, {
        "task_id": "test_link4",
        "removed": 244,
        "status": "finished",
        "start_time": "2019-01-01T06:00:00+03:00",
        "sync_time": "2019-01-01T12:00:00+03:00"
      }, {
        "task_id": "test_link5",
        "removed": 2134,
        "status": "finished",
        "start_time": "2019-01-01T06:00:00+03:00",
        "sync_time": "2019-01-01T13:00:00+03:00"
      }]'::jsonb
);
