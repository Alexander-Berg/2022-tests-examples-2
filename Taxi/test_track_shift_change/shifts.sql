INSERT INTO grocery_performer_mentorship.shifts(shift_id, performer_id,
                                                depot_id, legacy_depot_id, 
                                                started_at,
                                                closes_at,
                                                status)
VALUES ('100', '123_001', 'FFF_123', '123', CURRENT_TIMESTAMP + interval '1 hour', CURRENT_TIMESTAMP + interval '2 hour',
        'waiting'),
    ('101', '123_101', 'FFF_123', '123', CURRENT_TIMESTAMP + interval '1 hour', CURRENT_TIMESTAMP + interval '2 hour',
        'waiting');

INSERT INTO grocery_performer_mentorship.mentorship(newbie_id, newbie_shift_id, mentor_id, mentor_shift_id, status)
VALUES ('123_101', '101' , '123_001', '100', 'assigned');
