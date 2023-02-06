INSERT INTO userstats.processed_orders (identity_type, order_id, created_at)
VALUES
  ('phone_id', 'order1', '2020-08-03 11:59:00+03'),
  -- order2 попадает в -1 день, но из-за округления дожен остаться в базе
  ('phone_id', 'order2', '2020-08-03 12:09:00+03'),
  ('phone_id', 'order3', '2020-08-10 12:10:00+03')
;
