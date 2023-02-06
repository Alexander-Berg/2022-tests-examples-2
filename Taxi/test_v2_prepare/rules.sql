INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (
    1,
    'discount: 20% for econom, 10% for other categories',
    'if (fix.category == "econom") { return concat(ride.price * 0.8, {metadata=["discount_percent": 20]});} return concat(ride.price * 0.9, {metadata=["discount_percent": 10]});',
    'both_side',
    'ioann-v',
    1,
    ''
  )
;

INSERT INTO price_modifications.rules_drafts
  (rule_id, name, source_code, policy, author, approvals_id, ast, evaluate_on_prestable, prestable_evaluation_begin_time)
VALUES
  (
    2,
    'test draft',
    'return ride.price;',
    'both_side',
    'ioann-v',
    1,
    '',
    true,
    null
  )
;
