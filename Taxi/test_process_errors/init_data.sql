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
  'test_user3', '[]',
  '2017-11-01T01:10:00'::timestamp, '2017-11-01T01:10:00'::timestamp,
  'test2', '[{"login": "l3"}, {"login": "l5"}]', 'failed', 2, '125',
  FALSE, 'test_service2', 'test_api2', '{"test_key": "test_value"}', '236',
  '2017-11-01T01:10:00'::timestamp, 'push', '["TAXIRATE-35"]', '{}',
  null::timestamp, false, null::integer
  ), (
  'test_user', '[]',
  '2017-11-01T01:10:00'::timestamp, '2017-11-01T01:10:00'::timestamp,
  'test2', '[{"login": "test_login"}]', 'need_approval', 2, '126',
  FALSE, '$multidraft', '$multidraft', '{}', '$multidraft_123',
  '2017-11-01T01:10:00'::timestamp, 'push', '[]', '{}',
  null::timestamp, true, null::integer
  ), (
  'test_user', '[]',
  '2017-11-01T01:10:00'::timestamp, '2017-11-01T01:10:00'::timestamp,
  'test2', '[{"login": "l1"}, {"login": "l2"}]', 'failed', 2, '127',
  FALSE, 'test_service2', 'test_api2', '{}', 'ch_22',
  '2017-11-01T01:10:00'::timestamp, 'push', '[]', '{}',
  null::timestamp, false, 4
  ), (
  'test_user', '[]',
  '2017-11-01T01:10:00'::timestamp, '2017-11-01T01:10:00'::timestamp,
  'test2', '[{"login": "l1"}, {"login": "l2"}]', 'failed', 2, '128',
  FALSE, 'test_service2', 'test_api2', '{}', 'ch_23',
  '2017-11-01T01:10:00'::timestamp, 'push', '[]', '{}',
  null::timestamp, false, 4
  );

insert into
    approvals_schema.process_errors (
        draft_id,
        response_body,
        response_status,
        response_headers,
        error_type,
        details,
        error_processed
    )
values
    (1, null, null, null, 'other', '', true),
    (2, null, null, null, 'timeout', 'Timeout', false),
    (3, null, null, null, 'other', 'Other', false),
    (
        5,
        '{"test": "value"}',
        409,
        '{"X-YaRequestId": "test-link"}'::jsonb,
        'bad_response',
        'Bad response',
        false
    ),
    (6, null, null, null, 'exception', 'Exception', false)

