INSERT INTO tips.tips (id, is_final, updated_at) 
VALUES
    ('order_1_above_exp_time_final',     true,  '2020-11-24T12:00:00'),
    ('order_2_above_exp_time_not_final', false, '2020-11-24T12:00:00'),
    ('order_3_below_exp_time_final',     true,  '2020-11-24T12:00:00'),
    ('order_4_below_exp_time_not_final', false, '2020-11-24T12:00:00');
