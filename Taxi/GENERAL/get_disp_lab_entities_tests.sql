SELECT
    lab_entity_id,
    test_id

FROM persey_labs.lab_entity_tests
WHERE lab_entity_id = ANY($1);
