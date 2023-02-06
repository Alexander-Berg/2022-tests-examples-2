DROP SCHEMA IF EXISTS edc_app_checkups CASCADE;
CREATE SCHEMA edc_app_checkups;

SET SEARCH_PATH TO edc_app_checkups;

CREATE TYPE public_point_t_v1 AS
(
    id            uuid,
    address       TEXT,
    contact_name  TEXT,
    contact_phone TEXT,
    latitude      DOUBLE PRECISION,
    longitude     DOUBLE PRECISION,
    is_active     BOOLEAN,
    owner_park_id TEXT
);

CREATE TYPE service_point_t_v1 AS
(
    id         uuid,
    park_id    TEXT,
    type       TEXT,
    work_hours TEXT,
    is_active  BOOLEAN
);

CREATE TABLE IF NOT EXISTS public_points
(
    id            uuid             NOT NULL PRIMARY KEY,
    address       TEXT             NOT NULL,
    contact_name  TEXT             NOT NULL,
    contact_phone TEXT             NOT NULL,
    latitude      DOUBLE PRECISION NOT NULL,
    longitude     DOUBLE PRECISION NOT NULL,
    is_active     BOOLEAN          NOT NULL,
    owner_park_id TEXT,
    updated_ts    TIMESTAMP        NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX IF NOT EXISTS public_points_owner_park_id_idx
    ON public_points (owner_park_id);

CREATE TABLE IF NOT EXISTS service_points
(
    id              uuid      NOT NULL PRIMARY KEY,
    public_point_id uuid      NOT NULL,
    park_id         TEXT      NOT NULL,
    type            TEXT      NOT NULL,
    work_hours      TEXT      NOT NULL,
    is_active       BOOLEAN   NOT NULL,
    updated_ts      TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    FOREIGN KEY (public_point_id)
        REFERENCES public_points (id)
        ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS service_point_pp_id_type_idx
    ON service_points (public_point_id, type);

CREATE TYPE permission AS ENUM ('create_medical_review', 'create_technical_review');

CREATE TYPE checkup_t_v1 AS
(
    id              uuid,
    number          TEXT,
    creator_user_id TEXT,
    creator         JSON,
    driver_id       TEXT,
    driver          JSON,
    vehicle_id      TEXT,
    vehicle         JSON,
    park_id         TEXT,
    park            JSON,
    created_at      TIMESTAMP,
    passed_at       TIMESTAMP,
    status          TEXT
);

CREATE TYPE medical_review_t_v1 AS
(
    id                   uuid,
    physician_id         TEXT,
    physician            JSON,
    park_id              TEXT,
    resolution_is_passed BOOLEAN,
    resolution           JSON,
    passed_at            TIMESTAMP
);

CREATE TYPE technical_review_t_v1 AS
(
    id                   uuid,
    technician_id        TEXT,
    technician           JSON,
    park_id              TEXT,
    resolution_is_passed BOOLEAN,
    resolution           JSON,
    passed_at            TIMESTAMP
);


CREATE TABLE IF NOT EXISTS checkups
(
    id                  uuid      NOT NULL PRIMARY KEY,
    number              TEXT      NOT NULL UNIQUE,
    creator_user_id     TEXT      NOT NULL,
    creator             JSON      NOT NULL,
    driver_id           TEXT      NOT NULL,
    driver              JSON      NOT NULL,
    vehicle_id          TEXT      NOT NULL,
    vehicle             JSON      NOT NULL,
    park_id             TEXT      NOT NULL,
    park                JSON      NOT NULL,
    medical_review_id   uuid,
    technical_review_id uuid,
    created_at          TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    passed_at           TIMESTAMP,
    status              TEXT      NOT NULL
);

CREATE TABLE IF NOT EXISTS medical_reviews
(
    id                   uuid      NOT NULL PRIMARY KEY,
    checkup_id           uuid      NOT NULL,
    physician_id         TEXT      NULL,
    physician            JSON      NOT NULL,
    park_id              TEXT      NOT NULL,
    resolution_is_passed BOOLEAN   NOT NULL,
    resolution           JSON      NULL,
    passed_at            TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    FOREIGN KEY (checkup_id)
        REFERENCES checkups (id)
        ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE TABLE IF NOT EXISTS technical_reviews
(
    id                   uuid      NOT NULL PRIMARY KEY,
    checkup_id           uuid      NOT NULL,
    technician_id        TEXT      NOT NULL,
    technician           JSON      NOT NULL,
    park_id              TEXT      NOT NULL,
    resolution_is_passed BOOLEAN   NOT NULL,
    resolution           JSON      NOT NULL,
    passed_at            TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
    FOREIGN KEY (checkup_id)
        REFERENCES checkups (id)
        ON DELETE RESTRICT ON UPDATE RESTRICT
);

ALTER TABLE checkups
    ADD CONSTRAINT medical_review_id_fk
        FOREIGN KEY (medical_review_id)
            REFERENCES medical_reviews (id)
            ON DELETE RESTRICT ON UPDATE RESTRICT,
    ADD CONSTRAINT technical_review_id_fk
        FOREIGN KEY (technical_review_id)
            REFERENCES technical_reviews (id)
            ON DELETE RESTRICT ON UPDATE RESTRICT;

CREATE INDEX IF NOT EXISTS checkups_user_id_vehicle_id_idx
    ON checkups (driver_id, vehicle_id);

CREATE INDEX IF NOT EXISTS checkups_created_at_idx
    ON checkups (created_at);
