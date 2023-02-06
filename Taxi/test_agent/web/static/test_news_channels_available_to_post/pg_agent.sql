INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at) VALUES
('justmark0', 100500, NOW(), 'Mark', 'Nicholson', NOW()),
('webalex', 100500, NOW(), 'Alexander', 'Ivanov', NOW());

INSERT INTO agent.channels(
    key,
    created,
    creator,
    name,
    deleted,
    description,
    avatar
)
VALUES
       (
        'channel_1',
        '2020-01-01 10:00:00',
        'webalex',
        'channel_1_name',
        FALSE,
        'channel_1_description',
        'avatar_id'
       ),
       (
        'channel_2',
        '2020-01-01 10:00:00',
        'justmark0',
        'channel_2_name',
        FALSE,
        'channel_2_description',
        'avatar_id'
       ),
       (
        'channel_3',
        '2020-01-01 10:00:00',
        'webalex',
        'channel_3_name',
        True,
        'channel_3_description',
        'channel_3_avatar_id'
       );

INSERT INTO agent.channel_admins(
    login,
    channel_key
)
VALUES (
        'justmark0',
        'channel_1'
       ),
       (
        'justmark0',
        'channel_2'
       ),
       (
        'justmark0',
        'channel_3'
       );
