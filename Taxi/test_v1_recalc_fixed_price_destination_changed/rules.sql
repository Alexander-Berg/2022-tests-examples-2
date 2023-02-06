INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (1, 'common emits', 'return {metadata=["total_distance": trip.distance, "total_time": trip.time, "waiting_time": ride.ride.waiting_time, "waiting_in_transit_time": ride.ride.waiting_in_transit_time, "waiting_in_destination_time": ride.ride.waiting_in_destination_time]};', 'both_side', '200ok', 1, ''),
  (2, 'emit paid_supply_price', 'if (fix.paid_supply_price as paid_supply_price) {return {metadata=["paid_supply_price": paid_supply_price]};} else {return {metadata=["no_paid_supply": 0]};}return ride.price;', 'both_side', '200ok', 2, ''),
  (3, 'broken prices', 'return {boarding=-1};', 'both_side', '200ok', 3, '')
;
