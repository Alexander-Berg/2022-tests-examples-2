INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    join_at,
    piece,
    country
)
VALUES (
    1120000000252888,
     NOW(),
    'webalex',
    'Александр',
    'Иванов',
    '2016-06-02',
    false,
    null
),
(
    1120000000252888,
     NOW(),
    'dublicate_login',
    'test',
    'test',
    '2016-06-02',
    false,
    null
),
(
    1120000000252888,
     NOW(),
    'evrum',
    'Евгений',
    'Румянцев',
    '2016-06-02',
    false,
    null
);


INSERT INTO agent.dismissed_users VALUES
(
 'id432423423423',
 'dublicate_login',
 '2019-01-05',
 'webalex',
 'taxi',
 'taxi',
 '{"user_call_taxi"}',
 'new',
 '2019-01-01 00:00:00',
 null
),
(
 'id432423423995',
 'evrum',
 '2019-01-10',
 'webalex',
 'taxi',
 'taxi',
 '{"user_call_taxi"}',
 'new',
 '2019-01-01 00:00:00',
 null
);

