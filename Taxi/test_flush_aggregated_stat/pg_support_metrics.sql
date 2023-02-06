INSERT INTO events.aggregated_stat
 (id, source, created_ts, sent, stat, stat_interval, name)
VALUES
  (
    'stat_min_1', 'chatterbox', '2019-07-01 12:00:01.000000+00', FALSE,
    ('{"login":"superuser", "action":"create", "line":"first",' ||
     '"new_line": "null", "in_addition": "1", "count": 25}')::JSONB, '1min', 'name_1'
  ),
  (
    'stat_min_2', 'chatterbox', '2019-07-02 12:00:02.000000+00', FALSE,
    ('{"login":"support_1", "action":"forward", "line":"first",' ||
     '"new_line": "second", "in_addition": "0", "count": 22}')::JSONB, '1min', 'name_2'
  ),
  (
    'stat_hour_1', 'chatterbox', '2019-07-03 12:00:03.000000+00', FALSE,
    ('{"login":"support_2", "action":"close", "line":"first",' ||
     '"new_line": "null", "in_addition": "0", "count": 32}')::JSONB, '1hour', 'name_1'
  ),
  (
    'stat_hour_2', 'chatterbox', '2019-07-04 12:00:04.000000+00', TRUE,
    ('{"login":"superuser", "action":"create", "line":"first",' ||
     '"new_line": "null", "in_addition": "1", "count": 22}')::JSONB, '1hour', 'name_2'
  )
;
