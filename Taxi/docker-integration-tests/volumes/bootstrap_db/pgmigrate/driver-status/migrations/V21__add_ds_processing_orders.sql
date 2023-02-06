CREATE TYPE ds.processing_status AS ENUM ('unknown', 'pending', 'assigned', 'finished', 'cancelled');

CREATE TABLE ds.processing_orders (
  id TEXT PRIMARY KEY,
  alias_id TEXT, 
  driver_id BIGINT REFERENCES ds.drivers(id),
  status ds.order_status NOT NULL DEFAULT 'none'::ds.order_status,
  processing_status ds.processing_status NOT NULL,
  updated_ts TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX ds_processing_orders_updated_ts_index ON ds.processing_orders(updated_ts);
