
INSERT INTO
  fleet_financial_statements.park (park_id)
VALUES
  ('PARK-01')
;

INSERT INTO
  fleet_financial_statements.finstmt (
    park_id,
    stmt_id,
    stmt_ext_id,
    stmt_revision,
    stmt_status,
    bcm_percent,
    bcm_minimum,
    balance_at,
    work_rule_id,
    work_status
  )
VALUES
  ('PARK-01', 1, '00000000-0000-0000-0000-000000000001', 1, 'preparing',
   1, 75, '2020-01-01T12:00:00+03:00', '{}', '{}'),
  ('PARK-01', 2, '00000000-0000-0000-0000-000000000002', 1, 'preparing',
   1, 75, '2020-01-01T12:00:00+03:00', '{WORK_RULE_A, WORK_RULE_B}', '{}'),
  ('PARK-01', 3, '00000000-0000-0000-0000-000000000003', 1, 'preparing',
   1, 75, '2020-01-01T12:00:00+03:00', '{}', '{working, not_working}')
;
