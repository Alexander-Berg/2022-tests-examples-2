SET TIME ZONE 'UTC';

INSERT INTO snb_eda.agg_place_digests (
    place_id, period_date,
    place_name, place_address, delivery_type, currency_code,
    orders_total_cnt, orders_total_delta_cnt, orders_success_cnt, orders_success_delta_cnt,
    revenue_earned_lcy, revenue_earned_delta_lcy, revenue_lost_lcy, revenue_lost_delta_lcy,
    fines_lcy, fines_delta_lcy, delay_min, delay_delta_min,
    rating, rating_delta,
    fact_work_time_min, fact_work_time_delta_min, plan_work_time_min, plan_work_time_delta_min,
    _etl_updated_at)
VALUES
  (
     1, '2021-05-01',
     'place1', 'address1', 'native', 'RUB',
     100, 10, 80, -10,
     111.11111, -11.11111, 1.12349, 1.12349,
     10.99999, 1.99999, 100, -10,
     4.55, 0.11,
     1000, -100, 1111, 111,
     '2021-05-01 00:00:00'::timestamptz
  ),
  (
     1, '2021-04-30',
     'place1', 'address1', 'native', 'RUB',
     null, null, null, null,
     null, null, null, null,
     null, null, null, null,
     null, null,
     null, null, null, null,
     '2021-05-01 00:00:00'::timestamptz
  ),
  (
     2, '2021-05-01',
     'place2', 'address2', 'marketplace', 'BYN',
     200, 20, 60, -20,
     222.22222, -22.22222, 2.12349, 2.12349,
     20.99999, 2.99999, 200, -20,
     3.55, 0.22,
     2000, -200, 2222, 222,
     '2021-05-01 00:00:00'::timestamptz
  );
