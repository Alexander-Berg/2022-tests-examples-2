set search_path to eats_logistics_proactive_support;

INSERT INTO tracked_deliveries (
delivery_id,
delivery_type,
source_point_latitude,
source_point_longitude,
source_point_promise,
destination_point_latitude,
destination_point_longitude,
destination_point_promise)
VALUES
('000002', 'eats', 0.0, 0.0, '2021-03-04T14:45:00+00:00', 1.0, 1.0, '2021-03-04T15:30:00+00:00'),
('000003', 'eats', 5.0, 0.0, '2021-03-04T15:30:00+00:00', 1.0, 1.0, '2021-03-04T16:30:00+00:00'),
('000004', 'eats', 0.0, 10.0, '2021-03-04T18:00:00+00:00', 1.0, 1.0, '2021-03-04T20:00:00+00:00');
