INSERT INTO agent.departments VALUES
('yandex',NOW(),NOW(),'Yandex',null),
('yandex_taxi',NOW(),NOW(),'Yandex Taxi',null),
('yandex_eda',NOW(),NOW(),'Yandex Eda',null);

INSERT INTO agent.users (login, uid, created, first_name, last_name,department,join_at) VALUES
('liambaev', '100500', NOW(), 'Лиам', 'Баев', 'yandex_taxi','2000-01-01'::date),
('webalex', '100500', NOW(), ' Александр', 'Иванов', 'yandex_taxi','2000-01-01'::date),
('orangevl', '100500', NOW(), 'Семен', 'Решетняк', 'yandex_taxi','2000-01-01'::date),
('device25', '100500', NOW(), 'Андрей', 'Бахвалов','yandex_eda','2000-01-01'::date),
('new_user', '100500', NOW(), 'new_user', 'new_user','yandex_taxi',NOW()::date - 10);


INSERT INTO agent.courses_results VALUES (1,'webalex',NOW(),NOW(),'moe',100)
