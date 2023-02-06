INSERT INTO approvals_schema.drafts (
  created_by, comments, created, updated, description, approvals,
  status, version, request_id, run_manually, service_name,
  api_path, data, change_doc_id, apply_time, mode, tickets, summary,
  deferred_apply, reminded, date_expired
) VALUES (
    'test_user', '{}', '2017-10-01T01:10:00'::timestamp,
    '2017-11-01T01:10:00'::timestamp, 'test', '[]', 'approved', 1, '123',
    FALSE, 'test_service', 'test_api', '{"test_key": "test_value"}', '234',
    '2017-11-01T01:10:00'::timestamp, 'push', '["TAXIRATE-35"]', '{}',
    '2017-11-01T01:10:00'::timestamp, null::timestamp, '2018-01-01T01:10:00'::timestamp
  ),
  (
    'test_user', '{}', '2017-11-01T01:10:00'::timestamp,
    '2017-11-01T01:10:00+0300', 'test', '[]', 'waiting_check', 1, '124',
    FALSE, 'test_service', 'test_api', '{"test_key": "test_value"}', '235',
    null::timestamp, 'push', '["TAXIRATE-35"]', '{}',
    null::timestamp, null::timestamp, '2018-01-01T01:10:00'::timestamp
  );
