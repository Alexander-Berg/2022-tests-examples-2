UPDATE config.modes
SET geo_nodes_permitted = ARRAY['permitted']
WHERE mode_name = 'home'
;
