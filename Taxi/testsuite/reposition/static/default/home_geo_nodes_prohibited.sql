UPDATE config.modes
SET geo_nodes_prohibited = ARRAY['prohibited']
WHERE mode_name = 'home'
;
