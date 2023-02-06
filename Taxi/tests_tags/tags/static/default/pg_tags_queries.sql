INSERT INTO state.providers (id, name, description, active)
VALUES
(0, 'first_name', '', true),
(1, 'c5c97dfb70404435a6ba4a57', '', true),
(2, '3f4d6a2d929d4377ac3060c3', '', true),
(3, '6f9492477dda43fc9a36647a', '', true),
(4, 'dynamic_query', '', true),
(5, '489f019592ce4cf69184073e', '', true);

--INSERT INTO service.requests VALUES ();

SELECT setval('state.providers_id_seq', max_id)
FROM (SELECT max(id) max_id FROM state.providers) subquery;

INSERT INTO service.queries
    (name, provider_id, entity_type, tags, author, last_modifier, enabled,
    changed, created, period, query, syntax, custom_execution_time, disable_at,
    ticket, tags_limit)
VALUES
    ('first_name', 0, 'user_id', ARRAY['developer', 'yandex']::varchar[], 'иванов',
     'иванов', false, '2018-08-30T12:34:56'::timestamp,
     '2018-08-22T02:34:56'::timestamp, '1 minute'::interval, 'query text',
     'SQL', NULL, NULL, NULL, NULL),
    ('name_extended', 1, 'udid', ARRAY[]::varchar[], 'ivanov', 'ivanov', false,
     '2018-08-25T12:34:57'::timestamp, '2018-08-22T02:34:56'::timestamp,
     '10 minutes'::interval, 'select * from abc', 'SQL', NULL, NULL, NULL, NULL),
    ('nayme_with_error', 2, 'dbid_uuid', ARRAY[]::varchar[], 'ivanov', 'ivanov', false,
     '2018-08-22T12:34:56'::timestamp, '2018-08-22T02:34:56'::timestamp,
     '20 minutes'::interval, 'select * from abc', 'SQLv1', NULL, NULL, NULL, NULL),
    ('surname_not_last', 3, 'car_number', ARRAY[]::varchar[], 'ivanov', 'petrov', true,
     '2018-08-22T03:34:56'::timestamp, '2018-08-22T02:34:56'::timestamp,
     '30 minutes'::interval, 'select * from abc', 'SQLv1', NULL, NULL, NULL, NULL),
    ('the_last_dynamic_query', 4, NULL, ARRAY[]::varchar[], 'ivanov', 'petrov', true,
     '2018-08-22T02:35:56'::timestamp, '2018-08-22T02:34:56'::timestamp,
     '59 minutes'::interval, 'select * from abc', 'SQLv1', NULL, NULL, NULL, NULL),
    ('the_last_name', 5, 'park', ARRAY[]::varchar[], 'ivanov', 'petrov', true,
     '2018-08-22T02:34:56'::timestamp, '2018-08-22T02:34:56'::timestamp,
     '1 hour'::interval, 'original query', 'SQL', '2018-08-22T03:00:00'::timestamp,
     '2018-08-23T09:00:00'::timestamp, 'TASKTICKET-1234', 2000);

INSERT into service.yql_operations 
    (operation_id, provider_id, entity_type, status, started, failure_type, failure_description, total_count, added_count, removed_count, malformed_count)
VALUES
    ('5d92fb9b9dee76d0a1e0a72f', 0, 'user_id', 'completed', '2018-08-22T02:34:56'::timestamp, NULL, NULL, 8, 5, 4, 0),
    ('5d92f9b9095c4eba55cd0013', 2, 'dbid_uuid', 'completed', '2018-08-22T02:40:56'::timestamp, NULL, NULL, 9, 3, 7, 3),
    ('5d92f8149dee76d0a1e0a60b', 0, 'user_id', 'failed', '2018-08-22T02:35:56'::timestamp, 'execution_failed', 'failed to process operation: no dbid_uuid', NULL, NULL, NULL, NULL),
    ('5d92fa319dee76d0a1e0a6d3', 2, 'dbid_uuid', 'completed', '2018-08-22T03:00:56'::timestamp, NULL, NULL, 1, 0, 0, 0),
    ('5d92f63153f354d3cdf42a4a', 3, 'car_number', 'completed', '2018-08-22T02:34:56'::timestamp, NULL, NULL, 6, 4, 0, 4),
    ('5d92f79b9f4b9eac6652cf6e', 3, 'car_number', 'failed', '2018-08-22T03:04:56'::timestamp, 'bad_response_format', 'operation failed: ERROR', NULL, NULL, NULL, NULL),
    ('5d92f414095c4eba55ccfe48', 1, 'udid', 'completed', '2018-08-22T02:34:56'::timestamp, NULL, NULL, 8, 0, 0, 3),
    ('5d92f9b968a6f554a5a8fbb3', 0, 'user_id', 'running', '2018-08-22T02:36:56'::timestamp, NULL, NULL, NULL, NULL, NULL, NULL),
    ('5d92f9b968a6f554a5a8fbee', 0, 'user_id', 'aborted', '2018-08-22T02:37:56'::timestamp, NULL, NULL, NULL, NULL, NULL, NULL),
    ('5d92f79b9f4b9eac6652cf6f', 4, NULL, 'failed', '2018-08-22T03:14:56'::timestamp, 'bad_entity_types', 'operation failed: following entity_types in service=tags are invalid: [not_entity_type]', NULL, NULL, NULL, NULL);
