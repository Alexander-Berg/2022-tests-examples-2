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
    ),
    (
        'uid1',
        'login1',
        'cc1',
        'name1',
        'surname',
        NULL,
        '2018-06-22 22:10:25+3',
        'ready',
        'rgNIgYs0QpgbUs7DFCBMdI/oY5c+0EKB8Nvxm6uMw4Y=',
        'admin@unit.test',
        '+111',
        'unit.test',
        1000000000,
        'login1_staff',
        'Europe/Moscow',
        NULL,
        '2018-06-22'::DATE,
        'tel_name'
    ),
    (
        'uid2',
        'login2',
        'cc2',
        'name2',
        'surname',
        NULL,
        '2018-06-22 22:10:25+3',
        'ready',
        'rgNIgYs0QpgbUs7DFCBMdI/oY5c+0EKB8Nvxm6uMw4Y=',
        'supervisor@unit.test',
        '+111',
        'unit.test',
        1000000001,
        NULL,
        NULL,
        NULL,
        '2018-06-22'::DATE,
        'tel_name'
    ),
    (
        'uid3',
        'login3',
        'cc2',
        'deleted',
        'deleted',
        '2019-06-22 22:10:25+3',
        '2019-06-22 22:10:25+3',
        'deleting',
        'UWMhGgzCq9/bndLQ91mPyLO0Elh10a5rfd2ezeDzksM=',
        'supervisor@unit.test',
        '+000',
        'unit.test',
        1000000002,
        NULL,
        NULL,
        NULL,
        '2019-06-22'::DATE,
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
    ),
    (
        'disconnected',
        '{corp, help}',
        3
    ),
    (
        'connected',
        '{help}',
        4
    ),
    (
        'disconnected',
        '{}',
        5
    );

INSERT INTO callcenter_auth.m2m_operators_roles
    (yandex_uid, role)
VALUES
    ('admin_uid', 'admin'),
    ('supervisor_uid', 'supervisor'),
    ('uid1', 'operator'),
    ('uid2', 'supervisor'),
    ('uid3', 'operator');

ALTER SEQUENCE callcenter_auth.operator_id_seq RESTART WITH 1000000003;
