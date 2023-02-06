INSERT INTO events.aggregated_stat
 (id, source, created_ts, sent, stat, stat_interval, name)
VALUES
  (
    'stat_1', 'chatterbox', '2019-07-02 12:00:01.00000+03', FALSE,
    ('{"login":"superuser", "action":"first_accept", "line":"first_line",' ||
     '"new_line": "null", "in_addition": "1", "count": 1}')::JSONB,
    '1min', null
  ),
  (
    'stat_2', 'chatterbox', '2019-07-02 15:00:02.000000+06', FALSE,
    ('{"login":"null", "action":"forward", "line":"first_line",' ||
     '"new_line": "second", "in_addition": "0", "count": 2}')::JSONB,
    '1min', 'create_by_line_calculator'
  ),
  (
    'stat_3', 'chatterbox', '2019-07-02 12:00:00.000000+03', FALSE,
    ('{"login":"null", "action":"forward", "line":"first_line",' ||
     '"new_line": "second", "in_addition": "0", "count": 3}')::JSONB,
    '1hour', 'create_by_line_calculator'
  ),
  (
    'stat_4', 'chatterbox', '2019-06-15 00:00:02.000000+03', FALSE,
    ('{"login":"null", "action":"forward", "line":"first_line",' ||
     '"new_line": "second", "in_addition": "0", "count": 4}')::JSONB,
    '1min', 'create_by_line_calculator'
  ),
  (
    'stat_5', 'chatterbox', '2019-07-02 00:00:02.000000+03', FALSE,
    ('{"login":"toert", "action":"forward", "line":"null",' ||
     '"new_line": "second", "in_addition": "0", "count": 5.0}')::JSONB,
    '1min', 'supporter_sla'
  ),
  (
    'stat_6', 'chatterbox', '2019-07-03 00:00:00.000000+03', FALSE,
    ('{"login":"null", "action":"forward", "line":"first_line",' ||
     '"new_line": "second", "in_addition": "0", "count": 6}')::JSONB,
    '1day', 'create_by_line_calculator'
  ),
  (
    'stat_7', 'chatterbox', '2019-07-03 00:00:01.000000+03', FALSE,
    ('{"login":"null", "action":"forward", "line":"first_line",' ||
     '"new_line": "second", "in_addition": "0", "count": 7}')::JSONB,
    '1min', 'create_by_line_calculator'
  ),
  (
      'stat_8', 'chatterbox', '2019-07-02 00:00:01.000000+03', FALSE,
      ('{"line":"telephony", "action":"success_call", "count": 8,' ||
       '"params": {"lower_limit": 20, "upper_limit": 5}}')::JSONB,
      '1hour', 'ivr_success_calls_by_line_calculator'
  ),
  (
      'stat_9', 'chatterbox', '2019-07-02 00:01:01.000000+03', FALSE,
      ('{"line":"telephony", "action":"success_call", "count": 9,' ||
       '"lower_limit": 10}')::JSONB,
      '1hour', 'ivr_success_calls_by_line_calculator'
  ),
  (
      'stat_10', 'chatterbox', '2019-07-02 00:01:01.000000+03', FALSE,
      ('{"line":"telephony2", "action":"success_call", "count": 10,' ||
       '"lower_limit": 10}')::JSONB,
      '1hour', 'ivr_success_calls_by_line_calculator'
  ),
  (
      'stat_11', 'chatterbox', '2019-07-02 00:01:01.000000+03', FALSE,
      ('{"line":"telephony", "action":"missed_call", "count": 11,' ||
       '"lower_limit": 10}')::JSONB,
      '1hour', 'ivr_missed_calls_by_line_calculator'
  ),
  (
      'stat_12', 'chatterbox', '2019-07-01 00:01:01.000000+03', FALSE,
      ('{"line":"telephony2", "action":"missed_call", "count": 12,' ||
       '"upper_limit": 10}')::JSONB,
      '1hour', 'ivr_missed_calls_by_line_calculator'
  );
