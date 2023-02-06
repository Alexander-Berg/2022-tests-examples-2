INSERT INTO state.providers (id, name, description, active)
VALUES
       (1000, '1000_active', 'initially active', True),
       (1001, '1001_disabled', 'initially disabled', False),
       (1002, '1002_financial', 'financial active provider', True),
       (1003, '1003_active', 'initially active', True),
       (1004, '1004_with_custom_execution_time', 'bahnlhale', True),
       (1005, '1005_no_placeholder', 'test placeholder', True),
       (1006, '1006_driver_license', 'active query with deprecated entity_type', True),
       (1007, '1007_dynamic_entity_types', '', True),
       (1008, '1008_clickhouse', '', True),
       (1009, '1009_ticket', '', True),
       (1010, '1010_tags_limited', '', True);

INSERT INTO meta.tag_names (id, name)
VALUES
    (1000, 'tag_name_1000'),
    (1001, 'tag_name_1001'),
    (1002, 'tag_name_1002_financial');

INSERT INTO meta.topics (id, name, description, is_financial)
VALUES
    (10, 'topic_10', 'usual topic', False),
    (20, 'topic_20_financial', 'financial', True);

INSERT INTO meta.relations (topic_id, tag_name_id)
VALUES
    (10, 1000),
    (20, 1002);

INSERT INTO service.queries
    (name, provider_id, entity_type, tags, author, last_modifier, enabled,
     changed, created, period, query, syntax, custom_execution_time, yql_processing_method,
     ticket, tags_limit)
VALUES
    ('1000_active', 1000, 'dbid_uuid', '{"tag_name_1000", "tag_name_1001"}',
     'author', 'author', True, '2018-02-26 19:11:13 +03:00',
     '2018-02-26 19:11:13 +03:00', '3600 seconds', '[_INSERT_HERE_] SELECT * FROM table;',
     'SQLv1', NULL, 'yt_merge', 'TASKTICKET-123', 100),
    ('1001_disabled', 1001, 'dbid_uuid', '{}',
     'author', 'author', True, '2018-02-26 19:11:13 +03:00',
     '2018-02-26 19:11:13 +03:00', '3600 seconds', '[_INSERT_HERE_] SELECT * FROM table;',
     'SQL', NULL, 'yt_merge', 'TASKTICKET-123', 100),
    ('1002_financial', 1002, 'dbid_uuid',
     '{"tag_name_1000", "tag_name_1002_financial"}',
     'author', 'author', True, '2018-02-26 19:11:13 +03:00',
     '2018-02-26 19:11:13 +03:00', '3600 seconds', '[_INSERT_HERE_] SELECT * FROM table;',
     'SQLv1', NULL, 'yt_merge', 'TASKTICKET-123', 100),
    ('beautiful_query_name', 1003, 'dbid_uuid', '{"tag_name_1000", "tag_name_1001"}',
     'author', 'author', True, '2018-02-26 19:11:13 +03:00',
     '2018-02-26 19:11:13 +03:00', '3600 seconds', '[_INSERT_HERE_] SELECT * FROM table;',
     'SQLv1', NULL, 'yt_merge', 'TASKTICKET-123', 100),
    ('query_with_custom_execution_time', 1004, 'dbid_uuid', '{"tag_name_1000", "tag_name_1001"}',
     'author', 'author', True, '2018-02-26 19:11:13 +03:00',
     '2018-02-26 19:11:13 +03:00', '3600 seconds', '[_INSERT_HERE_] SELECT * FROM table;',
     'SQLv1', '2118-02-26 19:11:13 +03:00', 'yt_merge', 'TASKTICKET-123', 100),
    ('query_without_placeholder', 1005, 'dbid_uuid', '{"tag_name_1000", "tag_name_1001"}',
     'author', 'author', True, '2018-02-26 19:11:13 +03:00',
     '2018-02-26 19:11:13 +03:00', '3600 seconds', 'SELECT * FROM table;',
     'SQLv1', NULL, 'in_place', 'TASKTICKET-123', 100),
    ('query_with_driver_license', 1006, 'driver_license', '{"tag_name_1000", "tag_name_1001"}',
     'author', 'author', True, '2018-02-26 19:11:13 +03:00',
     '2018-02-26 19:11:13 +03:00', '3600 seconds', '[_INSERT_HERE_] SELECT * FROM table;',
     'SQLv1', NULL, 'yt_merge', 'TASKTICKET-123', 100),
    ('dynamic_entity_types', 1007, NULL, '{}', 'author', 'author', True,
     '2018-02-26 19:11:13 +03:00', '2018-02-26 19:11:13 +03:00', '3600 seconds',
     '[_INSERT_HERE_] SELECT * FROM table;', 'SQLv1', NULL, 'yt_merge',
     'TASKTICKET-123', 100),
    ('clickhouse_query', 1008, 'dbid_uuid', '{}', 'author', 'author', True,
     '2018-02-26 19:11:13 +03:00', '2018-02-26 19:11:13 +03:00', '3600 seconds',
     '[_INSERT_HERE_] SELECT * FROM table;', 'CLICKHOUSE', NULL, 'yt_merge',
     'TASKTICKET-123', NULL),
    (' no_ticket_query"with]bad!name ', 1009, 'dbid_uuid', '{"tag_name_1000", "tag_name_1001"}',
     'author', 'author', True, '2018-02-26 19:11:13 +03:00',
     '2018-02-26 19:11:13 +03:00', '3600 seconds', '[_INSERT_HERE_] SELECT * FROM table;',
     'SQLv1', NULL, 'yt_merge', NULL, 100);
