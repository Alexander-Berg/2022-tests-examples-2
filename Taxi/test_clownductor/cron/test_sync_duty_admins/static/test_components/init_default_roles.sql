INSERT INTO permissions.roles (login, role, service_id, project_id, is_super)
VALUES
('d1mbas-super', 'nanny_admin_prod', NULL, NULL, TRUE),
('d1mbas-service_1_t', 'nanny_admin_testing', 1, NULL, FALSE),
('d1mbas-service_1_s', 'nanny_admin_prod', 1, NULL, FALSE),
('d1mbas-project_1_t', 'nanny_admin_testing', NULL, 1, FALSE),
('d1mbas-project_1_s', 'nanny_admin_prod', NULL, 1, FALSE)
;
