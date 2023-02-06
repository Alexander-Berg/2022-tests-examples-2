INSERT INTO logins(
    user_id,
    login,
    personal_user_id,
    personal_login
)
VALUES
(
    'user_id1', 'test_login', NULL, NULL
),
(
    'user_id2', 'not_existed', 'some_id5', 'not_existed_not_change'
)
;
