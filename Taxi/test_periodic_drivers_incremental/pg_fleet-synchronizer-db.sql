INSERT INTO fleet_sync.parks_mappings
 (park_id, mapped_park_id, app_family, created_at)
VALUES
 ('ParkOne', 'ParkOneVezet', 'vezet', CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;

INSERT INTO auxiliary.cursors
 (app_family, task_type, last_updated_ts)
VALUES
 ('vezet', 'drivers_incremental', '0_1570000000_0')
ON CONFLICT DO NOTHING;

INSERT INTO auxiliary.cursors
 (app_family, task_type, last_updated_ts)
VALUES
 ('vezet', 'parks_incremental', '0_1570000000_0')
ON CONFLICT DO NOTHING;
