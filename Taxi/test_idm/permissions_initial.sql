INSERT INTO permissions.roles (id, service, slug)
VALUES (1, 'tags', 'topic1'),
       (2, 'tags', 'topic2');

INSERT INTO permissions.user_roles (login, role_id)
VALUES ('user1', 1),
       ('user1', 2),
       ('user2', 1);
