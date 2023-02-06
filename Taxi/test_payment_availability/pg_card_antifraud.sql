INSERT INTO card_antifraud.verified_cards(
  yandex_uid,
  device_id,
  card_id
)
VALUES (
  'user_2',
  'device_2',
  'card_2'
),
(
  'user_2',
  'device_2',
  'card_3'
),
(
  'user_3',
  'device_for_user_3',
  'card_for_user_3'
);

INSERT INTO card_antifraud.verified_devices (
  yandex_uid,
  device_id
)
VALUES (
  'user_uid_1',
  'device_1'
),
(
  'user_3',
  'device_for_user_3'
);
