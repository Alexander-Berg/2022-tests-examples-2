INSERT INTO price_modifications.rules (rule_id, name, source_code, ast, policy, author) VALUES
  (1, 'foo', 'let meta = ["additional_foo": 1.0, "only_for_agent_foo": 2.0, "only_for_response_foo": 3.0]; return {metadata = meta};', '', 'both_side', '200ok')
;
