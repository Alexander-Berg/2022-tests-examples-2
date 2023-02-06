CREATE SCHEMA debts;

CREATE TABLE debts.taxi_order_debts
(
  order_id    TEXT           NOT NULL,
  order_info  JSONB          NOT NULL,
  status      TEXT           NOT NULL,
  yandex_uid  TEXT           NOT NULL,
  phone_id    TEXT           NOT NULL,
  brand       TEXT           NULL,
  created     TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
  updated     TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
  value       DECIMAL(15, 4) NULL,
  currency    TEXT           NULL,
  reason_code TEXT           NULL,
  PRIMARY KEY (order_id)
);
CREATE INDEX yandex_uid ON debts.taxi_order_debts (yandex_uid);
CREATE INDEX phone_id ON debts.taxi_order_debts (phone_id);
