-- https://a.yandex-team.ru/arc/trunk/arcadia/drive/backend/tables/drive_payments
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

-- https://a.yandex-team.ru/arc/trunk/arcadia/drive/backend/tables/drive_refunds
CREATE TABLE IF NOT EXISTS drive_refunds (
    id SERIAL PRIMARY KEY,
    payment_id text NOT NULL,
    session_id text NOT NULL,
    status text NOT NULL,
    created_at_ts integer NOT NULL,
    last_update_ts integer NOT NULL,
    sum integer DEFAULT(0),
    order_id text,
    refund_id text,
    user_id text,
    billing_type text DEFAULT('car_usage'),
    real_refund boolean,
    payment_type text
);

-- https://a.yandex-team.ru/arc/trunk/arcadia/drive/backend/tables/compiled_rides
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

-- https://a.yandex-team.ru/arc/trunk/arcadia/drive/backend/tables/car_tags
CREATE TABLE IF NOT EXISTS car_tags (
    tag_id uuid DEFAULT (uuid_generate_v4()) NOT NULL,
    object_id uuid NOT NULL,
    tag character varying(50),
    data text NOT NULL,
    performer character varying(50),
    priority integer DEFAULT 0,
    snapshot text DEFAULT NULL
);


INSERT INTO scooters_misc.drive_tables_cursors
    (drive_table, drive_cursor)
VALUES
    ('drive_payments', 1),
    ('drive_refunds', 1),
    ('compiled_rides', 1)
ON CONFLICT DO NOTHING;


INSERT INTO public.drive_payments
    (id, billing_type, payment_type, pay_method, payment_id, session_id, status, cleared, created_at_ts, last_update_ts)
VALUES
    (1, 'car_usage', 'yandex_account', 'yandex_account_w/001', 'payment_id_1', 'session_id_101', 'cleared',        10000, 0, 0), -- will be skipped because of the cursor
    (2, 'car_usage', 'card',           'card-x256',            'payment_id_2', 'session_id_102', 'cleared',        10000, 0, 0), -- will be skipped because ot the payment_type
    (3, 'car_usage', 'yandex_account', 'yandex_account_w/003', 'payment_id_3', 'session_id_103', 'not_authorized', 0,     0, 0), -- will be skipped because of the status
    (4, 'car_usage', 'yandex_account', 'yandex_account_w/004', 'payment_id_4', 'session_id_104', 'cleared',        12000, 0, 0)  -- will be sent to tlog
ON CONFLICT DO NOTHING;


INSERT INTO public.drive_refunds
    (id, payment_id, session_id, status, sum, created_at_ts, last_update_ts, payment_type)
VALUES
    (1, 'payment_id_5', 'session_id_201', 'success',     12000, 0, 1624269600, 'card'          ), -- will be skipped because of the cursor
    (2, 'payment_id_6', 'session_id_202', 'success',     12000, 0, 1624273200, 'card'          ), -- will be sent to tlog
    (3, 'payment_id_7', 'session_id_203', 'not_success', 12000, 0, 1624273200, 'card'          ), -- will be skipped because of the status
    (4, 'payment_id_8', 'session_id_204', 'success',     12000, 0, 1624273200, 'yandex_account'), -- will be sent to tlog
    (5, 'payment_id_9', 'session_id_205', 'success',     12000, 0, 1624269600, NULL            )  -- will be skipped because of NULL payment_type
ON CONFLICT DO NOTHING;

TRUNCATE TABLE public.compiled_rides;
INSERT INTO public.compiled_rides
    (history_event_id, history_user_id, history_action, history_timestamp, session_id, object_id, price, duration, start, finish)
VALUES
    (1, 'stub', 'stub', 0, 'session_id_101', NULL,                                   0,     250, 0, 1624269600), -- will be skipped because of the price
    (2, 'stub', 'stub', 0, 'session_id_102', NULL,                                   0,     250, 0, 1624273200), -- will be skipped because of the price
    (3, 'stub', 'stub', 0, 'session_id_103', NULL,                                   0,     250, 0, 1624273200), -- will be skipped because of the price
    (4, 'stub', 'stub', 0, 'session_id_104', 'b84f3e8d-8c5a-4ad1-8859-0ba148148cb6', 12000, 250, 0, 1624276800)  -- will be sent to tlog
ON CONFLICT DO NOTHING;


INSERT INTO car_tags
    (object_id, tag, data)
VALUES
    ('b84f3e8d-8c5a-4ad1-8859-0ba148148cb6', 'scooter_krasnodar', '')
ON CONFLICT DO NOTHING;
