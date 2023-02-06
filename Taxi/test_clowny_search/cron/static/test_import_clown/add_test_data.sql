INSERT INTO clowny_search.imported_services
(clownductor_project, cluster_name, service_id, abc_slug, updated, cluster_type)
VALUES
('1', 'test_service', 1, 'test_slug', '2014-04-04 20:00:00-07'::timestamptz, 'nanny');



INSERT INTO clowny_search.imported_projects
(id, name)
VALUES
(1, 'test_project');
