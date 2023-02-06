
INSERT INTO callcenter_operators.operators_shifts_drafts
    (
        unique_operator_id,
        draft_id,
        shift_id,
        start,
        duration_minutes,
        status
    )
VALUES
    (
        1,
        '1',
        1,
        '2020-07-26 12:00:00.0 +0000',
        30,
        0
    ),
    (
        2,
        '2',
        3,
        '2020-07-26 18:00:00.0 +0000',
        600,
        1
    );
