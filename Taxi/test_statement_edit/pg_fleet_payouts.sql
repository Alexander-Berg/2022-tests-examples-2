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
    edited_at,
    edited_by,
    bcm_percent,
    bcm_minimum,
    next_ent_id,
    total_ent_count,
    total_pay_amount,
    total_bcm_amount
  )
VALUES
  (
    'PARK-01', 1, '00000000-0000-0000-0000-000000000001', 2, 'draft',
    '2020-01-01T12:00:00+03:00', 'Y1000',
    '2020-01-01T14:00:00+03:00', '{Y1001}',
    0.05, 100, 6,
    5, 15000, 771.4285
  )
;

INSERT INTO
  fleet_financial_statements.finstmt (
    park_id,
    stmt_id,
    stmt_ext_id,
    stmt_revision,
    stmt_status,
    deleted_at
  )
VALUES
  ('PARK-01', 2, '00000000-0000-0000-0000-000000000002', 3, 'draft', NOW()),
  ('PARK-01', 3, '00000000-0000-0000-0000-000000000003', 3, 'executing', NULL),
  ('PARK-02', 1, '00000000-0000-0000-0000-000000000001', 3, 'executing', NULL),
  ('PARK-02', 2, '00000000-0000-0000-0000-000000000002', 3, 'draft', NOW())
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
  ('PARK-01', 1, 1, 'DRIVER-01', 1000),
  ('PARK-01', 1, 2, 'DRIVER-02', 2000),
  ('PARK-01', 1, 3, 'DRIVER-03', 3000),
  ('PARK-01', 1, 4, 'DRIVER-04', 4000),
  ('PARK-01', 1, 5, 'DRIVER-05', 5000)
;

/*
  5% |  47.619047619047619 |   47.6190 |  100.0000
  5% |  95.238095238095238 |   95.2381 |  100.0000
  5% | 142.857142857142857 |  142.8571 |  142.8571
  5% | 190.476190476190476 |  190.4762 |  190.4762
  5% | 238.095238095238095 |  238.0952 |  238.0952
     |                     |  714.2856 |  771.4285
--------------------------------------------------
 10% |  90.909090909090909 |   90.9091 |  100.0000
 10% | 181.818181818181818 |  181.8182 |  181.8182
 10% | 272.727272727272727 |  272.7273 |  272.7273
 10% | 363.636363636363636 |  363.6364 |  363.6364
 10% | 454.545454545454545 |  454.5455 |  454.5455
     |                     | 1363.6365 | 1372.7274
*/
