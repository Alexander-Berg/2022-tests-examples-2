INSERT INTO agent.departments
(key,created,name)
VALUES
('yandex',NOW(),'Яндекс'),
('taxi_dep72956_dep20857',NOW(),'Группа внутренних сервисов
'),
('taxi_dep11496_dep38268_dep08025',NOW(),'Служба платформы микросервисов
');


INSERT INTO agent.users (
    uid, created, login, first_name, last_name, join_at
)
VALUES
    (1120000000252888, NOW(), 'login1', 'Тест', 'Тестовый', '2016-06-02'),
    (1120000000252888, NOW(), 'login2', 'Тест', 'Тестовый', '2016-06-02'),
    (1120000000252888, NOW(), 'mikh-vasily', 'Тест', 'Тестовый', '2016-06-02'),
    (1120000000252889, NOW(), 'webalex', 'Тест1', 'Тестовый1', '2016-06-02');


INSERT INTO agent.departments_heads (login,key,role)
VALUES
       ('login1','taxi_dep72956_dep20857','head'),
       ('login2','taxi_dep11496_dep38268_dep08025','head'),
       ('mikh-vasily','yandex','head');
