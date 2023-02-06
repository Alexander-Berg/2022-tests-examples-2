UPDATE config.modes
SET offer_only = True,
    offer_radius = 111
WHERE mode_name = 'home'
;
