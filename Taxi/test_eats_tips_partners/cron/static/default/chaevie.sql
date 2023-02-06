INSERT INTO modx_web_users (id, username)
VALUES
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (10, '10'),
    (11, '11'),
    (12, '12'),
    (13, '13'),
    (14, '14'),
    (15, '15'),
    (16, '16'),
    (17, '17'),
    (18, '18'),
    (19, '19'),
    (30, '30'),
    (40, '40'),
    (50, '50'),
    (51, '51'),
    (100, '100')
;


INSERT INTO modx_web_groups (webuser, webgroup)
VALUES
       (1, 2),
       (2, 2),
       (3, 2),
       (4, 2),
       (4, 1),

       (10, 1),
       (11, 1),
       (12, 1),
       (13, 1),
       (14, 1),
       (15, 1),
       (16, 1),
       (17, 1),
       (18, 1),
       (19, 1),
       (30, 5), -- номер в отеле
       (40, 6),
       (50, 13),    -- непредвиденная роль
       (51, 13),    -- непредвиденная роль с привязкой к админу
       (100, 10)
;


INSERT INTO modx_event_log (id, eventid, type, source, description)
VALUES
    (1, 500, 1, 'change_user_role', '1'),
    (2, 500, 1, 'change_user_role', '10'),
    (3, 500, 1, 'change_user_role', '3')
;


INSERT INTO modx_s_admin_to_admin_point (id, user_id, to_user_id)
VALUES
    (1, 2, 100)
;
