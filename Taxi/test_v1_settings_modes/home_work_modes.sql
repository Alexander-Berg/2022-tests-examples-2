UPDATE config.modes
  SET work_modes = ARRAY['driver-fix']
  WHERE mode_name = 'home';
