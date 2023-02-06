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




INSERT INTO agent.channel_category VALUES ('category_1','category_1_name');

INSERT INTO agent.channels
(
    key,
    category,
    created,
    creator,
    name,
    deleted,
    description,
    permissions
)
VALUES
(
 'dublicate',
 'category_1',
 '2021-01-01 00:00:00',
 'webalex',
 'Дубликат',
 false,
 'test',
 ARRAY['test']

);
