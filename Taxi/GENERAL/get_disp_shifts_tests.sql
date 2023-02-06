SELECT
    shift_id,
    test_id

FROM persey_labs.shift_tests
WHERE shift_id = ANY($1);
