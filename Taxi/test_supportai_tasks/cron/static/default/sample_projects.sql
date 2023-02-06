INSERT INTO supportai.roles (
    id,
    title,
    permissions
) VALUES
(1, 'Super Admin', '{}'),
(2, 'Project Admin', '{"read","write","modify"}'),
(3, 'Project Editor', '{"read","write"}'),
(4, 'Project Reader', '{"read"}');

INSERT INTO supportai.users (id, provider_id, is_active) VALUES
(1, 34, TRUE),
(2, 35, TRUE),
(3, 000000, FALSE);

INSERT INTO supportai.projects (id, slug, title) VALUES
(1, 'ya_market', 'Маркет'),
(2, 'ya_lavka', 'Лавка'),
(3, 'ya_useless', 'Бесполезный проект');

INSERT INTO supportai.user_to_role (user_id, role_id, project_slug) VALUES
(1, 3, 'ya_market'),
(1, 3, 'ya_lavka'),
(2, 3, 'ya_market'),
(2, 2, 'ya_lavka'),
(2, 3, 'ya_useless'),
(3, 3, 'ya_useless');

