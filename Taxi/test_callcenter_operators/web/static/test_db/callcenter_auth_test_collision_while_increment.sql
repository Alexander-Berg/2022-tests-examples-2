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
        operator_id,
        password,
        supervisor_login,
        phone_number,
        working_domain,
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
        1777777777,
        'rgNIgYs0QpgbUs7DFCBMdI/oY5c+0EKB8Nvxm6uMw4Y=',
        NULL,
        '+112',
        'unit.test',
        'ultra_staff',
        'Europe/Moscow',
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
        1000000000,
        'rgNIgYs0QpgbUs7DFCBMdI/oY5c+0EKB8Nvxm6uMw4Y=',
        'admin@unit.test',
        '+111',
        'unit.test',
        'login1_staff',
        'Europe/Moscow',
        NULL,
        '2018-06-22'::DATE,
        'tel_name'
    );
