insert into eats_retail_market_integration.orders (
    eater_id, order_nr, created_at
) values
  ('1', '1', now()),
  ('1', '2', now() - interval '1 days'),
  ('1', '3', now() - interval '2 days'),
  ('1', '4', now() - interval '3 days'),
  ('1', '5', now() - interval '4 days'),
  ('1', '6', now() - interval '5 days'),
  ('2', '7', now() - interval '10 days'),
  ('2', '8', now()  - interval '30 days'),
  ('3', '9', now() - interval '5 years');
