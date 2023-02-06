-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

DROP SCHEMA IF EXISTS parks_activation CASCADE;

CREATE SCHEMA parks_activation;

CREATE TABLE parks_activation.change_history(
  id BIGSERIAL PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  park_id TEXT NOT NULL,
  field_name TEXT NOT NULL,
  /* We're not interested in types here */
  before TEXT,
  after TEXT,
  reason TEXT,
  additional_data TEXT
);
