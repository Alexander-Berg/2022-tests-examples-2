ALTER TABLE ds.orders ADD CONSTRAINT unique_id_driver_id UNIQUE (id, driver_id);
