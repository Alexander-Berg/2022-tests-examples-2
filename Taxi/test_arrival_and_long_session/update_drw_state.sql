UPDATE state.sessions
SET drw_state = 'Active'
WHERE session_id = ANY(ARRAY[1502, 1505, 1506])
