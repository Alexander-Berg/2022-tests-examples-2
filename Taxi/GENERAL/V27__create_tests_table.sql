CREATE TABLE price_modifications.tests (
  test_name TEXT NOT NULL,
  backend_variables JSON NOT NULL,
  trip_details JSON NOT NULL,
  initial_price JSON NOT NULL,
  output_price JSON,
  output_meta JSON,
  last_result BOOLEAN DEFAULT NULL,
  last_result_rule_id BIGINT REFERENCES price_modifications.rules (rule_id) DEFAULT NULL,
  rule_name TEXT NOT NULL,
  PRIMARY KEY(rule_name, test_name)
);
