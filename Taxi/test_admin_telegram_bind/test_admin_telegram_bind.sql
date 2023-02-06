INSERT INTO eats_restapp_communications.places_tg_logins (place_id, login_id, created_at) 
VALUES 
  (1, 'login_id_1', now()), 
  (1, 'login_id_2', now()), 
  (1, 'login_id_3', now()), 
  (1, 'login_id_4', now()), 
  (1, 'login_id_5', now()), 
  (1, 'login_id_6', now()), 
  (1, 'login_id_7', now()),
  (1, 'login_id_8', now()),
  (1, 'login_id_9', now()),
  (1, 'login_id_10', now()),
  (3, 'login_id_11', now())
;

INSERT INTO eats_restapp_communications.place_digest_send_schedule (place_id, is_active, timezone) VALUES (2, false, 'Europe/Moscow'), (3, true, 'Europe/Moscow');
