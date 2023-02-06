INSERT INTO agent.users (
    uid,
    created,
    login,
    first_name,
    last_name,
    join_at
)
VALUES (
    1120000000252888,
     NOW(),
    'webalex',
    'Александр',
    'Иванов',
    '2016-06-02'
);

INSERT INTO agent.news(
    created,
    title,
    text,
    creator,
    tags,
    deleted
)

VALUES (

    NOW(),
    'Test new #1',
    'Test text #1',
    'webalex',
    '[]',
    false
);
