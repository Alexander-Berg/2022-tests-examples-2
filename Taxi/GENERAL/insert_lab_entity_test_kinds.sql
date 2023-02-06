INSERT INTO persey_labs.lab_entity_tests
(lab_entity_id, test_id)
SELECT $1, UNNEST($2)
ON CONFLICT (lab_entity_id, test_id) DO NOTHING;
