INSERT INTO eats_restapp_communications.places_tg_logins (place_id, login_id, created_at, updated_at) 
VALUES 
  (1, 'login_id_1', now() - INTERVAL '3 days', now() - INTERVAL '3 days'), 
  (1, 'login_id_2', now() - INTERVAL '3 days', now() - INTERVAL '3 days'), 
  (1, 'login_id_3', now() - INTERVAL '3 days', now() - INTERVAL '3 days'), 
  (1, 'login_id_4', now() - INTERVAL '3 days', now() - INTERVAL '3 days'), 
  (1, 'login_id_5', now() - INTERVAL '3 days', now() - INTERVAL '3 days'), 
  (1, 'login_id_6', now() - INTERVAL '3 days', now() - INTERVAL '3 days'), 
  (1, 'login_id_7', now() - INTERVAL '3 days', now() - INTERVAL '3 days'),
  (1, 'login_id_8', now() - INTERVAL '3 days', now() - INTERVAL '3 days'),
  (1, 'login_id_9', now() - INTERVAL '3 days', now() - INTERVAL '3 days'),
  (1, 'login_id_10', now() - INTERVAL '3 days', now() - INTERVAL '3 days'),
  (3, 'login_id_11', now() - INTERVAL '3 days', now() - INTERVAL '3 days')
;

INSERT INTO eats_restapp_communications.place_digest_send_schedule (place_id, is_active, timezone) VALUES (2, false, 'Europe/Moscow'), (3, true, 'Europe/Moscow');
