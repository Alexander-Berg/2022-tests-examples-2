INSERT INTO grocery_performer_mentorship.mentorship(newbie_id, newbie_shift_id, mentor_id, mentor_shift_id, status,
                                                    changes_counter)
VALUES ('123_101', '1002', '123_001', '1001', 'assigned', 1);

INSERT INTO grocery_performer_mentorship.shifts(shift_id, performer_id, depot_id, legacy_depot_id, started_at,
                                                closes_at, status)
VALUES ('1001', '123_001', 'FFFF123', '123', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + interval '4 hour', 'waiting'),
       ('1002', '123_101', 'FFFF123', '123', NULL, NULL,'closed');

INSERT INTO grocery_performer_mentorship.mentors(mentor_id, mentor_shifts_count, status)
VALUES ('123_001', 0, 'active');
