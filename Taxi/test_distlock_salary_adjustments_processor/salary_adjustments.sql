-- Курьеры
insert into eats_logistics_performer_payouts.performers (id, external_id)
values (5, 'courier_1'),
       (10, 'courier_2'),
       (15, 'courier_3'),
       (20, 'courier_4');

-- Сабжекты
insert into eats_logistics_performer_payouts.subjects (external_id, subject_type_id, performer_id)
values ('ggg', 1, 5),
       ('ttt', 1, 15);

-- Факторы
insert into eats_logistics_performer_payouts.factors (name, type, subject_type_id)
values  ('eats_region_id', 'string', 1),
        ('username', 'string', 1);

insert into eats_logistics_performer_payouts.factor_string_values (subject_id, factor_id, value)
values  (1, 1, 'region_1'),
        (1, 2, 'user_1'),
        (2, 1, 'region_3'),
        (2, 2, 'user_3');

-- Ручные корректировки
insert into eats_logistics_performer_payouts.salary_adjustments (id, performer_id, time_point_at, reason, amount, processed)
values (1, 5, '2020-10-08 01:00:00.000000 +00:00', 'prosto tak', 124.0001, false),
       (2, 10, '2020-10-08 02:00:00.000000 +00:00', 'asdasdasdsad', 400.5000, true),
       (3, 15, '2020-10-08 03:00:00.000000 +00:00', null, 10000.0000, false);
