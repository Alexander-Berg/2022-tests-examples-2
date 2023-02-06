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
        'uid1',
        'login1',
        'cc2',
        'name1',
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
        1000000000,
        'login1_staff',
        'verified',
        NULL,
        'telegram_login_1',
        NULL,
        '2016-06-01'::DATE,
        NULL,
        'login1_unit.test'
    ),
    (
        'uid2',
        'login2',
        'cc2',
        'name2',
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
        1000000001,
        'login2_staff',
        'verified',
        NULL,
        'telegram_login_2',
        NULL,
        '2016-06-01'::DATE,
        NULL,
        'login2_unit.test'
    );

INSERT INTO callcenter_auth.current_info
(
    sub_status,
    status,
    metaqueues,
    id
)
VALUES
    (
        NULL,
        'connected',
        '{test}',
        1
    ),
    (
        NULL,
        'connected',
        '{test_another}',
        2
    );


INSERT INTO callcenter_auth.m2m_operators_roles
(yandex_uid, role)
VALUES
    ('uid1', 'operator'),
    ('uid2', 'operator');

ALTER SEQUENCE callcenter_auth.operator_id_seq RESTART WITH 1000000003;
