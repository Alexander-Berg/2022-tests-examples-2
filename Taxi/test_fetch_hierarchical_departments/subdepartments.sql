INSERT INTO effrat_employees.subdepartments (
    name,
    department_id,
    department_url,
    department_level,
    ancestor_department_url
) VALUES 
  ('this department must be clean 2543-1', NULL, 'this_department_must_be_clean_2543_1', NULL, 'url_division_2543'),
  ('this department must be clean 2543-2', NULL, 'this_department_must_be_clean_2543_2', NULL, 'url_division_2543'),
  ('this department must be clean 3876', NULL, 'this_department_must_be_clean_3876', NULL, 'url_division_3876'),
  ('name url_division_10900', NULL, 'url_division_10900', NULL, 'url_division_3876'), -- this department should be updated
  ('this department must be left 1543', NULL, 'this_department_must_be_left_1543', NULL, 'url_division_1543')
  ;
