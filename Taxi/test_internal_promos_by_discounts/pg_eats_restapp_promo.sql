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
     (301, array['1', '2']::TEXT[], 'one_plus_one', 'approved',
     '2022-01-01 00:00:00 +00:00', '2022-02-01 00:00:00 +00:00',
     '{"requirements":[]}', '{"bonuses":[]}', NULL,
     current_timestamp, '', array['11']::TEXT[]),
     (302, array['1', '2']::TEXT[], 'gift', 'approved',
     '2022-01-01 00:00:00 +00:00', '2022-02-01 00:00:00 +00:00',
     '{"requirements":[]}', '{"bonuses":[]}', NULL,
     current_timestamp, '', array['12']::TEXT[]),
     (303, array['1', '2']::TEXT[], 'discount', 'approved',
     '2022-01-01 00:00:00 +00:00', '2022-02-01 00:00:00 +00:00',
     '{"requirements":[]}', '{"bonuses":[]}', NULL,
     current_timestamp, '', array['13']::TEXT[]),
     (304, array['1', '2']::TEXT[], 'free_delivery', 'approved',
     '2022-01-01 00:00:00 +00:00', '2022-02-01 00:00:00 +00:00',
     '{"requirements":[]}', '{"bonuses":[]}', NULL,
     current_timestamp, '', array['14']::TEXT[]),
     (305, array['1', '2']::TEXT[], 'plus_happy_hours', 'approved',
     '2022-01-01 00:00:00 +00:00', '2022-02-01 00:00:00 +00:00',
     '{"requirements":[]}', '{"bonuses":[]}', NULL,
     current_timestamp, '', array['15']::TEXT[]),
     (306, array['1', '2']::TEXT[], 'plus_first_orders', 'approved',
     '2022-01-01 00:00:00 +00:00', '2022-02-01 00:00:00 +00:00',
     '{"requirements":[]}', '{"bonuses":[]}', NULL,
     current_timestamp, '', array['16', '26']::TEXT[]);