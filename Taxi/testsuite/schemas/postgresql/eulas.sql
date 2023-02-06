
CREATE SCHEMA eulas;

CREATE TYPE eulas.status_t AS ENUM (
  'accepted',
  'rejected'
);

CREATE TABLE eulas.users(
  yandex_uid text NOT NULL,
  eula_id text NOT NULL,
  status eulas.status_t NOT NULL,
  valid_till timestamptz NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT current_timestamp,
  created_at timestamptz NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY(yandex_uid, eula_id)
);
