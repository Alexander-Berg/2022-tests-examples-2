CREATE TABLE changes_0 (
    park_id character varying(32) NOT NULL,
    id character varying(32) NOT NULL,
    date timestamp without time zone NOT NULL,
    object_id character varying (32) NOT NULL,
    object_type character varying (32) NOT NULL,
    user_id character varying (32) NOT NULL,
    user_name character varying (32) NOT NULL,
    counts integer NOT NULL,
    values character varying (8192) NOT NULL,
    ip character varying(32)
);

ALTER TABLE ONLY changes_0 ADD CONSTRAINT changes_0_pkey PRIMARY KEY (id);

CREATE INDEX idx_changes_0_id ON changes_0 USING btree (id);
