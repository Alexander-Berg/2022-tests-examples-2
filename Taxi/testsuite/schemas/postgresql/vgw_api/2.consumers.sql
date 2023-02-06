-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

CREATE SCHEMA consumers;

CREATE TABLE consumers.consumers(
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  enabled BOOLEAN NOT NULL,
  quota INTEGER NOT NULL DEFAULT 0  -- to be deleted
);

CREATE TABLE consumers.consumer_voice_gateways(
  consumer_id INTEGER NOT NULL REFERENCES consumers.consumers(id) ON DELETE CASCADE,
  gateway_id TEXT NOT NULL REFERENCES voice_gateways.voice_gateways(id) ON DELETE CASCADE,
  PRIMARY KEY (consumer_id, gateway_id)
);
