INSERT INTO grocery_performer_mentorship.mentorship(newbie_id, status, pending_since)
VALUES ('100_100', 'pending', CURRENT_TIMESTAMP - interval '5 minutes'),
       ('101_101', 'pending', CURRENT_TIMESTAMP - interval '2 hour'),
       ('102_102', 'assigned', CURRENT_TIMESTAMP - interval '2 hour');
