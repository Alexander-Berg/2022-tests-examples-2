INSERT INTO approvals_schema.drafts (
  created_by, comments, created, updated, description, approvals,
  status, version, request_id, run_manually, service_name,
  api_path, data, change_doc_id, apply_time, mode, tickets, summary,
  deferred_apply, reminded, scheme_type, tplatform_namespace
) VALUES (
    'test_user', '{}', '2017-11-01T01:10:00'::timestamp,
    '2017-11-01T01:10:00'::timestamp, 'test', '[]', 'approved', 1, '123',
    FALSE, 'test_service', 'test_api', '{"test_key": "test_value"}', '234',
    '2017-11-01T01:10:00'::timestamp, 'push', '["TAXIRATE-35"]', '{}',
    '2017-11-01T01:10:00'::timestamp, null::timestamp, 'platform', 'market'
  ), (
    'test_user2', '{}', '2017-11-01T01:10:00'::timestamp,
    '2017-11-01T01:10:00'::timestamp, 'test2', '[]', 'applying', 2, '124',
    FALSE, 'test_service', 'test_api2', '{"test_key": "test_value"}', '235',
    '2017-11-01T01:10:00'::timestamp, 'push', '[]', '{}', null::timestamp,
    null::timestamp, 'admin', 'taxi'
  ), (
    'test_user3', '{}', '2017-11-01T01:10:00'::timestamp,
    '2017-11-01T01:10:00'::timestamp, 'test3', '[]', 'applying', 2, '125',
    FALSE, 'test_service', 'test_api3', '{}', '236',
    '2017-11-01T01:10:00'::timestamp, 'poll', '[]', '{}', null::timestamp,
    null::timestamp, null, null
  ), (
    'test_user', '{}', '2016-11-01T01:10:00'::timestamp,
    '2016-11-01T01:10:00'::timestamp, 'test', '[{"login": "evgen"}]',
    'need_approval', 1, '1234',
    FALSE, 'test_service', 'test_api', '{"test_key": "test_value"}', '2345',
    null::timestamp, 'push', '["TAXIRATE-35"]', '{}',
    '2016-11-01T01:10:00'::timestamp, '2016-11-01T01:10:00'::timestamp, null, null
  ), (
    'test_user', '{}', '2016-11-01T01:10:00'::timestamp,
    '2016-11-01T01:10:00'::timestamp, 'test',
     '[{"login": "evgen"},{"login": "neo"}]', 'need_approval', 1, '1235',
    FALSE, 'test_service', 'test_api', '{"test_key": "test_value"}', '2346',
    null::timestamp, 'push', '["TAXIRATE-35"]',
    '{"new": "new", "current": "current"}',
    '2017-11-01T06:10:00'::timestamp, null::timestamp, null, null
  ), (
    'test_user', '{}', '2017-11-01T01:10:00'::timestamp,
    '2017-11-01T01:10:00'::timestamp, 'test', '[]', 'approved', 1, '126',
    FALSE, 'test_service', 'test_api', '{"test_key": "test_value"}', '237',
    '2017-11-01T05:10:40'::timestamp, 'push', '["TAXIRATE-35"]', '{}',
    null::timestamp, null::timestamp, null, null
  );

INSERT INTO approvals_schema.lock_ids
(
    draft_id, lock_id
)
VALUES
    (1, 'test_service:test_api:lock_id_1'),
    (1, 'test_service:test_api:lock_id_2'),
    (2, 'test_service:test_api2:lock_id_1'),
    (2, 'test_service:test_api2:lock_id_3'),
    (3, 'test_service:test_api3:lock_id_1');


INSERT INTO approvals_schema.summons
(
    draft_id, yandex_login, summoned
)
VALUES
    (1, 'test_login1', '2017-11-01T00:10:00'::timestamp),
    (1, 'test_login2', '2017-11-01T00:10:00'::timestamp),
    (5, 'test_login1', '2017-11-01T00:10:00'::timestamp),
    (5, 'test_login2', '2017-11-01T00:10:00'::timestamp);
