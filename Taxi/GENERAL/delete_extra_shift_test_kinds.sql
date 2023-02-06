DELETE FROM persey_labs.shift_tests
WHERE shift_id = $1 AND test_id NOT IN (SELECT(UNNEST($2)));
