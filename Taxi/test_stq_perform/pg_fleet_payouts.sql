
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
    stmt_status
  )
VALUES
  ('PARK-01', 1, '00000000-0000-0000-0000-000000000001', 5, 'executing'),
  ('PARK-01', 2, '00000000-0000-0000-0000-000000000002', 5, 'reverting')
;

INSERT INTO
  fleet_financial_statements.finstmt_entry (
    park_id,
    stmt_id,
    ent_id,
    driver_id,
    deleted_at,
    pay_amount
  )
VALUES
  ('PARK-01', 1,  1, 'DRIVER-08',   NULL,   0),
  ('PARK-01', 1,  2, 'DRIVER-09',   NULL,   0),
  ('PARK-01', 1,  3, 'DRIVER-10',   NULL,   0),
  ('PARK-01', 1,  4, 'DRIVER-01',  NOW(), 100),
  ('PARK-01', 1,  5, 'DRIVER-07',   NULL, 100),
  ('PARK-01', 1,  6, 'DRIVER-02',  NOW(), 200),
  ('PARK-01', 1,  7, 'DRIVER-06',   NULL, 200),
  ('PARK-01', 1,  8, 'DRIVER-03',  NOW(), 300),
  ('PARK-01', 1,  9, 'DRIVER-05',   NULL, 300),
  ('PARK-01', 1, 10, 'DRIVER-04',  NOW(), 400),
  ('PARK-01', 2,  1, 'DRIVER-08',   NULL,   0),
  ('PARK-01', 2,  2, 'DRIVER-09',   NULL,   0),
  ('PARK-01', 2,  3, 'DRIVER-10',   NULL,   0),
  ('PARK-01', 2,  4, 'DRIVER-01',  NOW(), 100),
  ('PARK-01', 2,  5, 'DRIVER-07',   NULL, 100),
  ('PARK-01', 2,  6, 'DRIVER-02',  NOW(), 200),
  ('PARK-01', 2,  7, 'DRIVER-06',   NULL, 200),
  ('PARK-01', 2,  8, 'DRIVER-03',  NOW(), 300),
  ('PARK-01', 2,  9, 'DRIVER-05',   NULL, 300),
  ('PARK-01', 2, 10, 'DRIVER-04',  NOW(), 400)
;
