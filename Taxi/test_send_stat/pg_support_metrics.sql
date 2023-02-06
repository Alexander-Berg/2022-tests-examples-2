INSERT INTO events.aggregated_stat
 (id, source, created_ts, sent, stat)
VALUES
  (
    'stat_1', 'chatterbox', '2019-07-02 12:00:01.000000+00', FALSE,
    ('{"login":"superuser", "action":"create", "line":"first",' ||
     '"new_line": "null", "in_addition": "1", "count": 25}')::JSONB
  ),
  (
    'stat_2', 'chatterbox', '2019-07-02 12:00:02.000000+00', FALSE,
    ('{"login":"support_1", "action":"forward", "line":"first",' ||
     '"new_line": "second", "in_addition": "0", "count": 22}')::JSONB
  ),
  (
    'stat_3', 'chatterbox', '2019-07-02 12:00:03.000000+00', FALSE,
    ('{"login":"support_2", "action":"close", "line":"first",' ||
     '"new_line": "null", "in_addition": "0", "count": 32}')::JSONB
  ),
  (
    'stat_4', 'chatterbox', '2019-07-02 12:00:04.000000+00', TRUE,
    ('{"login":"superuser", "action":"create", "line":"first",' ||
     '"new_line": "null", "in_addition": "1", "count": 22}')::JSONB
  )
;
