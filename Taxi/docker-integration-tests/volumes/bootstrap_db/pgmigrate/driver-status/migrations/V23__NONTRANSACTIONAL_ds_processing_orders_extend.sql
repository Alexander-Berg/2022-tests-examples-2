ALTER TABLE ds.processing_orders
  ALTER COLUMN updated_ts SET DEFAULT NOW(),
  ADD COLUMN event_updated_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  ADD COLUMN event_index INTEGER NOT NULL DEFAULT 0;
  
-- TODO temporary index needed during update_ts migration 
CREATE INDEX ds_processing_orders_event_updated_ts_index ON ds.processing_orders(event_updated_ts);
