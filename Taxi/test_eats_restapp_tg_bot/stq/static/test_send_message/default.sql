INSERT INTO logins
(user_id, login)
VALUES
(
    'some_user_id1', 'existed1'
),
(
    'some_user_id2', 'existed2'
);

INSERT INTO logins
(user_id, login, personal_user_id, personal_login)
VALUES
(
    'some_user_id3', 'existed3', 'personal_1', 'login_1'
),
(
    'some_user_id4', 'existed4', 'personal_2', 'login_2'
)
;
