INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at) VALUES
('justmark0', 100500, NOW(), 'Mark', 'Nicholson', NOW()),
('romford', 100500, NOW(), 'Alexander', 'Fedotov', NOW()),
('webalex', 100500, NOW(), 'Alexander', 'Ivanov', NOW()),
('no_access_user', 100500, NOW(), 'no_access_user', 'no_access_user', NOW());

INSERT INTO agent.channels(
    key,
    created,
    creator,
    name,
    deleted,
    description,
    avatar,
    public
)
VALUES
(
    'private_channel',
    '2020-01-01 10:00:00',
    'webalex',
    'private_channel_name',
    FALSE,
    'private_channel_description',
    'avatar_id',
    False
),
(
    'channel_1',
    '2020-01-01 10:00:00',
    'webalex',
    'channel_1_name',
    FALSE,
    'channel_1_description',
    'avatar_id',
    True
);

INSERT INTO agent.channel_admins(
    login,
    channel_key
)
VALUES (
        'webalex',
        'private_channel'
       ),
       (
        'webalex',
        'channel_1'
       );

INSERT INTO agent.news
(
    id,
    created,
    text,
    deleted,
    creator,
    images,
    format
) VALUES
('post1', NOW(),'text', False, 'webalex', NULL, 'text'),
('post2', NOW(),'text', False, 'webalex', NULL, 'text'),
('private_channel_post', NOW(),'text', False, 'webalex', NULL, 'text');

INSERT INTO agent.post_favorites (post_id, login, dttm) VALUES
('post2', 'webalex', NOW());

INSERT INTO agent.channel_posts
(
    channel_id,
    post_id
) VALUES
('channel_1','post1'),
('channel_1','post2'),
('private_channel','private_channel_post');
