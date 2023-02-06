INSERT INTO music.players
  (created, order_id, driver_id, user_uid, alias_id, player_state)
VALUES ('2019-06-13 12:01:50.000000+03', 'order-id-1', 'driver_id-1', 'yandex-uid-1', 'alias-id-1', NULL),
       ('2019-06-13 14:01:51.000000+03', 'order-id-2', 'driver_id-2', 'yandex-uid-2', 'alias-id-2', NULL),
       ('2019-06-14 16:01:52.000000+03', 'order-id-3', 'driver_id-3', 'yandex-uid-3', 'alias-id-3', NULL),
       ('2019-06-14 18:01:53.000000+03', 'order-id-4', 'driver_id-4', 'yandex-uid-4', 'alias-id-4',
        '{"prev_button_available": true, "next_button_available": true, "status": "unknown"}');
