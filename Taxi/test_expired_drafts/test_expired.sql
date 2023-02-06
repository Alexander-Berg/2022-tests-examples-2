INSERT INTO approvals_schema.drafts (
  created_by, comments, created, updated, description, approvals,
  status, version, request_id, run_manually, service_name,
  api_path, data, change_doc_id, apply_time, mode, tickets, summary,
  deferred_apply, reminded, date_expired
) VALUES
  -- expired draft
    (
        'test_user', '{}', '2017-10-01T01:10:00'::timestamp,
        '2017-11-01T01:10:00'::timestamp, 'test', '[]', 'need_approval', 1, '123',
        FALSE, 'test_service', 'test_api', '{"test_key": "test_value"}', '123',
        null::timestamp, 'push', '["TAXIRATE-35"]', '{}',
        null::timestamp, null::timestamp, null::timestamp
    ),
    -- expired_date > now
    (
        'test_user2', '{}', '2017-10-01T01:10:00'::timestamp,
        '2017-11-01T01:10:00'::timestamp, 'test2', '[]', 'need_approval', 2, '345',
        FALSE, 'test_service', 'test_api2', '{"test_key": "test_value"}', '345',
        null::timestamp, 'push', '[]', '{}', null::timestamp,
        null::timestamp, '2017-11-22T01:10:00'::timestamp
    ),
    -- expired_date < now
    (
        'test_user3', '{}', '2017-10-01T01:10:00'::timestamp,
        '2017-11-01T01:10:00'::timestamp, 'test3', '[]', 'need_approval', 2, '678',
        FALSE, 'test_service', 'test_api3', '{}', '678',
        null::timestamp, 'push', '[]', '{}', null::timestamp,
        null::timestamp, '2017-11-01T00:10:00'::timestamp
    ),
    -- new draft
    (
        'test_user3', '{}', '2017-11-01T01:10:00'::timestamp,
        '2017-11-01T01:10:00'::timestamp, 'test3', '[]', 'need_approval', 2, '910',
        FALSE, 'test_service', 'test_api3', '{}', '910',
        null::timestamp, 'push', '[]', '{}', null::timestamp,
        null::timestamp, null::timestamp
    ),
      -- draft with deferred_apply
    (
        'test_user', '{}', '2017-10-01T01:10:00'::timestamp,
        '2017-11-01T01:10:00'::timestamp, 'test', '[]', 'need_approval', 1, '321',
        FALSE, 'test_service', 'test_api', '{"test_key": "test_value"}', '321',
        null::timestamp, 'push', '["TAXIRATE-35"]', '{}',
        '2017-11-01T01:10:00'::timestamp, null::timestamp, null::timestamp
    )
    ;

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
    (1, 'test_login2', '2017-11-01T00:10:00'::timestamp);
