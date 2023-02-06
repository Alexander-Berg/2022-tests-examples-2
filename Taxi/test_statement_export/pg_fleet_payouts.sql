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
    created_at,
    created_by,
    edited_at,
    edited_by,
    executed_at,
    executed_by,
    reverted_at,
    reverted_by,
    work_rule_id,
    work_status,
    balance_limit,
    pay_mult_of,
    pay_minimum,
    pay_maximum,
    bcm_percent,
    bcm_minimum,
    total_ent_count,
    total_pay_amount,
    total_bcm_amount
  )
VALUES
  (
    'PARK-01', 1, '00000000-0000-0000-0000-000000000001', 9, 'reverted',
    '2020-01-01T12:00:00+03:00', 'Y1000',
    '2020-01-01T14:00:00+03:00', '{Y1002}',
    '2020-01-01T16:00:00+03:00', 'Y1000',
    '2020-01-01T18:00:00+03:00', 'T9999',
    '{WORK_RULE_A}', '{working}',
    50.0001, 200.0001, 100.0001, 1000.0001,
    0.0001, 10.0001,
    5, 5000.0015, 50.0005
  )
;

INSERT INTO
  fleet_financial_statements.finstmt_entry (
    park_id,
    stmt_id,
    ent_id,
    driver_id,
    pay_amount
  )
VALUES
  ('PARK-01', 1, 1, 'DRIVER-01', 1000.0001),
  ('PARK-01', 1, 2, 'DRIVER-02', 1000.0002),
  ('PARK-01', 1, 3, 'DRIVER-03', 1000.0003),
  ('PARK-01', 1, 4, 'DRIVER-04', 1000.0004),
  ('PARK-01', 1, 5, 'DRIVER-05', 1000.0005)
;
