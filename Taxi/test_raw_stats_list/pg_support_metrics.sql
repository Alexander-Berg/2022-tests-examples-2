INSERT INTO events.aggregated_stat
 (id, source, created_ts, sent, stat, stat_interval, name)
VALUES
  (
    'stat_1', 'chatterbox', '2019-07-02 21:00:00.00000z', FALSE,
    ('{"login":"superuser", "action":"sip_call", "line":"first_line",' ||
     '"count": 1}')::JSONB,
    '1day', 'sip_calls_calculator'
  ),
  (
    'stat_2', 'chatterbox', '2019-07-02 21:00:00.00000z', FALSE,
    ('{"login":"superuser", "action":"success_call", "line":"first_line",' ||
     '"count": 1, "avg_duration": 60}')::JSONB,
    '1day', 'sip_success_calls_calculator'
  ),
  (
    'stat_3', 'chatterbox', '2019-07-03 21:00:00.00000z', FALSE,
    ('{"login":"superuser", "action":"sip_call", "line":"first_line",' ||
     '"count": 1}')::JSONB,
    '1day', 'sip_calls_calculator'
  ),
  (
    'stat_4', 'chatterbox', '2019-07-03 21:00:00.00000z', FALSE,
    ('{"login":"superuser", "action":"success_call", "line":"first_line",' ||
     '"count": 1, "avg_duration": 60}')::JSONB,
    '1day', 'sip_success_calls_calculator'
  ),
  (
    'stat_5', 'chatterbox', '2019-07-03 21:00:00.00000z', FALSE,
    ('{"login":"user", "action":"success_call", "line":"second_line",' ||
     '"count": 1, "avg_duration": 60}')::JSONB,
    '1day', 'sip_success_calls_calculator'
  ),
  (
    'stat_6', 'chatterbox', '2019-07-03 21:00:00.00000z', FALSE,
    ('{"login":"user", "action":"success_call", "line":"first_line",' ||
     '"count": 1, "avg_duration": 60}')::JSONB,
    '1day', 'sip_success_calls_calculator'
  ),

  ('stat_7', 'chatterbox', '2019-07-03 21:00:00.00000z', FALSE,
   ('{"line":"first", "action":"chatterbox_line_backlog",' ||
   '"projects":["taxi"],' ||
    '"average_counts": {"new": 5, "reopen": 2}}')::JSONB,
   '1day', 'backlog_average_by_line_and_status'
   ),
   ('stat_8', 'chatterbox', '2019-07-03 21:00:00.00000z', FALSE,
   ('{"line":"first", "action":"chatterbox_line_backlog",' ||
   '"projects":["taxi", "eats"], ' ||
    '"average_counts": {"new": 7, "reopen": 3.5}}')::JSONB,
   '1min', 'backlog_average_by_line_and_status'
   ),
   ('stat_9', 'chatterbox', '2019-07-05 21:05:00.00000z', FALSE,
   ('{"line":"newest", "action":"chatterbox_line_backlog",' ||
   '"projects":["taxi"],' ||
    '"average_counts": {"new": 10.0, "reopen": 10.0}}')::JSONB,
   '1min', 'backlog_average_by_line_and_status'
   ),
   ('stat_10', 'chatterbox', '2019-07-05 21:05:00.00000z', FALSE,
   ('{"line":"newest_2", "action":"chatterbox_line_backlog",' ||
   '"projects":["taxi"],' ||
    '"average_counts": {"new": 15.0, "reopen": 10.0}}')::JSONB,
   '1min', 'backlog_average_by_line_and_status'
   ),
   ('stat_11', 'chatterbox', '2019-07-05 21:03:00.00000z', FALSE,
   ('{"line":"latecomer", "action":"chatterbox_line_backlog",' ||
   '"projects":["taxi"],' ||
    '"average_counts": {"new": 100.0, "reopen": 100.0}}')::JSONB,
   '1min', 'backlog_average_by_line_and_status'
   ),
   ('stat_12', 'chatterbox', '2019-07-05 21:01:00.00000z', FALSE,
   ('{"line":"latecomer_2", "action":"chatterbox_line_backlog",' ||
   '"projects":["taxi"],' ||
    '"average_counts": {"new": 1000.0, "reopen": 1000.0}}')::JSONB,
   '1min', 'backlog_average_by_line_and_status'
   )
;
