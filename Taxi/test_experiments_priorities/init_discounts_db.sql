INSERT INTO grocery_discounts.experiments_orders(id, experiments, updated_at)
VALUES
(511, ARRAY['second', 'third']::text[], '2020-07-18 10:00:00.000+03'),
(411, ARRAY['third', 'second']::text[], '2020-07-12 10:00:00.000+03');
