CREATE INDEX CONCURRENTLY place_updated_at_idx ON storage.places(updated_at);
CREATE INDEX CONCURRENTLY delivery_zone_update_at_idx ON storage.delivery_zones(updated_at);
