INSERT INTO music.players
  (created, order_id, driver_id, user_uid, alias_id, player_state)
VALUES ('2018-12-01T00:00:00.0Z', 'order-id-4', 'driver_id-4', 'yandex-uid-4', 'alias-id-4', 
    '{"prev_button_available": true, "next_button_available": true, "status": "unknown"}');

INSERT INTO music.player_actions
  (action_id, action_code, action_time, action_data, order_id, alias_id)
VALUES ('4hex-id-4', 'play_music', '2018-12-01T00:00:00.0Z', '{"deeplink": "some_link"}', 'order-id-4', 'alias-id-4'),
       ('4hex-id-5', 'pause', '2018-12-01T00:00:01.0Z', NULL, 'order-id-4', 'alias-id-4'),
       ('4hex-id-6', 'play', '2018-12-01T00:00:02.0Z', '{}', 'order-id-4', 'alias-id-4'),
       ('4hex-id-7', 'play', '2018-12-01T00:00:03.0Z', NULL, 'order-id-4', 'alias-id-4'),
       ('4hex-id-8', 'next', '2018-12-01T00:00:04.0Z', NULL, 'order-id-4', 'alias-id-4');


INSERT INTO music.players
  (created, order_id, driver_id, user_uid, alias_id, player_state)
VALUES ('2018-12-01T00:00:00.0Z', 'order-id-5', 'driver_id-5', 'yandex-uid-5', 'alias-id-5', 
'{"prev_button_available": true, "next_button_available": true, "status": "playing"}');

INSERT INTO music.player_actions
  (action_id, action_code, action_time, action_data, order_id, alias_id)
VALUES ('5hex-id-3', 'pause', '2018-12-01T00:00:01.0Z', NULL, 'order-id-5', 'alias-id-5'),
       ('5hex-id-4', 'play_music', '2018-12-01T00:00:02.0Z', '{"deeplink": "some_link"}', 'order-id-5', 'alias-id-5'),
       ('5hex-id-5', 'pause', '2018-12-01T00:00:03.0Z', NULL, 'order-id-5', 'alias-id-5'),
       ('5hex-id-6', 'play_music', '2018-12-01T00:00:04.0Z', '{"deeplink": "some_link"}', 'order-id-5', 'alias-id-5'),
       ('5hex-id-7', 'next', '2018-12-01T00:00:05.0Z', NULL, 'order-id-5', 'alias-id-5');
