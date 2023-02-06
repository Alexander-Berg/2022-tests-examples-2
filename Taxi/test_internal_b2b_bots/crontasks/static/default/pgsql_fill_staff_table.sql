DELETE FROM internal_b2b.telegram_staff;

INSERT INTO internal_b2b.telegram_staff
(
    login,
    chiefs,
    telegram_account
) VALUES
(
    'staff_user_login_1',
    '{"login": "chef_login_1"}',
    'telegram_account_1'
),(
    'staff_user_login_2',
    '{"login": "chef_login_2"}',
    'telegram_account_2'
),(
    'staff_user_login_3',
    '{"login": "chef_login_3"}',
    'telegram_account_3'
),(
    'staff_user_login_4',
    '{"login": "chef_login_4"}',
    'telegram_account_4'
)
