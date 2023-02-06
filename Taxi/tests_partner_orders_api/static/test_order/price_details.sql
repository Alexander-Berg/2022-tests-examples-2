INSERT INTO partner_orders_api.order_price_details(
  order_id,
  details_set_id,
  calculated_at
)
VALUES (
  'a88b3d49a8c24681bbf8d93cd158d8df',
  'details_id',
  '2020-12-26T20:10:00+0000'::timestamptz
), (
  'a88b3d49a8c24681bbf8d93cd158d8df',
  'another_details_id',
  '2020-12-26T20:00:00+0000'::timestamptz -- earlier, should be ignored
);

INSERT INTO partner_orders_api.price_details_items(
  details_set_id,
  price,
  item_name
)
VALUES
  ('details_id', 10, 'paid_wating'),
  ('details_id', 11.5, 'animalstransport'),
  ('details_id', 20, 'booster'),
  ('details_id', 30, 'big_booster'),
  ('details_id', 50, 'surge'),
  ('another_details_id', 1000, 'smoke_cigarettes') -- should not be counted
;
