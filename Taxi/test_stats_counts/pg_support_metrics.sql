INSERT INTO events.aggregated_stat
 (id, source, created_ts, sent, stat, stat_interval, name)
VALUES
  (
    'stat_1', 'chatterbox', '2019-07-02 12:00:01.00000+03', FALSE,
    ('{"login":"superuser", "action":"create", "line":"first_line",' ||
     '"new_line": "null", "in_addition": "1", "count": 1}')::JSONB,
    '1min', null
  ),
  (
    'stat_2', 'chatterbox', '2019-07-02 15:00:02.000000+06', FALSE,
    ('{"login":"null", "action":"create", "line":"first_line",' ||
     '"new_line": "second", "in_addition": "0", "count": 2}')::JSONB,
    '1min', 'create_by_line_calculator'
  ),
  (
    'stat_3', 'chatterbox', '2019-07-02 12:00:00.000000+03', FALSE,
    ('{"login":"null", "action":"create", "line":"first_line",' ||
     '"new_line": "second", "in_addition": "0", "count": 4}')::JSONB,
    '1hour', 'create_by_line_calculator'
  ),
  (
    'stat_4', 'chatterbox', '2019-06-15 00:00:02.000000+03', FALSE,
    ('{"login":"null", "action":"create", "line":"first_line",' ||
     '"new_line": "second", "in_addition": "0", "count": 8}')::JSONB,
    '1min', 'create_by_line_calculator'
  ),
  (
    'stat_5', 'chatterbox', '2019-07-02 00:00:02.000000+03', FALSE,
    ('{"login":"toert", "action":"create", "line":"null",' ||
     '"new_line": "second", "in_addition": "0", "count": 16.0}')::JSONB,
    '1min', 'supporter_sla'
  ),
  (
    'stat_6', 'chatterbox', '2019-07-03 00:00:00.000000+03', FALSE,
    ('{"login":"null", "action":"create", "line":"first_line",' ||
     '"new_line": "second", "in_addition": "0", "count": 32}')::JSONB,
    '1min', 'create_by_line_calculator'
  ),
  (
    'stat_7', 'chatterbox', '2019-07-03 00:00:01.000000+03', FALSE,
    ('{"login":"null", "action":"create", "line":"first_line",' ||
     '"new_line": "second", "in_addition": "0", "count": 64}')::JSONB,
    '1min', 'create_by_line_calculator'
  )
;
