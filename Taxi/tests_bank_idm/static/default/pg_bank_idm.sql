BEGIN;

DO $$
DECLARE
    base_user_id bank_idm.users.user_id%TYPE;
    base_system_id bank_idm.systems.system_id%TYPE;
BEGIN
    INSERT INTO bank_idm.users
    (
        login,
        email
    ) VALUES
        ('kalievoral', 'kalievoral@yandex-team.ru')
    RETURNING
      user_id INTO base_user_id;

    INSERT INTO bank_idm.systems (
        system_slug,
        system_name,
        system_description,
        system_path,
        creator
    ) VALUES
        ('idm', 'IDM', 'Bank IDM system', '', base_user_id)
    RETURNING
      system_id INTO base_system_id;

    INSERT INTO bank_idm.role_nodes
    (
        slug_path,
        role_name,
        is_leaf,
        system_id,
        parent_rolenode_id
    ) VALUES
        ('systems', 'Systems', false, base_system_id, NULL),
        ('systems/idm', 'IDM', false, base_system_id, 1),
        ('systems/idm/responsible', 'Responsible', true, base_system_id, 2);

    INSERT INTO bank_idm.roles
    (
        user_id,
        rolenode_id,
        role_status,
        requested_from
    ) VALUES
        (1, 3, 'granted'::bank_idm.role_status, base_user_id);
END
$$;

COMMIT;
