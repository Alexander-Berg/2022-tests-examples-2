INSERT INTO price_modifications.rules (rule_id, name, source_code, ast, policy, author) VALUES
  (1, 'foo', 'let meta = ["additional_foo": 1.0, "only_for_agent_foo": 2.0, "only_for_response_foo": 3.0]; return {metadata = meta};', '', 'both_side', '200ok'),
  (2, 'bar', 'if (fix.forced_skip_label as fs) { if (fs == handlers::libraries::pricing_functions::ForcedSkipLabel::kWithoutSurge) { return {boarding = 153.5}; } } return {boarding = 133.5};', '', 'both_side', '200ok')
;
