ALTER TABLE ds.drivers ADD CONSTRAINT unique_park_driver UNIQUE (park_id, driver_id);
