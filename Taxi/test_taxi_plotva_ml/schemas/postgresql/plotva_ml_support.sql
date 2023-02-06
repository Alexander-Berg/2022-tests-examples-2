DROP SCHEMA IF EXISTS support CASCADE;
CREATE SCHEMA support;
CREATE TABLE support.autoreply(id bigserial PRIMARY KEY, user_id text UNIQUE NOT NULL, last_visit timestamp with time zone NOT NULL);
