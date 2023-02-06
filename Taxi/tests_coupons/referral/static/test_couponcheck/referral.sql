INSERT INTO referral.promocodes
(id, yandex_uid, promocode, country, config_id)
VALUES
('00000000000000000000000000000000', '123456789', 'promo', 'rus', 1),
('a416702f-c4ba-436c-b71d-a9945d0a9510', '1234567892', 'referral2', 'rus', 1),
('a416702f-c4ba-436c-b71d-a9945d0a9511', '1234567893', 'referralone1', 'rus', 1)
;

INSERT INTO referral.promocode_activations
(id, promocode_id, yandex_uid, created, start, finish, series_id)
VALUES
(1, '00000000000000000000000000000000', '123', '2017-01-01 00:00:00+03', '2017-01-01 00:00:00+03', '2017-02-01 00:00:00+03', 'referral'),
(2, 'a416702f-c4ba-436c-b71d-a9945d0a9510', '1234567778', '2010-03-24 15:00:00+03', '2010-03-24 15:00:00+03', '2010-04-24 15:00:00+03', 'referral'),
(3, 'a416702f-c4ba-436c-b71d-a9945d0a9510', '1234567779', '2017-03-01 15:00:00+03', '2017-03-01 15:00:00+03', '2017-03-30 15:00:00+03', 'referral'),
(4, 'a416702f-c4ba-436c-b71d-a9945d0a9511', '1234567779', '2017-03-01 15:00:00+03', '2017-03-01 15:00:00+03', '2017-03-30 15:00:00+03', 'referralone')
;


INSERT INTO referral.promocode_success_activations
(yandex_uid, activation_id, created)
VALUES
('123', 1, '2010-01-01 00:00:00.000000+03')
;
