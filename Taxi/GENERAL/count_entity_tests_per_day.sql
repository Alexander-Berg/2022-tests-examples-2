SELECT
    COALESCE(SUM(tests_per_day), 0)
FROM persey_labs.labs
WHERE lab_entity_id = $1 AND is_active = TRUE;
