CREATE DATABASE bar WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C';

\connect bar

CREATE SCHEMA state;

CREATE TABLE state.services (
  id integer NOT NULL PRIMARY KEY,
  name character varying(128) NOT NULL
);

CREATE SCHEMA log;

CREATE TABLE log.messages (
  id integer NOT NULL PRIMARY KEY,
  service_id integer NOT NULL REFERENCES state.services (id),
  timestamp timestamp NOT NULL,
  message text NOT NULL
);

CREATE VIEW log.messages_view AS SELECT * FROM log.messages;
