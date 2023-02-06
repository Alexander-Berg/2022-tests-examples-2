INSERT INTO clowny_search.imported_services
(clownductor_project, cluster_name, service_id, abc_slug, updated, cluster_type)
VALUES
('1', 'taxi_service_1_smth', 1, 'taxi1', '2014-04-04 20:00:00-07'::timestamptz, 'nanny'),
('1', 'taxi_service_2_smth', 2, 'taxi2', '2014-04-04 20:00:00-07'::timestamptz, 'nanny'),
('1', 'taxi_service_3_smth', 3, 'taxi3', '2014-04-04 20:00:00-07'::timestamptz, 'nanny'),
('1', 'taxi_service_4_smth', 4, 'taxi4', '2014-04-04 20:00:00-07'::timestamptz, 'nanny'),
('2', 'eda_service_1_smth', 5, 'eda1', '2014-04-04 20:00:00-07'::timestamptz, 'nanny'),
('2', 'eda_service_3_smth', 6, 'eda2', '2014-04-04 20:00:00-07'::timestamptz, 'nanny'),
('2', 'eda_service_5_smth', 7, 'eda3', '2014-04-04 20:00:00-07'::timestamptz, 'nanny'),
('144', 'old_service', 8, null, '2014-04-04 20:00:00-07'::timestamptz, 'nanny');


INSERT INTO clowny_search.imported_projects
(id, name)
VALUES
(1, 'test_project'),
(2, 'test_project');


INSERT INTO clowny_search.abc_members
(id, login, abc_slug)
VALUES
(1, 'elrusso', 'taxi1'),
(2, 'elrusso', 'taxi2'),
(3, 'elrusso', 'taxi3'),
(4, 'deoevgen', 'taxi1'),
(5, 'deoevgen', 'taxi2'),
(6, 'deoevgen', 'abc_slug_not_upstea'),
(7, 'elrusso', 'eda1');
