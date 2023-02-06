INSERT INTO eats_coupons.new_user_blacklist
  (id_type, id_value, banned_until)
VALUES ('eater_id', '1', '2022-05-01T00:00:00+0000'),
       ('eater_id', '2', NULL),
       ('eater_id', '3', '2022-05-01T00:00:00+0000');


INSERT INTO eats_coupons.new_user_bad_attempts
    (eater_id, device_id, personal_phone_id, card_id)
VALUES
('1', '', '2', 'card_id'),
('1', '', '3', 'card_id'),
('1', '', '4', 'card_id'),
('2', 'device', '5', 'card_id2'),
('3', '', '5', 'card_id3'),
('3', '', '6', 'card_id4');
