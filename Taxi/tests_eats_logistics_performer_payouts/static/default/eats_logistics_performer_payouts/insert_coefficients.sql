INSERT
INTO eats_logistics_performer_payouts.coefficients_values (country_id, region_id, pool, courier_type, coefficients)
VALUES ('1', '__default__', 'eda', 'pedestrian', '{"fine_thresh_late": 10}'),
       ('1', '1', 'eda', 'pedestrian', '{"fine_thresh_early": 10}'),
       ('1', '1', 'shop', 'picker', '{"fine_thresh_early": 10}'),
       ('1', '2', 'eda', 'pedestrian', '{}');
