INSERT INTO cashback_annihilator.balances (wallet_id, yandex_uid, balance_to_expire, currency, annihilation_date, fake_annihilation_date, notification_date, notification_target, notification_user_id)
VALUES 
('w/eb92da32-3174-5ca0-9df5-d42db472a355', '1111111', '1337', 'RUB', '2024-07-13 04:01:50.000000+03', '2024-07-13 04:01:50.000000+03', '2020-04-13 04:01:50.000000+03', 'yandex', '123'),
('wallet_id', '7777777', '8723', 'RUB', '2024-07-13 04:01:50.000000+03', '2024-07-13 04:01:50.000000+03', '2021-04-13 04:01:50.000000+03', 'yandex', '123'),
('wallet_id_2', '98723411', '50', 'RUB', '2024-07-14 04:01:50.000000+03', '2024-07-14 04:01:50.000000+03', '2021-06-13 04:01:50.000000+03', 'yandex', '123'),
('w/eb92da32-3174-5ca0-9df5-d42db472a355_id3', '2222222', '1337', 'RUB', '2024-07-13 04:01:50.000000+03', '2024-07-13 04:01:50.000000+03', '2020-04-13 04:01:50.000000+03', 'yandex', '123');


INSERT INTO cashback_annihilator.balances (wallet_id, yandex_uid, balance_to_expire, currency, annihilation_date, fake_annihilation_date, notification_date, notified_at, notification_target, notification_user_id)
VALUES 
('w/another_wallet', '92350112', '321', 'RUB', '2024-07-15 04:01:50.000000+03', '2024-07-15 04:01:50.000000+03', '2021-07-12 04:01:50.000000+03', '2021-07-12 04:01:50.000000+03', 'yandex', '123');

INSERT INTO cashback_annihilator.balances (wallet_id, yandex_uid, balance_to_expire, currency, annihilation_date, fake_annihilation_date, annihilated_at)
VALUES
('w/123', '123', '123', 'RUB', '2024-10-13 04:01:50+0300', '2024-10-13 04:01:50+0300', null );
