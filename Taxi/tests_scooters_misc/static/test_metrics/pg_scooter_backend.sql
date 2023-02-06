CREATE TABLE IF NOT EXISTS compiled_rides (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,

    session_id TEXT NOT NULL,
    object_id uuid,
    price integer NOT NULL,
    duration integer NOT NULL,
    start integer NOT NULL,
    finish integer NOT NULL,
    meta JSON,
    meta_proto TEXT,
    hard_proto TEXT
);

CREATE TABLE IF NOT EXISTS car_tags (
    tag_id uuid DEFAULT (uuid_generate_v4()) NOT NULL,
    object_id uuid NOT NULL,
    tag character varying(50),
    data text NOT NULL,
    performer character varying(50),
    priority integer DEFAULT 0,
    snapshot text DEFAULT NULL

    -- FOREIGN KEY(object_id) REFERENCES "car"(id)
);

CREATE TABLE IF NOT EXISTS drive_payments (
    id SERIAL PRIMARY KEY,
    payment_id text NOT NULL,
    account_id bigint,
    session_id text NOT NULL,
    billing_type text NOT NULL,
    payment_type text NOT NULL,
    status text NOT NULL,
    payment_error text,
    pay_method text NOT NULL,
    created_at_ts integer NOT NULL,
    last_update_ts integer NOT NULL,
    sum integer DEFAULT 0,
    cleared integer DEFAULT 0,
    order_id text DEFAULT '',
    payment_error_desc text DEFAULT '',
    card_mask text DEFAULT '',
    rrn text DEFAULT '',
    meta text,
	user_id uuid
);

TRUNCATE public.compiled_rides;
INSERT INTO public.compiled_rides
    (history_event_id, history_user_id, history_action, history_timestamp, session_id, price, duration, START, finish)
VALUES 
    (0, 'random_user', 'random_history', 0, 'random_session', 10000, 250, 0, extract(epoch FROM NOW()))
ON CONFLICT DO NOTHING;

TRUNCATE public.car_tags;
INSERT INTO public.car_tags
    (object_id, tag, data)
VALUES
    ('6cff3f09-fedd-4567-9efb-cde95c325d65', 'old_state_reservation', ''),
    ('6cff3f09-fedd-4567-9efb-cde95c325d65', 'scooter_krasnodar', '')
ON CONFLICT DO NOTHING;


TRUNCATE public.drive_payments;
INSERT INTO public.drive_payments
    (id, billing_type, payment_type, pay_method, payment_id, session_id, status, cleared, created_at_ts, last_update_ts) 
VALUES 
    (1, 'car_usage', 'mobile_payment', 'apple_token-123', 'payment_id_1', 'session_id_101', 'cleared', 10000, 0, extract(epoch FROM NOW()))
ON CONFLICT DO NOTHING;
