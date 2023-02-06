CREATE TABLE ds.blocks_update(
  driver_id BIGINT PRIMARY KEY REFERENCES ds.drivers(id),
  checked_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ds_blocks_update_checked_ts_index ON ds.blocks_update(checked_ts);
