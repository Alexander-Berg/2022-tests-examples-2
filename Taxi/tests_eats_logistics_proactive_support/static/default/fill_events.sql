set search_path to eats_logistics_proactive_support;

INSERT INTO tracked_delivery_events (
    delivery_id,
    delivery_event_type,
    meta_info)
VALUES
('000002', 'assign', '{"position": [3.0, 5.0], "promise": "2021-03-04T14:50:00+00:00"}'),
('000002', 'assign', '{"position": [4.0, 5.5], "promise": "2021-03-04T14:55:00+00:00"}'),
('000003', 'assign', '{"position": [4.0, 0.0], "promise": "2021-03-04T15:35:00+00:00"}');
