INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (1, 'return_time', 'return concat(ride.price * (trip.time / *ride.price), {metadata=["dummy": 42]});', 'both_side', '200ok', 16, ''),
  (2, 'return_price', 'return ride.price;', 'both_side', '200ok', 17, ''),
  (3, 'up strikeout', 'return {boarding=ride.price.boarding + 30.0};', 'both_side', '200ok', 18, '')
;
