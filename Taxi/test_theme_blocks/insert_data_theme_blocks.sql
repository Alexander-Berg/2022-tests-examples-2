INSERT INTO eats_report_storage.rad_suggests (place_id, prioriy, suggest)
VALUES (1, 10, 'rating'),
       (1, 5, 'pict_share'),
       (1, 1, 'cancels'),
       (2, 10, 'rating'),
       (2, 5, 'pict_share'),
       (2, 1, 'cancels')
;

INSERT INTO eats_report_storage.rad_quality (place_id, brand_id, name, address, rating, orders,
                                             avg_check, cancel_rating, pict_share, plus_flg, dish_as_gift_flg,
                                             discount_flg, second_for_free_flg, pickup_flg, mercury_flg)
VALUES (1, 1, 'Burgers', 'Moon', 4.0, 10, 10.5, 0.5, 0.0, false, true, false, false, false, true),
       (2, 1, 'Burgers', 'Moon', 4.0, 10, 10.5, 0.5, 0.0, false, true, false, false, false, true);

INSERT INTO eats_report_storage.agg_place_metric (place_id, utc_period_start_dttm, scale_name, brand_id, delivery_type,
                                                  order_cancel_cnt, order_success_cnt, order_cnt, order_cancel_pcnt,
                                                  revenue_earned_lcy, revenue_lost_lcy, revenue_lcy,
                                                  revenue_average_lcy,
                                                  currency_code, place_availability_pcnt, order_per_place_avg,
                                                  plan_work_time_min, fact_work_time_min, _etl_processed_at)
VALUES (1, '2021-12-08T03:00+03:00'::timestamptz, 'day', 1, 'native',
        10, 90, 100, 10.0,
        900.0, 10.0, 910.0, 10.0,
        'RUB', 75.0, 10.7,
        1000, 750, '2022-01-01T03:00+03:00'::timestamp),
       (1, '2021-12-07T03:00+03:00'::timestamptz, 'day', 1, 'native',
        10, 90, 100, 10.0,
        900.0, 10.0, 910.0, 10.0,
        'RUB', 75.0, 10.7,
        1000, 750, '2022-01-01T03:00+03:00'::timestamp),
       (1, '2021-12-06T03:00+03:00'::timestamptz, 'day', 1, 'native',
        10, 90, 100, 10.0,
        900.0, 10.0, 910.0, 10.0,
        'RUB', 75.0, 10.7,
        1000, 750, '2022-01-01T03:00+03:00'::timestamp),
       (2, '2021-12-08T03:00+03:00'::timestamptz, 'day', 1, 'native',
        10, 90, 100, 10.0,
        900.0, 10.0, 910.0, 10.0,
        'RUB', 75.0, 10.7,
        1000, 750, '2022-01-01T03:00+03:00'::timestamp),
       (2, '2021-12-07T03:00+03:00'::timestamptz, 'day', 1, 'native',
        10, 90, 100, 10.0,
        900.0, 10.0, 910.0, 10.0,
        'RUB', 75.0, 10.7,
        1000, 750, '2022-01-01T03:00+03:00'::timestamp),
       (2, '2021-12-06T03:00+03:00'::timestamptz, 'day', 1, 'native',
        10, 90, 100, 10.0,
        900.0, 10.0, 910.0, 10.0,
        'RUB', 75.0, 10.7,
        1000, 750, '2022-01-01T03:00+03:00'::timestamp);
