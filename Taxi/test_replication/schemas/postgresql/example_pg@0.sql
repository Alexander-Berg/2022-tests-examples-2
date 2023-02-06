CREATE TABLE IF NOT EXISTS just_table (
  id VARCHAR(32) NOT NULL,
  doc_type VARCHAR(20) NOT NULL,
  total numeric (18, 6) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  modified_at TIMESTAMP,

  PRIMARY KEY(id, doc_type)
);
