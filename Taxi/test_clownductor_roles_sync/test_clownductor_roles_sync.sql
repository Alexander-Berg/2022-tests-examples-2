INSERT INTO secrets.scope_rights (
    project_name, service_name, env, login, role_type
)
VALUES
    ('taxi-infra', 'service-2', 'production', 'some-mate', 'edit_secrets'),
    ('taxi', null, 'testing', 'some-mate', 'edit_secrets'),
    (null, null, 'unstable', 'some-mate', 'edit_secrets'),

    (null, null, 'testing', 'some-mate-2', 'edit_secrets'),
    ('taxi', null, 'unstable', 'some-mate-2', 'edit_secrets'),

    ('taxi', 'service', 'testing', 'some-mate-3', 'edit_secrets'),
    ('taxi', 'service', 'unstable', 'some-mate-3', 'edit_secrets'),

    ('taxi-infra', 'service-2', 'production', 'some-mate', 'create_secrets'),
    ('taxi', null, 'testing', 'some-mate', 'create_secrets'),
    (null, null, 'unstable', 'some-mate', 'create_secrets'),

    (null, null, 'testing', 'some-mate-2', 'create_secrets'),
    ('taxi', null, 'unstable', 'some-mate-2', 'create_secrets'),

    ('taxi', 'service', 'testing', 'some-mate-3', 'create_secrets'),
    ('taxi', 'service', 'unstable', 'some-mate-3', 'create_secrets')
;
