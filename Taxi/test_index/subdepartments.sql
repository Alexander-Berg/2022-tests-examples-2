INSERT INTO effrat_employees.subdepartments (
    name,
    department_id,
    department_url,
    department_level,
    ancestor_department_url
) VALUES 
  ('url division 1', NULL, 'url_division_1', 1, 'url_division_0'),
  ('url division 2', NULL, 'url_division_2', 2, 'url_division_1'),
  ('url sub-division 3', NULL, 'url_subdivision_3', 2, 'url_subdivision_0')
  ;
