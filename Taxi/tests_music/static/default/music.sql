INSERT INTO music.players
  (version, created, order_id, driver_id, user_uid, alias_id, player_state)
VALUES (0, '2018-12-01T00:00:00.0Z', 'order-id-1', 'driver_id-1', 'yandex-uid-1', 'alias-id-1', NULL),
       (1, '2018-12-01T00:00:00.0Z', 'order-id-2', 'driver_id-2', 'yandex-uid-2', 'alias-id-2',
        '{"prev_button_available": true, "next_button_available": true, "status": "unknown"}'),
       (2, '2017-12-01T00:00:00.0Z', 'order-id-3', 'driver_id-2', 'yandex-uid-3', 'alias-id-3',
        '{}'),  -- NOTE: unused row
       (3, '2018-12-01T00:00:00.0Z', 'order-id-4', 'driver_id-4', 'yandex-uid-4', 'alias-id-4',
        '{"prev_button_available": true, "next_button_available": true, "status": "unknown", "volume": 15}');

INSERT INTO music.player_actions
  (action_id, action_code, action_time, action_data, order_id, alias_id)
VALUES ('hex-id-1', 'play_music', '2018-12-01T00:00:00.0Z', '{"deeplink": "some_link"}', 'order-id-2', 'alias-id-2'),
       ('hex-id-2', 'pause', '2018-12-01T00:00:01.0Z', NULL, 'order-id-2', 'alias-id-2'),
       ('hex-id-3', 'play', '2018-12-01T00:00:02.0Z', NULL, 'order-id-2', 'alias-id-2'),
       ('hex-id-4', 'set_volume', '2018-12-01T00:00:03.0Z', '{"volume": 50}', 'order-id-2', 'alias-id-2');
