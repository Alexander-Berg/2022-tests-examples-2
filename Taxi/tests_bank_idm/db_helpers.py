SELF_SYSTEM_ID = 1


def add_user(pgsql, user_login, user_email):
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        INSERT INTO bank_idm.users (login, email)
        VALUES ('{user_login}', '{user_email}')
        RETURNING user_id
    """,
    )
    return cursor.fetchone()[0]


# pylint: disable=W0102
def add_role(pgsql, user_id, rolenode_id, role_status='granted', version=0):
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        INSERT INTO bank_idm.roles (
        user_id,
        rolenode_id,
        role_status,
        requested_from,
        version)
        VALUES ({user_id},
                {rolenode_id},
                '{role_status}',
                {user_id},
                {version})
        RETURNING role_id
    """,
    )
    return cursor.fetchone()[0]


def add_system(
        pgsql,
        system_slug,
        user_id,
        system_status='enabled',
        system_name='TEST SYSTEM',
):
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        INSERT INTO bank_idm.systems (
        system_slug,
        system_name,
        system_description,
        system_path,
        system_status,
        creator)
        VALUES ('{system_slug}',
                '{system_name}',
                'TEST SYSTEM DESCRIPTION',
                '',
                '{system_status}',
                {user_id})
        RETURNING system_id
    """,
    )
    system_id = cursor.fetchone()[0]
    rolenode_id = add_role_nodes(
        pgsql,
        f'systems/{system_slug}/responsible',
        'Responsible',
        SELF_SYSTEM_ID,
    )
    add_role(pgsql, user_id, rolenode_id)
    return system_id


def add_role_nodes(
        pgsql,
        slug_path,
        role_name,
        system_id,
        rolenode_status='enabled',
        is_leaf=True,
        parent_rolenode_id=None,
):
    cursor = pgsql['bank_idm'].cursor()
    sql = """
        INSERT INTO bank_idm.role_nodes (
         slug_path,
        role_name,
        is_leaf,
        system_id,
        rolenode_status,
        parent_rolenode_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING rolenode_id
    """
    cursor.execute(
        sql,
        [
            slug_path,
            role_name,
            is_leaf,
            system_id,
            rolenode_status,
            parent_rolenode_id,
        ],
    )
    return cursor.fetchone()[0]


def add_action(
        pgsql,
        system_id: int,
        action: str,
        description=None,
        user_id=None,
        requester_id=None,
        parent_action_id=None,
        role_id=None,
        approve_id=None,
        rolenode_id=None,
):
    cursor = pgsql['bank_idm'].cursor()
    sql = """
        INSERT INTO bank_idm.actions (
          system_id,
          action,
          description,
          user_id,
          requester_id,
          parent_action_id,
          role_id,
          approve_id,
          rolenode_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING
          action_id;
    """
    cursor.execute(
        sql,
        [
            system_id,
            action,
            description,
            user_id,
            requester_id,
            parent_action_id,
            role_id,
            approve_id,
            rolenode_id,
        ],
    )
    return cursor.fetchone()[0]


def add_approve(
        pgsql,
        role_id: int,
        approver_user_id: int,
        approve_status='approved',
        role_version=0,
):
    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        f"""
        INSERT INTO bank_idm.approves (
          role_id,
          approver_user_id,
          approve_status,
          role_version
        )
        VALUES ({role_id},
                {approver_user_id},
                '{approve_status}',
                {role_version})
        RETURNING approve_id
    """,
    )
    return cursor.fetchone()[0]


def prepare_test_data(
        pgsql,
        user_login,
        responsible_user='responsible',
        system_status='enabled',
        rolenode_status='enabled',
        approvers=None,
):
    slug_path = 'test/slug_path'
    system_slug = 'test_slug'
    user_id = add_user(pgsql, user_login, 'test@gmail.com')
    responsible_user_id = add_user(pgsql, responsible_user, 'test@gmail.com')
    system_id = add_system(
        pgsql, system_slug, responsible_user_id, system_status,
    )
    rolenode_id = add_role_nodes(
        pgsql, slug_path, 'Slug Path', system_id, rolenode_status,
    )
    if approvers is not None:
        set_approvers(pgsql, approvers, system_id, slug_path)

    return user_id, rolenode_id


def get_approvers(pgsql, rolenode_id, approvers_version=0):
    cursor = pgsql['bank_idm'].cursor()
    sql = """
        SELECT approve_list_id from bank_idm.total_approvers
        WHERE rolenode_id = %s and approvers_version = %s
    """
    cursor.execute(sql, (rolenode_id, approvers_version))
    multi_approvers = cursor.fetchall()

    approvers = []
    get_single_approvers_sql = """
        SELECT user_login from bank_idm.approve_list_users
        WHERE approve_list_id = %s
    """
    for approve_list_id in multi_approvers:
        cursor.execute(get_single_approvers_sql, (approve_list_id[0],))
        approvers.append([row[0] for row in cursor.fetchall()])

    approvers = {'logins': approvers}
    return approvers


def set_approvers(pgsql, all_approvers, system_id, slug_path):
    cursor = pgsql['bank_idm'].cursor()
    update_approvers_version_sql = """
        UPDATE bank_idm.role_nodes
        SET approvers_version = approvers_version + 1
        WHERE system_id = %s AND slug_path = %s
        RETURNING role_name,
                  rolenode_id,
                  parent_rolenode_id,
                  approvers_version,
                  is_leaf;
    """
    cursor.execute(update_approvers_version_sql, (system_id, slug_path))
    rolenode_info = cursor.fetchone()
    set_approve_list_users_sql = """
        WITH inserted_approve_list AS (
            INSERT INTO bank_idm.approve_list DEFAULT VALUES
            RETURNING approve_list_id
        ), approvers AS (
            INSERT INTO bank_idm.total_approvers (
              approve_list_id,
              rolenode_id,
              approvers_version
            ) VALUES (
                (select approve_list_id from inserted_approve_list), %s, %s
            )
        )
        INSERT INTO bank_idm.approve_list_users (
          user_login,
          approve_list_id
        ) VALUES (
          UNNEST(%s), (select approve_list_id from inserted_approve_list)
        );
    """
    for approvers in all_approvers:
        cursor.execute(
            set_approve_list_users_sql,
            (rolenode_info[1], rolenode_info[3], approvers),
        )
