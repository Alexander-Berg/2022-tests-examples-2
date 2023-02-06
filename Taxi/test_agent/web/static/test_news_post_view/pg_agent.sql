INSERT INTO agent.users (login, uid, created, first_name, last_name, join_at) VALUES
('justmark0', 100500, NOW(), 'Mark', 'Nicholson', NOW()),
('romford', 100500, NOW(), 'Alexander', 'Fedotov', NOW()),
('webalex', 100500, NOW(), 'Alexander', 'Ivanov', NOW());

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
('post3', NOW(),'text', False, 'webalex', NULL, 'text');


INSERT INTO agent.post_views (post_id, login, dt) VALUES
('post1', 'justmark0', NOW());
