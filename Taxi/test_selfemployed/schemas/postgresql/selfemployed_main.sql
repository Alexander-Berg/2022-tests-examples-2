CREATE TABLE IF NOT EXISTS profiles (
  id VARCHAR(32) PRIMARY KEY, -- Синтетический id самозанятого (uuid4)
  step VARCHAR(20), -- Название шага, на котором находится процесс регистрации
  status VARCHAR(20), -- Статус
  inn VARCHAR(12), -- ИНН
  phone VARCHAR(50), -- Номер телефона
  phone_changed BOOLEAN, -- Факт изменения номера
  first_name VARCHAR(50), -- Имя (из ФНС)
  last_name VARCHAR(50), -- Фамилия (из ФНС)
  middle_name VARCHAR(50), -- Отчество (из ФНС)
  address VARCHAR(200), -- Адрес регистрации
  apartment_number VARCHAR(6), -- Номер квартиры
  post_code VARCHAR(6), -- Почтовый индекс
  account_number VARCHAR(20), -- Расчётный счет
  bik VARCHAR(9), -- БИК
  park_id VARCHAR(32), -- Id парка самозанятого
  driver_id VARCHAR(32), -- Id водителя самозанятого
  from_park_id VARCHAR(32), -- Id парка из которого конвертнулся самозанятый
  from_driver_id VARCHAR(32), -- Id водителя из которого конвертнулся самозанятый
  selfreg_id VARCHAR(32), -- Id профиля водителя из саморегистрации
  request_id VARCHAR(20), -- Id заявки на привязку самозанятого к Яндекс.Такси
  sms_track_id VARCHAR(50), -- Временный token для подтверждения телефона по СМС
  agreement_accepted BOOLEAN, -- Факт принятия оферты
  salesforce_account_id TEXT,  -- Id в salesforce для редактирования реквизитов
  created_at TIMESTAMP NOT NULL, -- Время создания профиля (utc)
  created_at_tstz TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- Время создания профиля
  modified_at TIMESTAMP NOT NULL, -- Время модификации профиля (utc)
  modified_at_tstz TIMESTAMPTZ NOT NULL DEFAULT NOW(),-- Время модификации профиля
  gas_stations_accepted BOOLEAN, -- Принята ли оферта заправок
  salesforce_requisites_case_id TEXT -- Id реквизитов в salesforce
);

CREATE UNIQUE INDEX idx_profiles_selfreg_inn ON profiles (inn);
CREATE UNIQUE INDEX idx_profiles_park_driver ON profiles (park_id, driver_id);
CREATE UNIQUE INDEX idx_profiles_from_park_driver ON profiles (from_park_id, from_driver_id);
CREATE INDEX idx_profiles_modified_at ON profiles (modified_at);
CREATE INDEX idx_profiles_modified_at_tstz ON profiles (modified_at_tstz);

CREATE TABLE IF NOT EXISTS cron_runs (
  task_name VARCHAR(32) PRIMARY KEY, -- Название джобы
  last_run TIMESTAMP DEFAULT '2019-01-01 00:00:00', -- Последний раз прошла
  last_run_tstz TIMESTAMPTZ DEFAULT '2019-01-01 00:00:00 +00' -- Последний раз прошла
);

CREATE TABLE IF NOT EXISTS referrals
(
  park_id       VARCHAR(32) NOT NULL,    -- Id парка самозанятого
  driver_id     VARCHAR(32) NOT NULL,    -- Id водителя самозанятого

  promocode     VARCHAR(30),             -- Промокод для пользователя
  reg_promocode VARCHAR(30),             -- Промокод, введенный при регистрации

  created_at       TIMESTAMP DEFAULT NOW(), -- Время создания профиля (utc)
  created_at_tstz  TIMESTAMPTZ DEFAULT NOW(), -- Время создания профиля
  modified_at      TIMESTAMP DEFAULT NOW(), -- Время модификации профиля (utc)
  modified_at_tstz TIMESTAMPTZ DEFAULT NOW(), -- Время модификации профиля

  PRIMARY KEY (park_id, driver_id)
);

CREATE UNIQUE INDEX idx_referrals_promocode ON referrals (promocode);

CREATE TABLE IF NOT EXISTS eats_registration_states (
  token_hash TEXT NOT NULL,
  park_id VARCHAR(32) NOT NULL, -- Id парка самозанятого
  driver_profile_id VARCHAR(32) NOT NULL, -- Id водителя самозанятого
  created_ts TIMESTAMP NOT NULL,
  created_tstz TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expire_ts TIMESTAMP NOT NULL,
  expire_tstz TIMESTAMPTZ NOT NULL,
  lock_ts TIMESTAMP,
  lock_tstz TIMESTAMPTZ,
  status VARCHAR(32) NOT NULL, -- 0 - created, 10 - pending, 20 - submitted
  PRIMARY KEY(token_hash)
);

CREATE INDEX idx_eats_registration_states_park_driver ON eats_registration_states (park_id, driver_profile_id);

CREATE SCHEMA IF NOT EXISTS se;

CREATE TABLE se.nalogru_phone_bindings (
    phone_pd_id                   TEXT PRIMARY KEY,
    status                        TEXT        NOT NULL,
    inn_pd_id                     TEXT UNIQUE,
    bind_request_id               TEXT,
    bind_requested_at             TIMESTAMPTZ,
    exceeded_legal_income_year    SMALLINT,
    exceeded_reported_income_year SMALLINT,
    increment                     BIGSERIAL   NOT NULL,
    created_at                    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    business_unit                 TEXT NOT NULL DEFAULT 'taxi'
);
CREATE INDEX se_nalogru_phone_bindings_replication_idx ON se.nalogru_phone_bindings (updated_at);
CREATE INDEX ON se.nalogru_phone_bindings (increment);
CREATE INDEX ON se.nalogru_phone_bindings (exceeded_reported_income_year);

CREATE TABLE se.quasi_profile_forms (
    park_id               TEXT        NOT NULL,
    contractor_profile_id TEXT        NOT NULL,
    phone_pd_id           TEXT        NOT NULL REFERENCES se.nalogru_phone_bindings (phone_pd_id),
    is_phone_verified     BOOLEAN     NOT NULL DEFAULT FALSE,
    sms_track_id          TEXT,
    is_accepted           BOOLEAN,
    requested_at          TIMESTAMPTZ,
    inn_pd_id             TEXT,
    increment             BIGSERIAL   NOT NULL,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (park_id, contractor_profile_id)
);
CREATE INDEX se_quasi_profile_forms_replication_idx ON se.quasi_profile_forms (updated_at);
CREATE INDEX ON se.quasi_profile_forms (increment);

CREATE TABLE IF NOT EXISTS se.finished_profiles (
    park_id               TEXT        NOT NULL,
    contractor_profile_id TEXT        NOT NULL,
    phone_pd_id           TEXT        NOT NULL REFERENCES se.nalogru_phone_bindings (phone_pd_id),
    inn_pd_id             TEXT        NOT NULL,
    do_send_receipts      BOOLEAN     NOT NULL DEFAULT TRUE,
    is_own_park           BOOLEAN     NOT NULL DEFAULT TRUE,
    increment             BIGSERIAL   NOT NULL,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    business_unit         TEXT NOT NULL DEFAULT 'taxi',
    PRIMARY KEY (park_id, contractor_profile_id)
);
CREATE INDEX se_finished_profiles_replication_idx ON se.finished_profiles (updated_at);
CREATE INDEX ON se.finished_profiles (phone_pd_id);
CREATE INDEX ON se.finished_profiles (increment);

CREATE OR REPLACE FUNCTION touch_updated_record()
RETURNS TRIGGER AS $$
    BEGIN
        -- There is a way to get sequence name dynamically,
        -- but we'd have to concatenate strings and make a table lookup
        NEW.increment = NEXTVAL(TG_ARGV[0]);
        NEW.updated_at = NOW();
        RETURN NEW;
    END
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER touch_updated_record BEFORE UPDATE
    ON se.nalogru_phone_bindings FOR EACH ROW EXECUTE PROCEDURE
    touch_updated_record('se.nalogru_phone_bindings_increment_seq');

CREATE TRIGGER touch_updated_record BEFORE UPDATE
    ON se.quasi_profile_forms FOR EACH ROW EXECUTE PROCEDURE
    touch_updated_record('se.quasi_profile_forms_increment_seq');

CREATE TRIGGER touch_updated_record BEFORE UPDATE
    ON se.finished_profiles FOR EACH ROW EXECUTE PROCEDURE
    touch_updated_record('se.finished_profiles_increment_seq');

CREATE TABLE IF NOT EXISTS se.ownpark_profile_forms_common (
    phone_pd_id                   TEXT PRIMARY KEY,
    external_id                   TEXT NOT NULL UNIQUE,
    state                         TEXT        NOT NULL,
    address                       TEXT,
    apartment_number              TEXT,
    postal_code                   TEXT,
    agreements                    JSONB,
    inn_pd_id                     TEXT,
    residency_state               TEXT,
    salesforce_account_id         TEXT,
    salesforce_requisites_case_id TEXT,
    initial_park_id               TEXT,
    initial_contractor_id         TEXT,
    created_park_id               TEXT,
    created_contractor_id         TEXT,
    increment                     BIGSERIAL   NOT NULL,
    created_at                    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ON se.ownpark_profile_forms_common (updated_at);
CREATE INDEX ON se.ownpark_profile_forms_common (increment);
CREATE TRIGGER touch_updated_record
    BEFORE UPDATE
    ON se.ownpark_profile_forms_common
    FOR EACH ROW
EXECUTE PROCEDURE
    touch_updated_record('se.ownpark_profile_forms_common_increment_seq');

CREATE TABLE IF NOT EXISTS se.ownpark_profile_forms_contractor (
    initial_park_id       TEXT        NOT NULL,
    initial_contractor_id TEXT        NOT NULL,
    phone_pd_id           TEXT,
    is_phone_verified     BOOLEAN     NOT NULL DEFAULT TRUE,
    track_id              TEXT,
    last_step             TEXT NOT NULL DEFAULT 'intro',
    increment             BIGSERIAL   NOT NULL,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    profession            TEXT NOT NULL DEFAULT 'taxi-driver',
    PRIMARY KEY (initial_park_id, initial_contractor_id)
);
CREATE INDEX ON se.ownpark_profile_forms_contractor (updated_at);
CREATE INDEX ON se.ownpark_profile_forms_contractor (increment);
CREATE TRIGGER touch_updated_record
    BEFORE UPDATE
    ON se.ownpark_profile_forms_contractor
    FOR EACH ROW
EXECUTE PROCEDURE
    touch_updated_record('se.ownpark_profile_forms_contractor_increment_seq');

CREATE TABLE IF NOT EXISTS se.finished_ownpark_profile_metadata (
    created_park_id               TEXT        NOT NULL,
    created_contractor_id         TEXT        NOT NULL,
    phone_pd_id                   TEXT        NOT NULL,
    external_id                   TEXT        NOT NULL UNIQUE,
    initial_park_id               TEXT        NOT NULL,
    initial_contractor_id         TEXT        NOT NULL,
    salesforce_account_id         TEXT        NOT NULL,
    salesforce_requisites_case_id TEXT,
    increment                     BIGSERIAL   NOT NULL,
    created_at                    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (created_park_id, created_contractor_id)
);
CREATE INDEX ON se.finished_ownpark_profile_metadata (updated_at);
CREATE INDEX ON se.finished_ownpark_profile_metadata (increment);
CREATE TRIGGER touch_updated_record
    BEFORE UPDATE
    ON se.finished_ownpark_profile_metadata
    FOR EACH ROW
EXECUTE PROCEDURE
    touch_updated_record('se.finished_ownpark_profile_metadata_increment_seq');

CREATE TYPE se.yandex_provider_type_enum AS ENUM('yandex', 'yandex_team');

CREATE TABLE IF NOT EXISTS se.parks_additional_terms (
    park_id                 TEXT        NOT NULL,
    contractor_profile_id   TEXT        NOT NULL,
    yandex_uid              TEXT        NOT NULL,
    yandex_provider         se.yandex_provider_type_enum NOT NULL,
    is_accepted             BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (park_id, yandex_uid, yandex_provider)
);

CREATE TABLE IF NOT EXISTS se.taxpayer_status_cache (
    inn_pd_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    second_name TEXT NOT NULL,
    registration_time TIMESTAMPTZ NOT NULL,
    region_oktmo_code TEXT NOT NULL,
    phone_pd_id TEXT NOT NULL,
    oksm_code TEXT,
    middle_name TEXT,
    unregistration_time TIMESTAMPTZ,
    unregistration_reason TEXT,
    activities jsonb,
    email TEXT,
    account_number TEXT,
    update_time TEXT,
    registration_certificate_num TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    increment BIGSERIAL NOT NULL
);
CREATE INDEX se_taxpayer_status_cache_replication_idx ON se.taxpayer_status_cache(updated_at);
CREATE INDEX ON se.taxpayer_status_cache (increment);
CREATE TRIGGER touch_updated_record
    BEFORE UPDATE
    ON se.taxpayer_status_cache
    FOR EACH ROW
EXECUTE PROCEDURE
    touch_updated_record('se.taxpayer_status_cache_increment_seq');
