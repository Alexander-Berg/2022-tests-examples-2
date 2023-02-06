INSERT INTO callcenter_auth.operators_access
    (
        yandex_uid,
        yandex_login,
        callcenter_id,
        first_name,
        deleted_at,
        updated_at,
        state,
        password,
        supervisor_login,
        phone_number,
        working_domain,
        operator_id,
        employment_date,
        name_in_telephony
    )
VALUES
    (
        'uid1',
        'login1',
        'cc1',
        'name1',
        NULL,
        '2018-06-22 22:10:25+3',
        'ready',
        NULL ,
        NULL,
        NULL,
        'unit.test',
        NULL,
        '2018-06-22'::DATE,
        'tel_name'
    );
