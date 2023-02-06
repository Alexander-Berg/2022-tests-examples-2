INSERT INTO state.providers (id, name, description, active)
VALUES
    (0, 'ordinary_query', '', true),
    (1, 'running_query', '', true),
    (2, 'disabled_query', '', true),
    (3, 'scheduled_query', '', true);

INSERT INTO service.queries
    (name, provider_id, entity_type, tags, author, last_modifier, enabled,
    changed, created, period, query, syntax, custom_execution_time, yql_processing_method)
VALUES
    ('ordinary_query', 0, 'dbid_uuid', ARRAY['developer']::varchar[], 'ivanov', 'ivanov', true,
     '2020-08-22T12:34:56'::timestamp, '2018-08-22T02:34:56'::timestamp,
      '3000 days'::interval, '[_INSERT_HERE_]', 'SQLv1', null, 'yt_merge'),
    ('running_query', 1, 'dbid_uuid', ARRAY['developer']::varchar[], 'ivanov', 'ivanov', true,
     '2020-08-22T12:34:56'::timestamp, '2018-08-22T02:34:56'::timestamp,
     '3000 days'::interval, '[_INSERT_HERE_]', 'SQLv1', null, 'yt_merge'),
    ('disabled_query', 2, 'dbid_uuid', ARRAY['developer']::varchar[], 'ivanov', 'ivanov', false,
     '2020-08-22T12:34:56'::timestamp, '2018-08-22T02:34:56'::timestamp,
     '3000 days'::interval, '[_INSERT_HERE_]', 'SQLv1', null, 'yt_merge'),
    ('scheduled_query', 3, 'dbid_uuid', ARRAY['developer']::varchar[], 'ivanov', 'ivanov', true,
     '2020-08-22T03:34:56'::timestamp, '2018-08-22T02:34:56'::timestamp,
     '3000 days'::interval, '[_INSERT_HERE_]', 'SQLv1', '2020-11-03T23:59:59'::timestamp, 'yt_merge');

INSERT into service.yql_operations
    (operation_id, provider_id, entity_type, status, started, failure_type, failure_description)
VALUES
    ('5d92fb9b9dee76d0a1e0a72f', 0, 'dbid_uuid', 'completed', '2020-11-02T11:34:56'::timestamp, null, null),
    ('5d92f9b9095c4eba55cd0013', 1, 'dbid_uuid', 'running', '2020-11-02T12:34:50'::timestamp, null, null);
