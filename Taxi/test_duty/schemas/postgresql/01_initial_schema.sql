DROP SCHEMA IF EXISTS duty CASCADE;
CREATE SCHEMA duty;


CREATE TABLE duty.duty_groups (
    id SERIAL UNIQUE PRIMARY KEY,
    compatibility_id TEXT DEFAULT NULL,
    name TEXT NOT NULL,
    rearrange_on_vacations BOOLEAN NOT NULL DEFAULT TRUE,
    calendar_layer INTEGER DEFAULT NULL,
    exclude_weekend BOOLEAN NOT NULL DEFAULT FALSE,
    abc_service TEXT,
    days_long INTEGER NOT NULL DEFAULT 7,
    shift_start INTEGER NOT NULL DEFAULT 12,
    st_queue TEXT DEFAULT NULL,

    UNIQUE (name),
    UNIQUE (compatibility_id),
    UNIQUE (calendar_layer)
);


CREATE TABLE duty.events (
    id SERIAL UNIQUE PRIMARY KEY,
    duty_group_id INTEGER REFERENCES
        duty.duty_groups (id) ON DELETE CASCADE,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    is_started BOOLEAN NOT NULL DEFAULT FALSE,
    login TEXT NOT NULL,
    calendar_event_id INTEGER DEFAULT NULL,
    st_key TEXT DEFAULT NULL,

    UNIQUE (duty_group_id, start_time, login)
);

CREATE INDEX duty_event_login
    ON duty.events (login);

CREATE INDEX duty_event_duty_group_id_start_time
    ON duty.events (duty_group_id, start_time);
