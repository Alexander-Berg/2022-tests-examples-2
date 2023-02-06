CREATE TABLE IF NOT EXISTS just_table (
  id VARCHAR(32) NOT NULL,
  modified_at TIMESTAMP NOT NULL,

  PRIMARY KEY(id)
);
CREATE INDEX ON just_table(modified_at);
CREATE TABLE IF NOT EXISTS polygons (
  id VARCHAR(32) NOT NULL,
  created_at TIMESTAMP NOT NULL,

  PRIMARY KEY(id)
);

