INSERT INTO callcenter_auth.operators_access
    (
        yandex_uid,
        yandex_login,
        callcenter_id,
        first_name,
        last_name,
        deleted_at,
        updated_at,
        state,
        password,
        supervisor_login,
        phone_number,
        working_domain,
        operator_id,
        staff_login,
        timezone,
        mentor_login,
        employment_date,
        name_in_telephony
    )
VALUES
    (
        'admin_uid',
        'admin',
        'cc1',
        'admin',
        'adminov',
        NULL,
        '2016-06-22 22:10:25+3',
        'ready',
        'rgNIgYs0QpgbUs7DFCBMdI/oY5c+0EKB8Nvxm6uMw4Y=',
        NULL,
        '+112',
        'unit.test',
        1777777777,
        'ultra_staff',
        'Europe/Moscow',
        NULL,
        '2016-06-22'::DATE,
        'tel_name'
    ),
    (
        'supervisor_uid',
        'supervisor',
        'cc1',
        'supervisor',
        'supervisorov',
        NULL,
        '2016-06-22 22:10:25+3',
        'ready',
        'UWMhGgzCq9/bndLQ91mPyLO0Elh10a5rfd2ezeDzksM=',
        'admin@unit.test',
        '+221',
        'unit.test',
        1888888888,
        NULL,
        NULL,
        NULL,
        '2016-06-22'::DATE,
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
    ),
    (
        'disconnected',
        '{}',
        2
    );

INSERT INTO callcenter_auth.m2m_operators_roles
    (yandex_uid, role)
VALUES
    ('admin_uid', 'ru_disp_call_center_head'),
    ('supervisor_uid', 'ru_disp_team_leader');
