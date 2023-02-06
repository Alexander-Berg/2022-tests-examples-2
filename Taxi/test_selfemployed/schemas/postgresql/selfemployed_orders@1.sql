CREATE TABLE IF NOT EXISTS receipts (
  id VARCHAR(32) NOT NULL, -- Id order/payment (uuid4)
  receipt_type VARCHAR(20) NOT NULL, -- Тип чека (order, subvention)
  park_id VARCHAR(32) NOT NULL, -- Id парка самозанятого
  driver_id VARCHAR(32) NOT NULL, -- Id водителя самозанятого
  inn VARCHAR(12), -- ИНН самозанятого
  status VARCHAR(20) NOT NULL, -- Статус
  total numeric (18, 6) NOT NULL,
  fns_id VARCHAR(50), -- Id чека в ФНС
  fns_url VARCHAR(256), -- Url на jpeg чека в ФНС
  is_corp BOOLEAN, -- Признак корпоративного заказа
  is_cashless BOOLEAN, -- Признак безналичного заказа
  receipt_at TIMESTAMP NOT NULL, -- Время формирования чека (local)
  receipt_at_tstz TIMESTAMPTZ NOT NULL, -- Время формирования чека
  checkout_at TIMESTAMP NOT NULL, -- Время расчета (local)
  checkout_at_tstz TIMESTAMPTZ NOT NULL, -- Время расчета
  created_at TIMESTAMP NOT NULL, -- Время создания записи в БД (utc)
  created_at_tstz TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Время создания записи в БД
  modified_at TIMESTAMP NOT NULL, -- Время модификации записи в БД (utc)
  modified_at_tstz TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Время модификации записи в БД
  do_send_receipt BOOLEAN NOT NULL DEFAULT TRUE, -- Состояние флага `do_send_receipts` в полном se.finished_profiles на момент приёма чека
  is_own_park BOOLEAN NOT NULL DEFAULT TRUE, -- Является ли парк собственным для самозанятого (FALSE для квазиков)

  PRIMARY KEY(id, receipt_type)
);

CREATE TABLE IF NOT EXISTS corrections (
  reverse_id VARCHAR(32) NOT NULL, -- Id чека, который отменяем
  new_id VARCHAR(32), -- Id чека, который добавляем в случае успешной отмены старого чека
  park_id VARCHAR(32) NOT NULL, -- Id парка самозанятого
  driver_id VARCHAR(32), -- Id водителя самозанятого
  status VARCHAR(20) NOT NULL, -- Статус корректировки
  total numeric (18, 6), -- Новая сумма чека
  receipt_at TIMESTAMP, -- Время формирования чека (local)
  receipt_at_tstz TIMESTAMPTZ, -- Время формирования чека
  checkout_at TIMESTAMP, -- Время расчета (local)
  checkout_at_tstz TIMESTAMPTZ, -- Время расчета
  created_at TIMESTAMP NOT NULL, -- Время создания записи в БД (utc)
  created_at_tstz TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Время создания записи в БД
  modified_at TIMESTAMP NOT NULL, -- Время модификации записи в БД (utc)
  modified_at_tstz TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- Время модификации записи в БД

  PRIMARY KEY(reverse_id)
);

CREATE INDEX idx_receipts_inn ON receipts (inn);
CREATE INDEX idx_receipts_modified_at ON receipts (modified_at);
CREATE INDEX idx_receipts_modified_at_tstz ON receipts (modified_at_tstz);

CREATE UNIQUE INDEX idx_corrections_new_id ON corrections(new_id);
CREATE INDEX idx_corrections_status ON corrections(status);
CREATE INDEX idx_corrections_modified_at ON corrections(modified_at);
CREATE INDEX idx_corrections_modified_at_tstz ON corrections(modified_at_tstz);


CREATE SCHEMA IF NOT EXISTS se_income;

DO
$grant_privileges_db$
    BEGIN
        IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname = 'taxiro') THEN
            GRANT USAGE ON SCHEMA se_income TO taxiro;
            GRANT SELECT ON ALL TABLES IN SCHEMA se_income TO taxiro;
            ALTER DEFAULT PRIVILEGES IN SCHEMA se_income GRANT SELECT ON TABLES TO taxiro;
        END IF;
    END
$grant_privileges_db$;


CREATE TABLE IF NOT EXISTS se_income.entries (
    id               BIGINT PRIMARY KEY,
    park_id          TEXT        NOT NULL,
    contractor_id    TEXT        NOT NULL,
    agreement_id     TEXT        NOT NULL,
    sub_account      TEXT        NOT NULL,
    doc_ref          BIGINT      NOT NULL,
    event_at         TIMESTAMPTZ NOT NULL,
    inn_pd_id        TEXT,
    is_own_park      BOOLEAN     NOT NULL,
    do_send_receipt  BOOLEAN     NOT NULL,
    status           TEXT        NOT NULL,
    amount           NUMERIC     NOT NULL,
    income_type      TEXT,
    order_id         TEXT,
    reverse_entry_id BIGINT,
    receipt_id       TEXT,
    receipt_url      TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON se_income.entries (updated_at);

CREATE OR REPLACE FUNCTION se_income.touch_updated_record()
    RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END
$$ LANGUAGE 'plpgsql';
CREATE TRIGGER touch_updated_record BEFORE UPDATE
    ON se_income.entries FOR EACH ROW EXECUTE PROCEDURE
    se_income.touch_updated_record();
