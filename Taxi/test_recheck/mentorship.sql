INSERT INTO grocery_performer_mentorship.mentorship(newbie_id, newbie_shift_id, mentor_id, mentor_shift_id, status, changes_counter )
VALUES ('123_101', '1002', '123_001', '1001', 'assigned', 1),
       ('123_102', '1004', '123_002', '1003', 'assigned', 1),
       ('123_103', '1005', NULL, NULL, 'assigned', 0);

INSERT INTO grocery_performer_mentorship.shifts(shift_id, performer_id, depot_id, legacy_depot_id, started_at,
                                                closes_at, status)
VALUES ('1001', '123_001', 'FFFF123', '123', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + interval '4 hour', 'waiting'),
       ('1003', '123_110', 'FFFF123', '123', CURRENT_TIMESTAMP + interval '3 hour', CURRENT_TIMESTAMP + interval
           '7 hour', 'waiting'),
       ('1002', '123_101', 'FFFF123', '123', CURRENT_TIMESTAMP + interval '2 hour',
        CURRENT_TIMESTAMP + interval '6 hour',
        'waiting'),
       ('1004', '123_102', 'FFFF123', '123', CURRENT_TIMESTAMP + interval '4 hour',
        CURRENT_TIMESTAMP + interval '8 hour',
        'waiting'),
       ('1005', '123_103', 'FFFF123', '123', CURRENT_TIMESTAMP + interval '7 hour',
        CURRENT_TIMESTAMP + interval '11 hour',
        'waiting');

INSERT INTO grocery_performer_mentorship.mentors(mentor_id, mentor_shifts_count, status)
VALUES ('123_001', 0, 'active'),
       ('123_002', 0, 'active');
