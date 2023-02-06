INSERT INTO
  fleet_financial_statements.park (park_id)
VALUES
  ('PARK-01'),
  ('PARK-02')
;

INSERT INTO
  fleet_financial_statements.finstmt (
    park_id,
    stmt_id,
    stmt_ext_id,
    stmt_revision,
    stmt_status,
    created_at,
    created_by,
    deleted_at,
    executed_at,
    executed_by,
    work_rule_id,
    work_status
  )
VALUES
  (
    'PARK-01', 1, '00000000-0000-0000-0000-000000000001', 7, 'reverted',
    '2020-01-01T12:00:00+03:00', 'Y1000', NULL,
    '2020-01-01T14:00:00+03:00', 'Y1002', '{WORK_RULE_A}', '{working}'
  ),
  (
    'PARK-01', 2, '00000000-0000-0000-0000-000000000002', 3, 'executed',
    '2020-01-01T18:00:00+03:00', 'Y1000', NULL,
    '2020-01-01T20:00:00+03:00', 'Y1000', '{WORK_RULE_B}', '{working}'
  ),
  (
    'PARK-01', 3, '00000000-0000-0000-0000-000000000003', 2, 'draft',
    '2020-01-02T12:00:00+03:00', 'Y1001', '2020-01-02T14:00:00+03:00',
    NULL, NULL, '{}', '{not_working}'
  ),
  (
    'PARK-01', 4, '00000000-0000-0000-0000-000000000004', 2, 'draft',
    '2020-01-02T12:30:00+03:00', 'Y1001', '2020-01-02T14:30:00+03:00',
    NULL, NULL, '{}', '{fired}'
  ),
  (
    'PARK-01', 5, '00000000-0000-0000-0000-000000000005', 8, 'reverting',
    '2020-01-03T12:00:00+03:00', 'Y1001', NULL,
    '2020-01-03T14:00:00+03:00', 'Y1001', '{}', '{not_working}'
  ),
  (
    'PARK-01', 6, '00000000-0000-0000-0000-000000000006', 6, 'executing',
    '2020-01-03T12:05:00+03:00', 'Y1001', NULL,
    '2020-01-04T12:05:00+03:00', 'Y1000', '{}', '{fired}'
  ),
  (
    'PARK-01', 7, '00000000-0000-0000-0000-000000000007', 9, 'executing',
    '2020-01-03T12:10:00+03:00', 'Y1001', NULL,
    '2020-01-04T12:10:00+03:00', 'Y1000', '{}', '{fired}'
  ),
  (
    'PARK-01', 8, '00000000-0000-0000-0000-000000000008', 2, 'draft',
    '2020-01-04T12:00:00+03:00', 'Y1002', NULL,
    NULL, NULL, '{WORK_RULE_A}', '{}'
  ),
  (
    'PARK-01', 9, '00000000-0000-0000-0000-000000000009', 1, 'preparing',
    '2020-01-04T12:05:00+03:00', 'Y1002', NULL,
    NULL, NULL, '{WORK_RULE_B}', '{}'
  ),
  (
    'PARK-01', 10, '00000000-0000-0000-0000-000000000010', 1, 'preparing',
    '2020-01-04T12:10:00+03:00', 'Y1002', NULL,
    NULL, NULL, '{WORK_RULE_C}', '{}'
  ),
  (
    'PARK-02', 1, '00000000-0000-0000-0000-000000000001', 2, 'draft',
    '2020-01-01T18:00:00+03:00', 'Y3000', NULL,
    NULL, NULL, '{}', '{}'
  )
;