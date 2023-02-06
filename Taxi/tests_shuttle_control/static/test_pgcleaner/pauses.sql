INSERT INTO state.pauses (
    pause_id,
    shuttle_id,
    pause_requested,
    expected_pause_start,
    pause_started,
    expected_pause_finish,
    pause_finished
) VALUES (
    1,
    1,
    '2020-05-28T11:40:55+0000',
    NULL,
    '2020-05-28T11:41:55+0000',
    NULL,
    '2020-05-28T11:45:55+0000'
), (
    2,
    1,
    '2020-05-28T12:40:55+0000',
    NULL,
    NULL,
    NULL,
    NULL
);

UPDATE state.shuttles
SET pause_state = 'requested',
    pause_id = 2
WHERE shuttle_id = 1;
