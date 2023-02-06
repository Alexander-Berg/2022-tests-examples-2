UPDATE
  state.shuttles
SET
  drw_state = 'Active'
WHERE
  shuttle_id = 1;

UPDATE
  state.shuttles
SET
  drw_state = 'Assigned'
WHERE
  shuttle_id = 2;
