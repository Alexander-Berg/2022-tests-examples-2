INSERT INTO card_antifraud.verified_devices(yandex_uid, device_id)
VALUES
  ('1234', 'verified_device_1');
INSERT INTO card_antifraud.verified_cards(yandex_uid, device_id, card_id)
VALUES
  ('2345', 'not_verified_device_1', 'x-234567');
