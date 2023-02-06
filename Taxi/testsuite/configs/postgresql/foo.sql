CREATE DATABASE foo WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C';

\connect foo

CREATE TABLE users (
  id character varying(32) NOT NULL PRIMARY KEY,
  name character varying(128) NOT NULL
);
