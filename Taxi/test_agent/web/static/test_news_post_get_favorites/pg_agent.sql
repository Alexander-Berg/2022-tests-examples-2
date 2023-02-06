INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at) VALUES
('justmark0', 100500, '2022-01-01 00:00:00', 'Mark', 'Nicholson', '2022-01-01 00:00:00'),
('romford', 100500, '2022-01-01 00:00:00', 'Alexander', 'Fedotov', '2022-01-01 00:00:00'),
('webalex', 100500, '2022-01-01 00:00:00', 'Alexander', 'Ivanov', '2022-01-01 00:00:00'),
('no_access_user', 100500, '2022-01-01 00:00:00', 'no_access_user', 'no_access_user', '2022-01-01 00:00:00');


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
        'channel_1',
        '2020-01-01 10:00:00',
        'justmark0',
        'channel_1_name',
        FALSE,
        'channel_1_description',
        'avatar_id',
        True
       ),
       (
        'channel_2',
        '2020-01-01 10:00:00',
        'justmark0',
        'channel_2_name',
        FALSE,
        'channel_2_description',
        'avatar_id',
        True
       ),
       (
        'private_channel',
        '2020-01-01 10:00:00',
        'justmark0',
        'private_channel_name',
        FALSE,
        'private_channel_description',
        'avatar_id',
        FALSE
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
       );

INSERT INTO agent.news
(
    serial,
    id,
    created,
    text,
    deleted,
    creator,
    images,
    format
) VALUES
(1,'post_1', '2022-01-01 00:00:00','text', False, 'justmark0', NULL, 'text'),
(2,'post_2', '2022-01-01 00:00:00','text', False, 'justmark0', '{image_1}', 'text'),
(3,'post_3', '2022-01-01 00:00:00','text', True, 'justmark0', '{}', ''),
(4,'post_4', '2022-01-01 00:00:00','text', False, 'justmark0', '{}', ''),
(5,'post_5', '2022-01-01 00:00:00','text', False, 'justmark0', NULL, 'text'),
(6,'post_6', '2022-01-01 00:00:00','text', False, 'justmark0', NULL, 'text');


INSERT INTO agent.channel_posts
(
    channel_id,
    post_id
) VALUES
('channel_1','post_1'),
('channel_2','post_1'),
('channel_1','post_2'),
('channel_2','post_3'),
('channel_1','post_3'),
('channel_2','post_4'),
('channel_2','post_5'),
('private_channel','post_6');

INSERT INTO agent.post_favorites (serial, post_id, login, dttm) VALUES
(1,'post_1', 'justmark0', '2022-01-01 00:00:00'),
(2,'post_2', 'justmark0', '2022-01-02 00:00:00'),
(3,'post_3', 'justmark0', '2022-01-03 00:00:00'),
(4,'post_5', 'justmark0', '2022-01-04 00:00:00'),
(5,'post_5', 'webalex', '2022-01-04 00:00:00'),
(6,'post_1', 'webalex', '2022-01-01 00:00:00'),
(7,'post_3', 'webalex', '2022-01-02 00:00:00'),
(8,'post_4', 'webalex', '2022-01-03 00:00:00'),
(9,'post_6', 'no_access_user', '2022-01-03 00:00:00');

INSERT INTO agent.post_likes
(
    post_id,
    login,
    dt
) VALUES
( 'post_1','justmark0', '2022-01-01 00:00:00');


INSERT INTO agent.post_views
(
    post_id,
    login,
    dt
) VALUES
( 'post_1','justmark0', '2022-01-01 00:00:00');
