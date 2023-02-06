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
        'admin_unit.test'
    ),
    (
        'UID',
        'LOGIN',
        'cc2',
        'name',
        'surname',
        NULL,
        '2019-06-22 22:10:25+3',
        'ready',
        'UWMhGgzCq9/bndLQ91mPyLO0Elh10a5rfd2ezeDzksM=',
        'admin@unit.test',
        '+333',
        'unit.test',
        1000000000,
        NULL,
        NULL,
        NULL,
        '2019-06-22'::DATE,
        'login_unit.test'
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
        'connected',
        '{test}',
        2
    );

ALTER SEQUENCE callcenter_auth.operator_id_seq RESTART WITH 1000000001;
