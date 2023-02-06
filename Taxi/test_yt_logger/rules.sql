INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (1, 'common emits', 'return {metadata=["total_distance": trip.distance, "total_time": trip.time, "waiting_time": ride.ride.waiting_time, "waiting_in_transit_time": ride.ride.waiting_in_transit_time, "waiting_in_destination_time": ride.ride.waiting_in_destination_time]};', 'both_side', '200ok', 1, ''),
  (2, 'emit prev payment type', 'if (fix.payment_type as pt) { return {metadata=["is_cash": ((pt == "cash")?1:0)]}; } return {};', 'both_side', '200ok', 2, ''),
  (5, 'emit paid_supply_price', 'return {boarding=ride.price.boarding+100500};', 'both_side', '200ok', 3, '')
;
