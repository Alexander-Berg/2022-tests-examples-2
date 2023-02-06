CREATE SCHEMA tags;

CREATE TABLE tags.tag_records (
  entity_type text NOT NULL,
  entity_id text NOT NULL,
  name text NOT NULL,
  starts_at timestamp without time zone NOT NULL,
  ends_at timestamp without time zone NOT NULL
);
