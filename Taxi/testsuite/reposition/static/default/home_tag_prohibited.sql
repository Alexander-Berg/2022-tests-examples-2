UPDATE config.modes
SET tags_prohibited = ARRAY['prohibited']
WHERE mode_name = 'home'
;
