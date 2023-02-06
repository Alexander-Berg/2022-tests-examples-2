CREATE TABLE ds.master_orders(
  alias_id VARCHAR(48) NOT NULL,
  order_id VARCHAR(48),
  contractor_id BIGINT NOT NULL REFERENCES ds.drivers(id),
  status ds.order_status NOT NULL,
  provider_id SMALLINT NOT NULL REFERENCES ds.providers(id),
  event_ts TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

  CONSTRAINT unique_performer_order UNIQUE (alias_id, contractor_id)
);

CREATE INDEX ds_master_orders_updated_ts_index ON ds.master_orders(updated_ts);
