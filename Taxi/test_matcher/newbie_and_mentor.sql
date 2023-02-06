INSERT INTO grocery_performer_mentorship.mentorship(newbie_id)
VALUES ('123_101');

INSERT INTO grocery_performer_mentorship.shifts(shift_id, performer_id, depot_id, legacy_depot_id, started_at,
                                                closes_at, status)
VALUES  --- first part
       ('1001', '123_001', 'FFFF123', '123', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + interval '4 hour', 'waiting'),
       ('1002', '123_101', 'FFFF123', '123', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + interval '4 hour', 'waiting'),
       -- second part
       ('1004', '123_102', 'FFFF123', '123', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + interval '4 hour', 'waiting'),
       -- 123_002 is not a mentor
       ('1003', '123_002', 'FFFF123', '123', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + interval '4 hour', 'waiting'),
       ('1006', '123_003', 'FFFF123', '123', CURRENT_TIMESTAMP + interval '4 hour', CURRENT_TIMESTAMP + interval
           '7 hour', 'waiting'),
       ('1005', '123_103', 'FFFF123', '123', CURRENT_TIMESTAMP + interval '4 hour',
        CURRENT_TIMESTAMP + interval '7 hour',
        'waiting');

INSERT INTO grocery_performer_mentorship.mentors(mentor_id, mentor_shifts_count, status)
VALUES ('123_001', 0, 'active'),
       ('123_003', 0, 'active');
