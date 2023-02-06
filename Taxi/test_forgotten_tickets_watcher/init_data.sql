INSERT INTO approvals_schema.drafts (
  created_by, comments, created, updated, description, approvals,
  status, version, request_id, run_manually, service_name,
  api_path, data, change_doc_id, apply_time, mode, tickets, summary,
  deferred_apply, is_multidraft, multidraft_id
) VALUES (
  'test_user', '[]',
  '2017-11-01T01:10:00'::timestamp, '2017-11-01T01:10:00'::timestamp, 'test',
  '[]', 'approved', 1, '123', FALSE, 'test_service', 'test_api',
  '{"test_key": "test_value"}', '234', '2017-11-01T01:10:00'::timestamp,
  'push', '[]', '{}', '2017-11-01T01:10:00'::timestamp, false, null::integer
  ), (
  'test_user2', '[]',
  '2017-11-01T01:10:00'::timestamp, '2017-11-01T01:10:00'::timestamp,
  'test2', '[{"login": "l3"}, {"login": "l4"}]', 'failed', 2, '124',
  FALSE, 'test_service', 'test_api2', '{"test_key": "test_value"}', '235',
  '2017-11-01T01:10:00'::timestamp, 'push', '["TAXIRATE-35"]', '{}',
  null::timestamp, false, null::integer
  ), (
  'test_user2', '[]',
  '2017-11-01T01:10:00'::timestamp, '2017-11-01T01:10:00'::timestamp,
  'test2', '[{"login": "l3"}, {"login": "l4"}]', 'expired', 2, '125',
  FALSE, 'test_service', 'test_api2', '{"test_key": "test_value"}', '236',
  '2017-11-01T01:10:00'::timestamp, 'push', '["TAXIRATE-35", "RUPRICING-5729"]', '{}',
  null::timestamp, false, null::integer
  ), (
  'test_user2', '[]',
  '2017-11-01T01:10:00'::timestamp, '2017-11-01T01:10:00'::timestamp,
  'test2', '[{"login": "l3"}, {"login": "l4"}]', 'need_approval', 2, '126',
  FALSE, 'test_service', 'test_api2', '{"test_key": "test_value"}', '237',
  '2017-11-01T01:10:00'::timestamp, 'push', '["TAXIRATE-35", "RUPRICING-5728"]', '{}',
  null::timestamp, false, null::integer
  ), (
  'test_user2', '[]',
  '2017-11-01T01:10:00'::timestamp, '2017-11-01T01:10:00'::timestamp,
  'test2', '[{"login": "l3"}, {"login": "l4"}]', 'rejected', 2, '127',
  FALSE, 'test_service', 'test_api2', '{"test_key": "test_value"}', '238',
  '2017-11-01T01:10:00'::timestamp, 'push', '["TAXIRATE-35", "TAXIADMIN-73"]', '{}',
  null::timestamp, false, null::integer
  )
;
