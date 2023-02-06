INSERT INTO supportai.events (created, project_id, user_id, type, object_type, object_id, object_description)
VALUES
('2021-08-31 09:59:01+03', 1, 1, 'create', 'scenario', '1', 'Some scenario'),
('2021-08-30 09:59:01+03', 1, 1, 'create', 'feature', '1', 'Some feature'),
('2021-08-29 09:59:01+03', 1, 4, 'delete', 'scenario', '1', 'Another scenario'),
('2021-08-29 09:59:01+03', 1, 1, 'update', 'scenario', '1', 'Some scenario');
