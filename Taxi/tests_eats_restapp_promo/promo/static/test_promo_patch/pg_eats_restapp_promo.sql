INSERT INTO eats_restapp_promo.promos (
    promo_id,
    place_ids,
    promo_type,
    status,
    starts,
    ends,
    requirements,
    bonuses,
    schedule,
    set_at,
    discount_task_id,
    discount_ids
)
VALUES
    (228, array['1', '2']::TEXT[], 'plus_first_orders', 'approved',
     '2020-11-25 18:43:00 +03:00', '2021-11-25 18:43:00 +03:00',
     '{"requirements":[{"min_order_price":50.5}]}',
     '{"bonuses":[{"cashback":[20,10,5]}]}',
     NULL,
     current_timestamp, 1, array['aboba']),
    (229, array['1', '2']::TEXT[], 'plus_first_orders', 'approved',
     '2020-11-25 18:43:00 +03:00', '2021-11-25 18:43:00 +03:00',
     '{"requirements":[{"min_order_price":50.5}]}',
     '{"bonuses":[{"cashback":[20,10,5]}]}',
     NULL,
     current_timestamp, 1, NULL),
    (2304, array['1', '2']::TEXT[], 'plus_first_orders', 'completed',
     '2020-11-25 18:43:00 +03:00', '2021-11-25 18:43:00 +03:00',
     '{"requirements":[{"min_order_price":50.5}]}',
     '{"bonuses":[{"cashback":[20,10,5]}]}',
     NULL,
     current_timestamp, 1, array['aboba'])