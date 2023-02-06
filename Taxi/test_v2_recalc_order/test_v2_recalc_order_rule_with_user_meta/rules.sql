INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (1, 'rule#1', '
    using(UserMeta) {
    if ("foo" in ride.ride.user_meta) {
     return {metadata=["foo": 1]};
    } else {
     return {metadata=["foo": 0]};
    }
    }
    return ride.price;
', 'both_side', '200ok', 1, '')
;
