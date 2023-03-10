INSERT INTO callcenter_auth.operators_access
    (
        yandex_uid,
        yandex_login,
        callcenter_id,
        first_name,
        middle_name,
        last_name,
        created_at,
        deleted_at,
        updated_at,
        state,
        password,
        supervisor_login,
        phone_number,
        working_domain,
        operator_id,
        staff_login,
        staff_login_state,
        timezone,
        telegram_login,
        mentor_login,
        employment_date,
        mentor_updated_at,
        name_in_telephony
    )
VALUES
    (
        'admin_uid',
        'admin',
        'cc1',
        'admin',
        'adminovich',
        'adminov',
        '2016-06-01T19:10:25Z',
        NULL,
        '2016-06-22T19:10:25Z',
        'ready',
        'rgNIgYs0QpgbUs7DFCBMdI/oY5c+0EKB8Nvxm6uMw4Y=',
        NULL,
        '+112',
        'yandex-team.ru',
        1777777777,
        'ultra_staff',
        'verified',
        'Europe/Moscow',
        'telegram_login_admin',
        'admin@yandex-team.ru',
        '2016-06-01'::DATE,
        '2016-06-01T19:10:25Z',
        'admin_unit.test'
    ),
    (
        'supervisor_uid',
        'supervisor',
        'cc1',
        'supervisor',
        NULL,
        'supervisorov',
        '2016-06-01T19:10:25Z',
        NULL,
        '2016-06-22T19:10:25Z',
        'ready',
        'UWMhGgzCq9/bndLQ91mPyLO0Elh10a5rfd2ezeDzksM=',
        'admin@yandex-team.ru',
        '+221',
        'yandex-team.ru',
        1888888888,
        NULL,
        'verified',
        NULL,
        'telegram_login_supervisor',
        'admin@unit.test',
        '2016-06-01'::DATE,
        '2016-06-01T19:10:25Z',
        'supervisor_unit.test'
    ),
    (
        'uid1',
        'login1',
        'cc1',
        'name1',
        'middlename',
        'surname',
        '2016-06-01T19:10:25Z',
        NULL,
        '2016-06-22T19:10:26Z',
        'ready',
        'rgNIgYs0QpgbUs7DFCBMdI/oY5c+0EKB8Nvxm6uMw4Y=',
        'admin@unit.test',
        '+111',
        'unit.test',
        1000000000,
        'login1_staff',
        'verified',
        'Europe/Moscow',
        'telegram_login_1',
        'supervisor@unit.test',
        '2016-06-01T19:10:25Z',
        '2016-06-01T19:10:25Z',
        'login1_unit.test'
    ),
    (
        'uid2',
        'login2',
        'cc1',
        'name2',
        'middlename',
        'surname',
        '2016-06-01T19:10:25Z',
        '2016-06-22T19:10:27Z',
        '2016-06-22T19:10:27Z',
        'deleted',
        'jfWvc94NtwpSRc2O6pSsxjIPk3awvU6+KkT53zHHAyg=',
        'admin@yandex-team.ru',
        '+222',
        'yandex-team.ru',
        1000000001,
        NULL,
        'verified',
        NULL,
        'telegram_login_2',
        'supervisor@unit.test',
        '2016-06-01'::DATE,
        '2016-06-01T19:10:25Z',
        'login2_unit.test'
    ),
    (
        'uid3',
        'login3',
        'cc2',
        'name3',
        NULL,
        'surname',
        '2016-06-01T19:10:25Z',
        NULL,
        '2016-06-22T19:10:28Z',
        'ready',
        'UWMhGgzCq9/bndLQ91mPyLO0Elh10a5rfd2ezeDzksM=',
        'admin@unit.test',
        '+333',
        'unit.test',
        1000000002,
        'login3_staff',
        'verified',
        NULL,
        'telegram_login_3',
        NULL,
        '2016-06-01'::DATE,
        NULL,
        'login3_unit.test'
    );

INSERT INTO callcenter_auth.current_info
    (
        status,
        metaqueues,
        id
    )
VALUES
    (
        'disconnected',
        '{}',
        1
    ),
    (
        'disconnected',
        '{}',
        2
    ),
    (
        'disconnected',
        '{corp, help}',
        3
    ),
    (
        'disconnected',
        '{disp}',
        4
    ),
    (
        'connected',
        '{disp}',
        5
    );

INSERT INTO callcenter_auth.m2m_operators_roles
    (yandex_uid, role, source)
VALUES
    ('admin_uid', 'admin', 'idm'),
    ('supervisor_uid', 'supervisor', 'idm'),
    ('supervisor_uid', 'some_random_role', 'admin'),
    ('uid1', 'operator', 'idm'),
    ('uid2', 'operator', 'idm'),
    ('uid2', 'some_random_role', 'admin'),
    ('uid3', 'operator', 'idm');

ALTER SEQUENCE callcenter_auth.operator_id_seq RESTART WITH 1000000003;
