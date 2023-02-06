UPDATE
  state.shuttles
SET
  drw_state = 'Active'
WHERE
  shuttle_id = 1 OR shuttle_id = 2;

UPDATE
  state.shuttles
SET
  drw_state = 'Assigned'
WHERE
  shuttle_id = 4;
