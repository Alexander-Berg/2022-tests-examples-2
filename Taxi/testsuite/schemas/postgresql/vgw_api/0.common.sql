-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

CREATE SCHEMA common;

CREATE TYPE common.client_type_t AS ENUM (
  'passenger',
  'driver',
  'dispatcher'
);

CREATE TYPE common.geo_point_t AS (
  lon DOUBLE PRECISION,
  lat DOUBLE PRECISION
);
