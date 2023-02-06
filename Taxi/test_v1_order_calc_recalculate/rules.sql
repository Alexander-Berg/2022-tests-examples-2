INSERT INTO price_modifications.rules (rule_id, name, source_code, policy, deleted, author, ast)
VALUES (2, 'price_x2', 'return ride.price*2;', 'both_side', false, 'pronin', '');
INSERT INTO price_modifications.rules (rule_id, name, source_code, policy, deleted, author, ast)
VALUES (1, 'price', 'return ride.price*1;', 'both_side', false, 'pronin', '');
INSERT INTO price_modifications.rules (rule_id, name, source_code, policy, deleted, author, ast)
VALUES (3, 'meta', 'return concat(ride.price*3, {metadata=["meta1": trip.distance]});', 'both_side', false, 'pronin', '');
INSERT INTO price_modifications.rules (rule_id, name, source_code, policy, deleted, author, ast)
VALUES (4, 'surge', 'return ride.price*fix.surge_params.value;', 'both_side', false, 'pronin', '');
