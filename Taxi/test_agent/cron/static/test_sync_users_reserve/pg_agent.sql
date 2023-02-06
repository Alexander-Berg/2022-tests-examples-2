INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at,piece,quit_at
)
VALUES
    (1120000000252888, NOW(), 'mikh-vasily', 'Василий', 'Михайлов', '2022-05-01',True,null),
    (1120000000252889, NOW(), 'webalex', 'Александр', 'Иванов', '2022-04-30',True,null),
    (1120000000252889, NOW(), 'akozhevina', 'Анна', 'Кожевина', '2021-06-01',True,null),
    (1120000000252888, NOW(), 'slon', 'Василий', 'Слонов', '2022-06-01',True,null),
    (1120000000252889, NOW(), 'korol', 'Александр', 'Король', '2021-06-01',False,null),
    (1120000000252889, NOW(), 'meetka', 'Дмитрий', 'Борисов', '2021-05-30',True,'2021-05-31');


INSERT INTO agent.permissions VALUES
(
 'user_calltaxi',
 '2021-01-01 00:00:00',
 '2021-01-01 00:00:00',
 'webalex',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi',
 'user_calltaxi'
);

INSERT INTO agent.teams VALUES
('team_1','team_1','user_calltaxi');

UPDATE agent.users SET team='team_1' WHERE login IN ('mikh-vasily','webalex','akozhevina','slon','korol');
