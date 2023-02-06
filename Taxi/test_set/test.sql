INSERT INTO metadata.candidate_metadata(order_id, park_id, driver_profile_id, metadata) VALUES
('order', 'park', 'uuid', '{"old_key": "old_value"}');

INSERT INTO metadata.candidate_metadata_v2(order_id, park_id, driver_profile_id, key, value) VALUES
('order', 'park', 'uuid', 'old_key', '["old_value"]');
