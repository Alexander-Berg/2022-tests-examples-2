INSERT INTO supportai.roles (
    id,
    title,
    permissions
) VALUES
(1, 'Super Admin', '{}');

INSERT INTO supportai.users (id, provider_id, login, is_active) VALUES
(4, '007', 'ya_user_4', TRUE);

INSERT INTO supportai.user_to_role (user_id, role_id, project_slug) VALUES
(4, 1, NULL);

INSERT INTO supportai.projects (id, slug, title, new_config_schema) VALUES
(1, 'demo_dialog', 'Маркет', False);

