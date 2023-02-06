INSERT INTO price_modifications.rules
  (rule_id, name, source_code, policy, author, approvals_id, ast)
VALUES
  (
    1,
    'pcc_analyzer',
    '
if (fix.previously_calculated_categories as pcc) {
  if ("business" in pcc) {
    return {metadata=["business_in_pcc": 1]};
  }
  return {metadata=["business_not_in_pcc": 1]};
}
return {metadata=["no_pcc": 1]};
',
    'both_side',
    'ioann-v',
    1,
    ''
  )
;
