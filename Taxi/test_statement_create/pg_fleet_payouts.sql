INSERT INTO
  fleet_financial_statements.park (park_id, next_stmt_id)
VALUES
  ('PARK-01', 3)
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
  ('PARK-01', 1, '00000000-0000-0000-0000-000000000001', 2, 'draft', NULL),
  ('PARK-01', 2, '00000000-0000-0000-0000-000000000002', 3, 'draft', NOW())
;
