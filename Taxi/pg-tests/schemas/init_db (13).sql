CREATE SCHEMA coupons;

CREATE TYPE coupons.coupon_type AS ENUM (
    'support',
    'marketing',
    'referral',
    'referral_reward'
);

CREATE TABLE coupons.errors_log (
    coupon              TEXT                    NOT NULL,
    error_code          TEXT                    NOT NULL,
    cart_id             TEXT                    NOT NULL,
    created             TIMESTAMPTZ             NOT NULL DEFAULT CURRENT_TIMESTAMP,
    yandex_uid          TEXT                    NOT NULL,
    personal_phone_id   TEXT                    NULL,
    coupon_type         coupons.coupon_type     NULL
);

CREATE UNIQUE INDEX CONCURRENTLY coupons_unique_index ON coupons.errors_log (coupon, error_code, cart_id);

CREATE INDEX CONCURRENTLY coupons_created_index ON coupons.errors_log (created);
CREATE INDEX CONCURRENTLY coupons_yandex_uid_index ON coupons.errors_log (yandex_uid);
