INSERT INTO agent.users (
    uid,
    guid,
    created,
    login,
    first_name,
    last_name,
    join_at,
    piece,
    country
)
VALUES (
    1120000000252888,
    'abeb11542dbaee44bf7753d5ddf41100',
     NOW(),
    'webalex',
    'Александр',
    'Иванов',
    '2016-06-02',
    false,
    null
);


INSERT INTO agent.roles (key, created, updated, creator, ru_name, en_name, ru_description, en_description, visible) VALUES
('lavkastorekeeper',NOW(),NOW(),'webalex','lavkastorekeeper','lavkastorekeeper','lavkastorekeeper','lavkastorekeeper',TRUE),
('lavkastorekeeper_director',NOW(),NOW(),'webalex','lavkastorekeeper_director','lavkastorekeeper_director','lavkastorekeeper_director','lavkastorekeeper_director',TRUE);
