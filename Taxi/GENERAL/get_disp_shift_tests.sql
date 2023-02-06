SELECT
    test_id

FROM persey_labs.shift_tests
WHERE shift_id = $1;
