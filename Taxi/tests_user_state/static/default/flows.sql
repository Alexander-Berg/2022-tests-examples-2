INSERT INTO last_payment_methods.flows (
  yandex_uid,
  service,
  flow,
  created_at,
  updated_at,
  payment_info
)
VALUES 
('uid', 'taxi', 'order', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z', '{"payment_method": {"type": "cash"}}'::jsonb),
('bound-uid1', 'taxi', 'order', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"payment_method": {"type": "card", "id": "card:123"}}'::jsonb),
('bound-uid1', 'taxi', 'tips', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z', NULL),
('bound-uid2', 'taxi', 'order', '2018-12-01T00:00:00.0Z', '2018-12-01T00:00:00.0Z', NULL),
('bound-uid2', 'taxi', 'tips', '2018-12-01T00:00:00.0Z', '2019-12-01T00:00:00.0Z', '{"payment_method": {"type": "cash"}}'::jsonb)
