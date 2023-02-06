INSERT INTO 
scripts.tests(script_id, test_input, test_output, test_name)
(
  SELECT $1::int, test_input, test_output, test_name 
  FROM UNNEST($2::TEXT[], $3::TEXT[], $4::TEXT[]) as t(test_input, test_output, test_name)
);
