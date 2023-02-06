SET timezone = 'Europe/Moscow';
CREATE TABLE IF NOT EXISTS test_table (
  id VARCHAR(32) PRIMARY KEY,
  created_at_ts TIMESTAMP,
  created_at_ts_tz TIMESTAMPTZ,
  can_delete BOOLEAN,
  should_not_be_null VARCHAR(32)
);
CREATE TABLE IF NOT EXISTS test_table_two_pk (
  id VARCHAR(32),
  second_id VARCHAR(32),
  created_at_ts TIMESTAMP,
  created_at_ts_tz TIMESTAMPTZ,
  can_delete BOOLEAN,
  should_not_be_null VARCHAR(32),
  PRIMARY KEY(id, second_id)
);
