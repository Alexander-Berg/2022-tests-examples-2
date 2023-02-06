SELECT
    DISTINCT le.test_kind

FROM persey_labs.labs AS l
INNER JOIN persey_labs.addresses AS la ON l.address_id = la.id
INNER JOIN persey_labs.lab_entities AS le ON l.lab_entity_id = le.id
WHERE
    le.test_kind IS NOT NULL AND
    le.is_active AND
    l.is_active AND
    la.locality_id = $1;
