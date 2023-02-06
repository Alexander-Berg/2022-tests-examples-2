DELETE FROM persey_labs.lab_entity_tests
WHERE lab_entity_id = $1 AND test_id NOT IN (SELECT(UNNEST($2)));
