CREATE SCHEMA IF NOT EXISTS card_antifraud;

-- Таблица верификации карт

CREATE TABLE card_antifraud.cards_verification
(
    id                       SERIAL      NOT NULL PRIMARY KEY,
    yandex_uid               TEXT        NOT NULL,
    device_id                TEXT        NOT NULL,
    card_id                  TEXT        NOT NULL,
    status                   TEXT        NOT NULL DEFAULT 'draft',
    method                   TEXT,
    version                  INTEGER     NOT NULL DEFAULT 0,
    x3ds_url                 TEXT,
    random_amount_tries_left INTEGER,
    finish_binding_url       TEXT,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    trust_verification_id    TEXT,
    purchase_token           TEXT,
    idempotency_token        TEXT        NOT NULL
);


ALTER TABLE card_antifraud.cards_verification
    ADD CONSTRAINT cards_verification_user_device_idempotency_uniq
    UNIQUE(yandex_uid, device_id, idempotency_token);

CREATE INDEX cards_verification_user_card_idx
    ON card_antifraud.cards_verification
    USING btree(yandex_uid, card_id);

CREATE INDEX cards_verification_updated_idx
    ON card_antifraud.cards_verification(updated_at);

-- Таблица верифицированных карт

CREATE TABLE card_antifraud.verified_cards
(
    id         SERIAL      NOT NULL PRIMARY KEY,
    yandex_uid TEXT        NOT NULL,
    device_id  TEXT        NOT NULL,
    card_id    TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
);

CREATE INDEX verified_cards_user_device_idx
    ON card_antifraud.verified_cards
    USING btree(yandex_uid, device_id);

-- Таблица проверенных устройств

CREATE TABLE card_antifraud.verified_devices
(
    id         SERIAL      NOT NULL PRIMARY KEY,
    yandex_uid TEXT        NOT NULL,
    device_id  TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
);

CREATE UNIQUE INDEX verified_devices_user_device_uniq_idx
    ON card_antifraud.verified_devices
    USING btree(yandex_uid, device_id);
