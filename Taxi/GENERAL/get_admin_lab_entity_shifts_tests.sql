SELECT
    st.test_id

FROM persey_labs.labs AS l
INNER JOIN persey_labs.lab_employees AS le ON le.lab_id = l.id
INNER JOIN persey_labs.lab_employee_shifts AS s ON s.lab_employee_id = le.id
INNER JOIN persey_labs.shift_tests AS st ON st.shift_id = s.id
WHERE l.lab_entity_id = $1;
