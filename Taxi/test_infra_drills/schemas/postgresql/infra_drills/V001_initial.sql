SET TIME ZONE 'UTC';

CREATE SCHEMA IF NOT EXISTS drills;
CREATE TYPE drill_card_states AS ENUM (
	'NEW', 'PLANNED', 'FINISHED', 'CANCELLED', 'DELETED'
);

CREATE TABLE IF NOT EXISTS drills.anchormen(
	login text PRIMARY KEY,
	drills_count int4,
	last_drill_date date
);

CREATE TABLE IF NOT EXISTS drills.drill_events (
	event_id int4 PRIMARY KEY,
	event_state text NULL,
	start_ts text NULL,
	end_ts text NULL,
	summary text NULL,
	event_description text NULL
);

CREATE TABLE IF NOT EXISTS drills.drill_st_tickets (
	ticket_id int4 PRIMARY KEY,
	summary text NULL,
	"description" text NULL
);

CREATE TABLE IF NOT EXISTS drills.drill_announces (
	announce_id serial4 PRIMARY KEY,
	is_announced boolean NOT NULL DEFAULT FALSE,
	telegram text NULL,
	email text NULL
);

ALTER TABLE drills.drill_announces ALTER is_announced SET DEFAULT null;
ALTER TABLE drills.drill_announces RENAME is_announced TO announce_count;
ALTER TABLE drills.drill_announces ALTER announce_count TYPE INTEGER USING (announce_count::integer);
ALTER TABLE drills.drill_announces ALTER announce_count SET DEFAULT 0;

ALTER TABLE drills.drill_announces DROP COLUMN telegram;
ALTER TABLE drills.drill_announces DROP COLUMN email;
ALTER TABLE drills.drill_announces ADD last_send timestamp NOT NULL DEFAULT '1970-01-01 00:00:00.000';

CREATE TABLE IF NOT EXISTS drills.drill_cards (
	drill_id serial4 PRIMARY KEY,
	"state" drill_card_states,
	announce_id int4 NULL,
	business_unit text NULL,
	drill_type text NULL,
	datacenter text NULL,
	drill_date date NULL,
	time_interval text NULL,
	coordinator text NULL,
	anchorman text NULL,
	members text NULL,
	calendar_event int4 NULL,
	"comment" text NULL,
	st_ticket text NULL,
	st_ticket_summary text NULL,
	st_ticket_description text NULL,
	updated_at timestamp NULL,
	deleted_at timestamp NULL,
	FOREIGN KEY (calendar_event) REFERENCES drills.drill_events(event_id) ON UPDATE CASCADE,
	FOREIGN KEY (announce_id) REFERENCES drills.drill_announces(announce_id) ON UPDATE CASCADE
);

CREATE OR REPLACE FUNCTION drills.drill_card_update_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW; 
END;
$$ LANGUAGE plpgsql;

CREATE trigger set_update_at_tr
    BEFORE INSERT OR UPDATE
    ON drills.drill_cards
    for each ROW
EXECUTE PROCEDURE drills.drill_card_update_at();

CREATE TABLE drills.tests (
	"key" text NOT NULL,
	"value" text NOT NULL
);

CREATE OR REPLACE FUNCTION drills.drill_announces_last_send()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_send = NOW();
    RETURN NEW; 
END;
$$ LANGUAGE plpgsql;

CREATE trigger set_last_send_tr
    BEFORE UPDATE
    ON drills.drill_announces
    for each ROW
EXECUTE PROCEDURE drills.drill_announces_last_send();
