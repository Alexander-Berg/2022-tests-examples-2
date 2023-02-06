INSERT INTO eats_performer_support.performer_taxi_promocodes(
    performer_id,
    type,
    series_id,
    code,
    expires_at,
    amount,
    created_at,
    updated_at)
VALUES
-- +3
       (1, 'after_shift'::performer_taxi_promocode_type, '1', 'code_1', '2021-06-10T0:30:00+0000', 31.00,  '2021-06-09T09:20:00+0000', '2021-06-09T21:00:00+0000'),
-- +7
       (3, 'after_shift'::performer_taxi_promocode_type, '3', 'code_3', '2021-06-09T19:30:00+0000', 31.00, '2021-06-09T05:40:00+0000', '2021-06-09T21:00:00+0000'),
-- +10
       (4, 'after_shift'::performer_taxi_promocode_type, '4', 'code_4', '2021-06-09T23:09:00+0000', 31.00, '2021-06-09T01:30:00+0000', '2021-06-09T21:00:00+0000'),
-- -5
       (5, 'after_shift'::performer_taxi_promocode_type, '5', 'code_5', '2021-06-10T0:30:00+0000', 31.00,  '2021-06-09T17:10:00+0000', '2021-06-09T21:00:00+0000'),
-- -7
       (7, 'after_shift'::performer_taxi_promocode_type, '7', 'code_7', '2021-06-09T19:20:00+0000', 31.00, '2021-06-09T19:40:00+0000', '2021-06-09T21:00:00+0000'),
-- -8
       (8, 'after_shift'::performer_taxi_promocode_type, '8', 'code_8', '2021-06-09T23:09:00+0000', 31.00, '2021-06-09T18:00:00+0000', '2021-06-09T21:00:00+0000');

-- 2021-06-09T20:00:00+0000
