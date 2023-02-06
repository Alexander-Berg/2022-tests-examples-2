CREATE SCHEMA test_schema;
CREATE TABLE test_schema.test_table (
  id VARCHAR(32) PRIMARY KEY,
  created_at_ts TIMESTAMP,
  created_at_ts_tz TIMESTAMPTZ,
  can_delete BOOLEAN,
  should_not_be_null VARCHAR(32)
);
CREATE TABLE test_schema.test_table_comp_pk (
  id VARCHAR(32),
  second_id VARCHAR(32),
  created_at_ts TIMESTAMP,
  created_at_ts_tz TIMESTAMPTZ,
  can_delete BOOLEAN,
  should_not_be_null VARCHAR(32),
  PRIMARY KEY(id, second_id)
);
CREATE TABLE test_table_two_pk (
  id VARCHAR(32),
  second_id VARCHAR(32),
  created_at_ts TIMESTAMP,
  created_at_ts_tz TIMESTAMPTZ,
  can_delete BOOLEAN,
  should_not_be_null VARCHAR(32),
  PRIMARY KEY(second_id, id)
);

CREATE TABLE test_schema.fixprefix (
  id VARCHAR(32) PRIMARY KEY,
  created_ts TIMESTAMPTZ
);
CREATE TABLE test_schema.fixprefix_0 (
  id VARCHAR(32) PRIMARY KEY,
  created_ts TIMESTAMPTZ
);
CREATE TABLE test_schema.fixprefix_u12345 (
  id VARCHAR(32) PRIMARY KEY,
  created_ts TIMESTAMPTZ
);
