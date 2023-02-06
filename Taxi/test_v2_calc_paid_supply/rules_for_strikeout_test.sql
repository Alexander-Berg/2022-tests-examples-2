INSERT INTO price_modifications.rules
(rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES (1, 'reduce_time_price_by_100', '', 'both_side', 'ioann-v', 1, ''),
       (2, 'paid_supply_addition', '', 'both_side', 'ioann-v', 2, ''),
       (3, 'half_paid_supply_addition', '', 'both_side', 'ioann-v', 3, ''),
       (4, 'strikeout_price_modifications', '', 'both_side', 'nik-carlson', 4, ''),
       (5, 'strikeout_price_modifications_1', '', 'both_side', 'nik-carlson', 5, ''),
       (6, 'strikeout_price_modifications_2', '', 'both_side', 'nik-carlson', 6, ''),
       (7, 'strikeout_price_modifications_3', '', 'taximeter_only', 'nik-carlson', 7, '')
;

UPDATE price_modifications.rules
SET source_code = 'let new_time = (ride.price.time > 100) ? ride.price.time - 100 : 0;
return {time = new_time};'
WHERE rule_id = 1;

UPDATE price_modifications.rules
SET source_code = 'if (fix.paid_supply_price as paid_supply_price) {
  return  ((*ride.price + paid_supply_price) / *ride.price) * ride.price;
}
return ride.price;'
WHERE rule_id = 2;

UPDATE price_modifications.rules
SET source_code = 'if (fix.paid_supply_price as paid_supply_price) {
  return ((*ride.price + paid_supply_price / 2) / *ride.price) * ride.price;
}
return ride.price;'
WHERE rule_id = 3;

UPDATE price_modifications.rules
SET source_code = 'if (fix.paid_supply_price as paid_supply_price) {
  return ((*ride.price + paid_supply_price / 2) / *ride.price) * ride.price;
}
return ride.price;'

WHERE rule_id = 4;

UPDATE price_modifications.rules
SET source_code = 'if (fix.paid_supply_price as paid_supply_price) {
  return ((*ride.price + paid_supply_price / 2) / *ride.price) * ride.price;
}
return ride.price;'

WHERE rule_id = 5;

UPDATE price_modifications.rules
SET source_code = 'if (fix.paid_supply_price as paid_supply_price) {
  return ((*ride.price + paid_supply_price / 2) / *ride.price) * ride.price;
}
return ride.price;'
WHERE rule_id = 6;

UPDATE price_modifications.rules
SET source_code = 'if (fix.paid_supply_price as paid_supply_price) {
  return ((*ride.price + paid_supply_price / 2) / *ride.price) * ride.price;
}
return ride.price;'
WHERE rule_id = 7;
