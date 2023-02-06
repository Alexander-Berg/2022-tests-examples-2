insert into eats_business_rules.counterparty (id, source_id, client_id, "name", country, region, city)
values (1, '21', 21, 'Ресторан 1', 'Россия', 'Москва', 'Москва'),
       (2, '43', 43, 'Ресторан 2', 'Россия', 'Московская область', 'Коломна'),
       (3, '22', 22, 'Ресторан 3', 'Россия', 'Москва', 'Москва'),
       (4, '121', 121, 'Иванов', 'Россия', 'Москва', 'Москва'),
       (5, '444', 444, 'Петров', 'Россия', 'Москва', 'Москва'),
       (6, '666', 666, 'Сидоров', 'Россия', 'Москва', 'Москва');

insert into eats_business_rules.place
values (12, 1),
       (34, 2),
       (22, 3);

insert into eats_business_rules.courier
values (12, 4),
       (34, 5),
       (22, 6);

insert into eats_business_rules.commission (id, applied_at, cancelled_at, counterparty_id, service_type, commission)
values (1, '2020-11-01T00:00:00', '2020-11-03T00:00:00', 1, 'place_delivery', '{"commission": "9.44", "fix_commission": "100", "acquiring_commission": "0"}'),
       (2, '2020-11-01T00:00:00', '2020-11-03T00:00:00',  1, 'pickup', '{"commission": "8", "fix_commission": "10", "acquiring_commission": "1.5"}'),
       (3, '2020-11-03T00:00:00', '2020-12-01T00:00:00', 1, 'place_delivery', '{"commission": "9", "fix_commission": "0", "acquiring_commission": "0.5"}'),
       (4, '2020-11-03T00:00:00', '2020-12-01T00:00:00', 1, 'pickup', '{"commission": "10.01", "fix_commission": "110", "acquiring_commission": "0.05"}'),
       (5, '2020-12-01T00:00:00', null, 1, 'place_delivery', '{"commission": "4.44", "fix_commission": "200", "acquiring_commission": "0.2"}'),
       (6, '2020-12-01T00:00:00', null, 1, 'pickup', '{"commission": "9.4", "fix_commission": "3.14", "acquiring_commission": "10"}'),
       (7, '2020-11-01T00:00:00', '2021-11-01T00:00:00', 4, 'picker_delivery', '{"commission": "3.4", "fix_commission": "0", "acquiring_commission": "1"}'),
       (8, '2020-11-01T00:00:00', '2021-11-01T00:00:00',  4, 'tips', '{"commission": "5.4", "fix_commission": "10", "acquiring_commission": "1.5"}'),
       (9, '2021-11-01T00:00:00', null, 4, 'picker_delivery', '{"commission": "10", "fix_commission": "250", "acquiring_commission": "1.1"}'),
       (10, '2021-11-01T00:00:00', null, 4, 'tips', '{"commission": "5.5", "fix_commission": "30", "acquiring_commission": "2.17"}'),
       (11, '2021-01-01T00:00:00', null, 6, 'picker_delivery', '{"commission": "6.66", "fix_commission": "666", "acquiring_commission": "66"}'),
       (12, '2021-01-01T00:00:00', null, 6, 'tips', '{"commission": "6", "fix_commission": "600", "acquiring_commission": "16"}');
