INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast, updated)
VALUES
  ({new_id}, '{name}', 'return ride.price;', 'both_side', '200ok', {approvals_id}, '', '{updated}')
;

UPDATE price_modifications.workabilities SET rule_id={new_id} WHERE rule_id={old_id};
