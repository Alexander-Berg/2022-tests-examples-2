SET TIME ZONE 'UTC';

CREATE SCHEMA IF NOT EXISTS fleet_fines;

CREATE TABLE IF NOT EXISTS fleet_fines.documents_vc (
    id BIGSERIAL PRIMARY KEY,
    park_id text NOT NULL,
    car_id text NOT NULL,
    vc_original text,
    vc_normalized text,
    is_normalized boolean default FALSE NOT NULL,
    is_valid boolean default FALSE NOT NULL,
    last_check_date timestamp,
    last_successful_check timestamp,
    source_modified_date timestamp,
    modified_at timestamp DEFAULT NOW() NOT NULL,
    last_ride_time timestamp NULL,
    UNIQUE(park_id, car_id)
);
CREATE TABLE IF NOT EXISTS fleet_fines.documents_dl (
    id BIGSERIAL PRIMARY KEY,
    park_id text NOT NULL,
    driver_id text NOT NULL,
    dl_pd_id_original text,
    dl_pd_id_normalized text,
    is_normalized boolean default FALSE NOT NULL,
    is_valid boolean default FALSE NOT NULL,
    last_check_date timestamp,
    last_successful_check timestamp,
    source_modified_date timestamp,
    modified_at timestamp DEFAULT NOW() NOT NULL,
    last_ride_time timestamp NULL,
    UNIQUE(park_id, driver_id)
);
CREATE TABLE IF NOT EXISTS fleet_fines.cursors (
    job_id text PRIMARY KEY,
    value text
);
CREATE TABLE IF NOT EXISTS fleet_fines.ym_requests (
    req_id text PRIMARY KEY,
    dl_pd_ids text[],
    vcs text[],
    created_at timestamp NOT NULL,
    next_poll_at timestamp NOT NULL,
    last_polled_at timestamp
);
CREATE TABLE IF NOT EXISTS fleet_fines.fines_dl (
    uin text PRIMARY KEY,
    dl_pd_id_normalized text NOT NULL,
    payment_link text NOT NULL,
    bill_date timestamp NOT NULL,
    sum float NOT NULL,
    discounted_sum float,
    discount_date timestamp,
    loaded_at timestamp NOT NULL,
    last_reloaded_at timestamp,
    article_code text,
    location text,
    disappeared_at timestamp,
    modified_at timestamp DEFAULT NOW() NOT NULL
);
CREATE TABLE IF NOT EXISTS fleet_fines.fines_vc (
    uin text PRIMARY KEY,
    vc_normalized text NOT NULL,
    payment_link text NOT NULL,
    bill_date timestamp NOT NULL,
    sum float NOT NULL,
    discounted_sum float,
    discount_date timestamp,
    loaded_at timestamp NOT NULL,
    last_reloaded_at timestamp,
    article_code text,
    location text,
    disappeared_at timestamp,
    modified_at timestamp DEFAULT NOW() NOT NULL
);

CREATE TABLE IF NOT EXISTS fleet_fines.fuse (
    id          varchar(64) PRIMARY KEY,
    chain_start timestamp   NOT NULL,
    count       bigint      NOT NULL
);

CREATE TABLE IF NOT EXISTS fleet_fines.deferred_updates (
    id BIGSERIAL PRIMARY KEY,
    uin text NOT NULL,
    eta timestamp NOT NULL
);
