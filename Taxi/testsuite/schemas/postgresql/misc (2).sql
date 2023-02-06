CREATE TABLE changes_0 (
    park_id character varying(32) NOT NULL,
    id character varying(32) NOT NULL,
    date timestamp without time zone NOT NULL,
    object_id character varying (32) NOT NULL,
    object_type character varying (32),
    user_id character varying (32),
    user_name character varying (32),
    counts integer NOT NULL,
    values character varying (8192) NOT NULL,
    ip character varying(32),
    PRIMARY KEY (park_id, id)
);

CREATE INDEX idx_changes_0_date ON changes_0 USING btree (park_id, date DESC);
CREATE INDEX idx_changes_0_object_id ON changes_0 USING btree (object_id);
