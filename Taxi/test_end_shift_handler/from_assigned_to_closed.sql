INSERT INTO grocery_performer_mentorship.mentorship(newbie_id, newbie_shift_id, mentor_id, mentor_shift_id, status,
                                                    notifications)
VALUES ('123_101', '1002', '123_001', '1001', 'assigned',
        ('{mentor,newbie}')::grocery_performer_mentorship.end_mentor_shift_notification_v1[]);

INSERT INTO grocery_performer_mentorship.shifts(shift_id, performer_id, depot_id, legacy_depot_id, started_at,
                                                closes_at, status)
VALUES ('1001', '123_001', 'FFFF123', '123', CURRENT_TIMESTAMP - interval '4 hour',
        CURRENT_TIMESTAMP - interval '1 minute', 'closed'),
       ('1002', '123_101', 'FFFF123', '123', CURRENT_TIMESTAMP - interval '4 hour',
        CURRENT_TIMESTAMP - interval '1 minute', 'closed');

INSERT INTO grocery_performer_mentorship.mentors(mentor_id, mentor_shifts_count, status)
VALUES ('123_001', 0, 'active');
