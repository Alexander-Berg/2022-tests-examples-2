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
        'chief_uid',
        'chief',
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
        NULL,
        '2016-06-01'::DATE,
        '2016-06-01T19:10:25Z',
        'tel_name'
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
    );

INSERT INTO callcenter_auth.m2m_operators_roles
    (yandex_uid, role)
VALUES
    ('chief_uid', 'admin');

ALTER SEQUENCE callcenter_auth.operator_id_seq RESTART WITH 1000000001;
