INSERT INTO
    deptrans.session_statuses(
        driver_license_pd_id,
        session_status,
        session_deny_reason,
        ended_at,
        is_driver_online
    )
VALUES
    (
        'driver_license_pd_id_2',
        'NO_WAYBILL',
        NULL,
        NOW(),
        True
    );
