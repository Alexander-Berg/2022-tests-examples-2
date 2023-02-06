CREATE TABLE IF NOT EXISTS just_table (
  id VARCHAR(32) NOT NULL,
  condition_field INT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  modified_at TIMESTAMP,

  PRIMARY KEY(id)
);
CREATE INDEX IF NOT EXISTS just_table_created_at ON just_table (created_at);
CREATE INDEX IF NOT EXISTS just_table_modified_at ON just_table (modified_at);

CREATE TABLE IF NOT EXISTS polygons (
  id VARCHAR(32) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  polygon_data POLYGON,
  total numeric (18, 6) NOT NULL,
  range_dttm tsrange,
  PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS json_table (
  id VARCHAR(32) NOT NULL PRIMARY KEY,
  created_at TIMESTAMP NOT NULL,
  json_type JSON,
  jsonb_type JSONB
);

CREATE TABLE IF NOT EXISTS simple_table (
  id INTEGER NOT NULL PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS date_table (
  id VARCHAR(32) NOT NULL PRIMARY KEY,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMP NOT NULL,
  magic_ts TIMESTAMP,
  magic_date DATE
);

CREATE TABLE IF NOT EXISTS date_table_ok (
  id VARCHAR(32) NOT NULL PRIMARY KEY,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMP NOT NULL,
  magic_date DATE
);

CREATE TABLE IF NOT EXISTS date_table_err (
 id VARCHAR(32) NOT NULL PRIMARY KEY,
 created_at TIMESTAMPTZ,
 updated_at TIMESTAMP NOT NULL,
 magic_date DATE
);
