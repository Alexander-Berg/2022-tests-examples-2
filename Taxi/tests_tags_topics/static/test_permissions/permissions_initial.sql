INSERT INTO permissions.roles (id, service, slug)
VALUES (1, 'tags', 'topic1'),
       (2, 'tags', 'topic2'),
       (3, 'passenger-tags', 'topic3'),
       (4, 'eats-tags', 'topic4'),
       (5, 'grocery-tags', 'topic5');

INSERT INTO permissions.user_roles (login, role_id)
VALUES ('user1', 1),
       ('user1', 2),
       ('user2', 1),
       ('user1', 3),
       ('user1', 4),
       ('user1', 5);
