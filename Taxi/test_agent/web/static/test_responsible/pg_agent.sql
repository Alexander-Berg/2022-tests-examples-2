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
),
(
    1120000000252888,
     NOW(),
    'liambaev',
    'Лиам',
    'Баев',
    '2016-06-02'
);

INSERT INTO agent.channel_category (key,name) VALUES ('dev','dev');

INSERT INTO agent.channels (key, category, created, creator, name, deleted, description, permissions) VALUES
('chatterbox','dev','2021-01-01 00:00:00','webalex','Chatterbox',false,'test','{"can_one","can_two"}'),
('agent','dev','2021-01-01 00:00:00','webalex','Agent',true,'test','{"can_one","can_two"}');


INSERT INTO agent.channels_responsible (channel_key,login) VALUES ('chatterbox','liambaev');

