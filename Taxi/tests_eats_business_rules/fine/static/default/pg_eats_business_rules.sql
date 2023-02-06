insert into eats_business_rules.counterparty (id, source_id, client_id, "name", country, region, city)
values (1, '21', 12, 'Ресторан 1', 'Россия', 'Москва', 'Москва'),
       (2, '43', 43, 'Ресторан 2', 'Россия', 'Московская область', 'Коломна'),
       (3, '22', 22, 'Ресторан 3', 'Россия', 'Москва', 'Москва'),
       (4, '121', 121, 'Иванов', 'Россия', 'Москва', 'Москва'),
       (5, '444', 444, 'Петров', 'Россия', 'Москва', 'Москва'),
       (6, '666', 666, 'Сидоров', 'Россия', 'Москва', 'Москва'),
       (7, '777', 777, 'Сидоров', 'Казахстан', 'Алматинская область', 'Алма-Ата');

insert into eats_business_rules.place
values (12, 1),
       (34, 2),
       (22, 3),
       (52, 7);

insert into eats_business_rules.courier
values (12, 4),
       (34, 5),
       (22, 6);

insert into eats_business_rules.fine (id, applied_at, cancelled_at, created_at, level, business, delivery, reason,
                                      counterparty_id, fine)
values (3, '2020-11-01T00:00:00', null, '2020-11-01T00:00:00',
        'counterparty', 'store', 'native', 'cancellation', 2,
        '{"application_period": 24, "fine": "1.0", "fix_fine": "5.0", "min_fine": "0.5", "max_fine": "10.0", "gmv_limit": "7.0"}'),
       (5, '2020-11-01T01:00:00', null, '2020-11-01T00:00:00',
        'counterparty', 'store', 'native', 'return', 2,
        '{"application_period": 24, "fine": "1.0", "fix_fine": "5.0", "min_fine": "0.5", "max_fine": "10.0", "gmv_limit": "7.0"}'),
       (8, '2020-11-01T02:00:00', '2020-11-04T02:00:00', '2020-11-01T00:00:00',
        'counterparty', 'restaurant', 'native', 'return', 4,
        '{"application_period": 72, "fine": "3.5", "fix_fine": "5.0", "min_fine": "0.5", "max_fine": "10.0", "gmv_limit": "7.0"}'),
       (9, '2020-11-04T01:00:00', null, '2020-11-01T00:00:00',
        'counterparty', 'restaurant', 'native', 'return', 4,
        '{"application_period": 24, "fine": "1.0", "fix_fine": "5.0", "min_fine": "0.5", "max_fine": "10.0", "gmv_limit": "7.0"}'),
       (12, '2020-12-01T00:00:00', '2020-12-04T00:00:00', '2020-11-01T00:00:00',
        'counterparty', 'restaurant', 'native', 'return', 5,
        '{"application_period": 24, "fine": "2.0", "fix_fine": "7.0", "min_fine": "0.7", "max_fine": "8.0", "gmv_limit": "5.0"}');

insert into eats_business_rules.fine (id, applied_at, cancelled_at, created_at, level, business, delivery, reason, name,
                                      fine)
values (1, '2020-11-01T03:00:00', null, '2020-11-01T00:00:00', 'country', 'shop', 'pickup', 'return', 'Россия',
        '{"application_period": 24, "fine": "1.0", "fix_fine": "5.0", "min_fine": "0.5", "max_fine": "10.0", "gmv_limit": "7.0"}'),
       (2, '2020-11-01T02:00:00', null, '2020-11-01T00:00:00', 'city', 'shop', 'pickup', 'return', 'Москва',
        '{"application_period": 48, "fine": "2.5", "fix_fine": "4.5", "min_fine": "0.5", "max_fine": "10.0", "gmv_limit": "7.0"}'),
       (4, '2020-11-01T02:00:00', null, '2020-11-01T00:00:00', 'region', 'store', 'native', 'return',
        'Московская область',
        '{"application_period": 24, "fine": "1.0", "fix_fine": "5.0", "min_fine": "0.5", "max_fine": "10.0", "gmv_limit": "7.0"}'),
       (6, '2020-11-01T00:00:00', null, '2020-11-01T00:00:00', 'country', 'restaurant', 'native', 'return', 'Россия',
        '{"application_period": 24, "fine": "1.0", "fix_fine": "5.0", "min_fine": "0.5", "max_fine": "10.0", "gmv_limit": "7.0"}'),
       (7, '2020-11-01T02:00:00', null, '2020-11-01T00:00:00', 'country', 'restaurant', 'native', 'return', 'Казахстан',
        '{"application_period": 24, "fine": "2.5", "fix_fine": "5.0", "min_fine": "0.7", "max_fine": "10.0", "gmv_limit": "8.0"}'),
       (10, '2020-11-01T02:00:00', null, '2020-11-01T00:00:00', 'city', 'restaurant', 'native', 'return', 'Москва',
        '{"application_period": 23, "fine": "4.5", "fix_fine": "5.0", "min_fine": "0.5", "max_fine": "10.0", "gmv_limit": "7.0"}'),
       (11, '2020-11-01T03:00:00', null, '2020-11-01T00:00:00', 'region', 'restaurant', 'native', 'return',
        'Московская область',
        '{"application_period": 72, "fine": "3.5", "fix_fine": "5.0", "min_fine": "0.5", "max_fine": "10.0", "gmv_limit": "7.0"}');
