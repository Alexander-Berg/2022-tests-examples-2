CREATE SCHEMA IF NOT EXISTS cashback;


CREATE TABLE IF NOT EXISTS cashback.order_rates
(
  order_id TEXT        NOT NULL,
  rates    JSONB       NOT NULL,
  updated  TIMESTAMPTZ DEFAULT NOW(),
  created  TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (order_id)
);

CREATE INDEX cs_or_updated ON cashback.order_rates (updated);
