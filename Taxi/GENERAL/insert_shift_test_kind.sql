INSERT INTO persey_labs.shift_tests
(shift_id, test_id)
SELECT $1, UNNEST($2)
ON CONFLICT (shift_id, test_id) DO NOTHING;
