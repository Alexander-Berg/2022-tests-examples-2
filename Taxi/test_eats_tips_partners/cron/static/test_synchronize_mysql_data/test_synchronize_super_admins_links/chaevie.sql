INSERT INTO modx_web_users (id, username)
VALUES
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (100, '100'),
    (105, '105')
;


INSERT INTO modx_web_groups (webuser, webgroup)
VALUES
    (1, 2),
    (2, 2),
    (3, 2),
    (4, 2),
    (4, 1),
    (100, 10),
    (105, 10)
;


INSERT INTO modx_s_admin_to_admin_point (id, user_id, to_user_id)
VALUES
    (1, 2, 100),
    (2, 3, 100),
    (3, 3, 101),
    (4, 2, 103)
;
