INSERT INTO profiles
(id, from_driver_id, from_park_id, park_id, driver_id,
inn, created_at, modified_at)
VALUES
('aaa17', 'd1', 'p1', 'p1', 'd1',
'111', NOW()::TIMESTAMP, NOW()::TIMESTAMP)
ON CONFLICT DO NOTHING;
