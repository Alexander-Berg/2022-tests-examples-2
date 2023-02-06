INSERT INTO eats_restapp_communications.places_tg_logins (place_id, login_id, created_at, updated_at, deleted_at) 
VALUES 
  (1, 'some_login1', NOW() - INTERVAL '12 days', NOW() - INTERVAL '12 days', NULL), 
  (1, 'some_login2', NOW() - INTERVAL '12 days', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'), 
  (1, 'some_login3', NOW() - INTERVAL '12 days', NOW() - INTERVAL '12 days', NULL),
  (1, 'some_login4', NOW() - INTERVAL '12 days', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days')
;
