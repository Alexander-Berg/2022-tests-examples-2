INSERT INTO state.providers (id, name, description, active)
VALUES (1000, '1000_active', 'initially active', True),
       (1001, '1001_disabled', 'initially disabled', False),
       (1002, '[1002_]active_with_bad_name! ', 'initially active', True);

INSERT INTO meta.tag_names (id, name)
VALUES (1000, 'tag_name_1000'),
       (1001, 'tag_name_1001'),
       (1002, 'tag_name_1002_financial');

INSERT INTO meta.topics (id, name, description, is_financial)
VALUES (10, 'topic_10', 'probably audited topic', False),
       (20, 'topic_20_financial', 'financial', True);

INSERT INTO meta.relations (topic_id, tag_name_id)
VALUES (10, 1000),
       (20, 1002);

INSERT INTO service.queries
(name, provider_id, entity_type, tags, author, last_modifier, enabled,
 changed, created, period, query, syntax)
VALUES ('1000_active', 1000, 'dbid_uuid', '{"tag_name_1000", "tag_name_1001"}',
        'author', 'author', True, '2018-02-26 19:11:13 +03:00',
        '2018-02-26 19:11:13 +03:00', '3600 seconds', 'SELECT * FROM table;',
        'SQLv1'),
       ('[1002_]active_with_bad_name! ', 1002, 'dbid_uuid',
        '{"tag_name_1000", "tag_name_1001"}',
        'author', 'author', True, '2018-02-26 19:11:13 +03:00',
        '2018-02-26 19:11:13 +03:00', '3600 seconds', 'SELECT * FROM table;',
        'SQLv1');
