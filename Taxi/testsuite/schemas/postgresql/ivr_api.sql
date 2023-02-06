CREATE SCHEMA IF NOT EXISTS ivr_api;

CREATE TABLE IF NOT EXISTS ivr_api.order_data(
    order_id VARCHAR(40) PRIMARY KEY NOT NULL,
    inbound_number VARCHAR(16) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT (clock_timestamp() at time zone 'utc')::timestamp
);


CREATE INDEX IF NOT EXISTS order_data_created ON ivr_api.order_data(
  created ASC -- deleted by cron job regularly
);

CREATE TABLE IF NOT EXISTS ivr_api.worker_actions(
    id BIGSERIAL,
    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    worker_name VARCHAR NOT NULL,
    session_id VARCHAR,
    personal_phone_id VARCHAR NOT NULL,
    application VARCHAR,
    country VARCHAR,
    call_guid VARCHAR,
    order_id VARCHAR,
    callcenter_number VARCHAR,
    action_type VARCHAR NOT NULL,
    action_kwargs JSONB
);

CREATE INDEX IF NOT EXISTS action_created_idx ON ivr_api.worker_actions(created ASC);
CREATE INDEX IF NOT EXISTS call_guid_idx ON ivr_api.worker_actions(call_guid);
CREATE INDEX IF NOT EXISTS session_idx ON ivr_api.worker_actions(session_id);
CREATE INDEX IF NOT EXISTS order_idx ON ivr_api.worker_actions(order_id);


CREATE TYPE ivr_api.status AS ENUM ('ok', 'error', 'skipped', 'pending');
CREATE TYPE ivr_api.transport_type AS ENUM ('sms', 'call', 'ucommunication_scenario');

CREATE TABLE IF NOT EXISTS ivr_api.notifications(
    id                        VARCHAR                              , -- id нотификации (sringed uuid)
    event_id                  VARCHAR NOT NULL                     , -- id события, к которому принадлежит нотификация
    notification_alias        VARCHAR NOT NULL                     , -- человекочитаемый алиас для нотификации (main_order_notification и др)
    transport_type            ivr_api.transport_type DEFAULT NULL  , -- тип отправления нотификации (смс, звонок)
    notification_status       ivr_api.status NOT NULL              , -- текущий статус нотификации (pending, ok, skipped, error)
    created                   TIMESTAMPTZ NOT NULL DEFAULT NOW()   ,
    updated                   TIMESTAMPTZ NOT NULL DEFAULT NOW()   ,
    PRIMARY KEY (id)
    );

CREATE INDEX IF NOT EXISTS event_idx ON ivr_api.notifications(event_id);
CREATE INDEX IF NOT EXISTS notification_updated_idx ON ivr_api.notifications(updated);
