UPDATE config.modes
SET tags_permitted = ARRAY['permitted']
WHERE mode_name = 'home'
;
