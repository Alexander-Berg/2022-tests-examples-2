INSERT INTO clowny_search.imported_services
(clownductor_project, cluster_name, service_id, abc_slug, updated)
VALUES
('1', 'clowny-perforator', 144, 'taxiinfraclownyperforator', '2014-04-04 20:00:00-07'::timestamptz ),
('1', 'clowny-search', 129, 'taxidevopsclownysearch', '2014-04-04 20:00:00-07'::timestamptz ),
('1', 'test_service_404', 139, 'taxidevservice404', '2014-04-04 20:00:00-07'::timestamptz )
;


INSERT INTO clowny_search.abc_members
(login, abc_slug)
VALUES
('elrusso', 'taxiinfraclownyperforator'),
('elrusso', 'taxidevopsclownysearch'),
('elrusso', 'taxidevservice404'),
('deoevgen', 'taxideoevgen_no'),
('eatroshkin', 'taxiinfraclownyperforator'),
('isharov', 'test_slug')
;
