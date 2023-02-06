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
    'team_1_lead',
    'team_1_lead',
    'team_1_lead',
    '2016-06-02'
),(
    1120000000252888,
     NOW(),
    'team_2_lead',
    'team_2_lead',
    'team_2_lead',
    '2016-06-02'
),(
    1120000000252888,
     NOW(),
    'team_3_lead',
    'team_3_lead',
    'team_3_lead',
    '2016-06-02'
),(
    1120000000252888,
     NOW(),
    'subscribed_user',
    'subscribed_user',
    'subscribed_user',
    '2016-06-02'
),(
    1120000000252888,
     NOW(),
    'user_subscribed_via_project',
    'user_subscribed_via_project',
    'user_subscribed_via_project',
    '2016-06-02'
),(
    1120000000252888,
     NOW(),
    'not_subscribed_user',
    'not_subscribed_user',
    'not_subscribed_user',
    '2016-06-02'
),(
    1120000000252888,
     NOW(),
    'user_subscribed_via_team_and_manually',
    'user_subscribed_via_team_and_manually',
    'user_subscribed_via_team_and_manually',
    '2016-06-02'
),(
    1120000000252888,
     NOW(),
    'feed_test_user',
    'feed_test_user',
    'feed_test_user',
    '2016-06-02'
),(
    1120000000252888,
     NOW(),
    'no_access_user',
    'no_access_user',
    'no_access_user',
    '2016-06-02'
);

INSERT INTO agent.permissions (key,created,creator,ru_name,en_name,en_description,ru_description) VALUES
('permission_1',NOW(),'team_1_lead','permission_1','permission_1','permission_1','permission_1'),
('news_create_channel',NOW(),'team_1_lead','permission_1','permission_1','permission_1','permission_1'),
('user_project_1',NOW(),'team_1_lead','permission_1','permission_1','permission_1','permission_1'),
('user_project_2',NOW(),'team_1_lead','permission_1','permission_1','permission_1','permission_1');

INSERT INTO agent.teams
(key,name,en_name,permission,piece)
VALUES
('team_1','team_1','team_1','permission_1',true),
('team_2','team_2','team_2','permission_1',true),
('team_3','team_3','team_3','permission_1',true),
('team_4','team_4','team_4','permission_1',true),
('team_5','team_5','team_5','permission_1',true);

UPDATE agent.users SET team='team_1' WHERE login IN ('team_1_lead');
UPDATE agent.users SET team='team_2' WHERE login IN ('team_2_lead');
UPDATE agent.users SET team='team_3' WHERE login IN ('team_3_lead');
UPDATE agent.users SET team='team_4' WHERE login IN ('user_subscribed_via_team_and_manually');
UPDATE agent.users SET team='team_5' WHERE login IN ('feed_test_user');


INSERT INTO agent.roles VALUES
(
 'can_create_channel_role',
 '2021-01-01 00:00:00',
 null,
 'team_1_lead',
 'can_create_channel_role',
 'can_create_channel_role',
 'can_create_channel_role',
 'can_create_channel_role',
 true
),
(
 'project_1_role',
 '2021-01-01 00:00:00',
 null,
 'team_1_lead',
 'project_1_role',
 'project_1_role',
 'project_1_role',
 'project_1_role',
 true
),
(
 'project_2_role',
 '2021-01-01 00:00:00',
 null,
 'feed_test_user',
 'project_2_role',
 'project_2_role',
 'project_2_role',
 'project_2_role',
 true
);

INSERT INTO agent.roles_permissions VALUES
(
 'can_create_channel_role',
 'news_create_channel',
 '2021-01-01 00:00:00',
 'team_1_lead'
),
(
 'project_1_role',
 'user_project_1',
 '2021-01-01 00:00:00',
 'team_1_lead'
),
(
 'project_2_role',
 'user_project_2',
 '2021-01-01 00:00:00',
 'feed_test_user'
);


INSERT INTO agent.users_roles
(
 created,
 login,
 key
 )
VALUES
(
'2020-01-01 00:00:00',
'team_1_lead',
'can_create_channel_role'
),
(
'2020-01-01 00:00:00',
'user_subscribed_via_project',
'project_1_role'
),
(
'2020-01-01 00:00:00',
'feed_test_user',
'project_2_role'
);

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
        'team_1_lead',
        'channel_1_name',
        FALSE,
        'channel_1_description',
        'avatar_id',
        True
       ),
       (
        'channel_2',
        '2020-01-01 10:00:00',
        'team_1_lead',
        'channel_2_name',
        FALSE,
        'channel_2_description',
        'avatar_id',
        True
       ),
       (
        'channel_3',
        '2020-01-01 10:00:00',
        'team_1_lead',
        'channel_3_name',
        FALSE,
        'channel_3_description',
        'channel_3_avatar_id',
        True
       ),
       (
        'existing_channel',
        '2020-01-01 10:00:00',
        'team_1_lead',
        'existing_channel_name',
        FALSE,
        'existing_channel_description',
        'avatar_id',
        True
       ),
       (
        'existing_channel_without_subscribers',
        '2020-01-01 10:00:00',
        'team_1_lead',
        'existing_channel_without_subscribers_name',
        FALSE,
        'existing_channel_without_subscribers_description',
        'avatar_id',
        True
       ),
       (
        'feed_test_channel_1',
        '2020-01-01 10:00:00',
        'feed_test_user',
        'feed_test_channel_1_name',
        FALSE,
        'feed_test_channel_1_description',
        'avatar_id',
        True
       ),
       (
        'feed_test_channel_2',
        '2020-01-01 10:00:00',
        'feed_test_user',
        'feed_test_channel_2_name',
        FALSE,
        'feed_test_channel_2_description',
        'avatar_id',
        True
       ),
       (
        'feed_test_channel_3',
        '2020-01-01 10:00:00',
        'feed_test_user',
        'feed_test_channel_3_name',
        FALSE,
        'feed_test_channel_3_description',
        'avatar_id',
        True
       ),
       (
        'deleted_channel',
        '2020-01-01 10:00:00',
        'team_1_lead',
        'deleted_channel_name',
        TRUE,
        'deleted_channel_description',
        'avatar_id',
        True
       ),
       (
        'private_channel',
        '2020-01-01 10:00:00',
        'team_1_lead',
        'private_channel_name',
        FALSE,
        'private_channel_description',
        'avatar_id',
        False
       );

INSERT INTO agent.channel_admins(
    login,
    channel_key
)
VALUES (
        'team_1_lead',
        'existing_channel'
       ),
       (
        'team_1_lead',
        'existing_channel_without_subscribers'
       ),
       (
        'feed_test_user',
        'feed_test_channel_1'
       ),
       (
        'feed_test_user',
        'feed_test_channel_2'
       ),
       (
        'feed_test_user',
        'feed_test_channel_3'
       );

INSERT INTO agent.team_subscriptions(
    team_key,
    channel_key
)
VALUES (
        'team_1',
        'existing_channel'
       ),
       (
        'team_4',
        'channel_3'
       ),
       (
        'team_5',
        'feed_test_channel_1'
       );

INSERT INTO agent.project_subscriptions(
    project,
    channel_key
)
VALUES (
        'project_1',
        'existing_channel'
       ),
       (
        'project_2',
        'feed_test_channel_2'
       );

INSERT INTO agent.channels_teams_access(
    team_key,
    channel_key
)
VALUES (
        'team_1',
        'existing_channel'
       );

INSERT INTO agent.channels_projects_access(
    project,
    channel_key
)
VALUES (
        'project_1',
        'existing_channel'
       );

INSERT INTO agent.subscriptions(
    login,
    channel_key
)
VALUES (
        'subscribed_user',
        'channel_1'
       ),
       (
        'user_subscribed_via_team_and_manually',
        'channel_3'
       ),
       (
        'feed_test_user',
        'feed_test_channel_3'
       ),
       (
        'no_access_user',
        'private_channel'
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
(1,'existing_post', NOW(),'text', False, 'team_1_lead', NULL, 'text'),
(2,'existing_post_1', NOW(),'text', False, 'team_1_lead', NULL, 'text'),
(3,'existing_post_2', NOW(),'text', False, 'team_2_lead', '{image_1}', 'text'),
(10,'feed_test_post_1', '2022-01-10 00:00:00','feed_test_post_1_text', True, 'feed_test_user', '{}', ''),
(9,'feed_test_post_2', '2022-01-09 00:00:00','feed_test_post_2_text', False, 'feed_test_user', '{}', ''),
(8,'feed_test_post_3', '2022-01-08 00:00:00','feed_test_post_3_text', False, 'feed_test_user', '{}', ''),
(7,'feed_test_post_4', '2022-01-07 00:00:00','feed_test_post_4_text', False, 'feed_test_user', '{}', ''),
(6,'feed_test_post_5', '2022-01-06 00:00:00','feed_test_post_5_text', True, 'feed_test_user', '{}', ''),
(5,'feed_test_post_6', '2022-01-05 00:00:00','feed_test_post_6_text', False, 'feed_test_user', '{}', ''),
(4,'feed_test_post_7', '2022-01-04 00:00:00','feed_test_post_7_text', False, 'feed_test_user', '{}', ''),
(11,'deleted_post', NOW(),'text', TRUE, 'team_1_lead', NULL, 'text'),
(12,'private_channel_post', NOW(),'text', False, 'team_1_lead', NULL, 'text');

INSERT INTO agent.channel_posts
(
    channel_id,
    post_id
) VALUES
('existing_channel','existing_post'),
('channel_1','existing_post'),
('existing_channel','existing_post_1'),
('channel_1','existing_post_1'),
('channel_1','existing_post_2'),
('feed_test_channel_1','feed_test_post_1'),
('feed_test_channel_1','feed_test_post_2'),
('feed_test_channel_2','feed_test_post_2'),
('feed_test_channel_3','feed_test_post_2'),
('feed_test_channel_3','feed_test_post_3'),
('feed_test_channel_1','feed_test_post_4'),
('feed_test_channel_2','feed_test_post_5'),
('feed_test_channel_3','feed_test_post_6'),
('private_channel','private_channel_post');

INSERT INTO agent.post_likes
(
    post_id,
    login,
    dt
) VALUES
('existing_post_1','team_1_lead', NOW());

INSERT INTO agent.post_views
(
    post_id,
    login,
    dt
) VALUES
('existing_post_1','team_1_lead', NOW());

