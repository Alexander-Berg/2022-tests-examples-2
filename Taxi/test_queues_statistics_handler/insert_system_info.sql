INSERT INTO callcenter_queues.callcenter_system_info
       (
       metaqueue,
       subcluster,
       enabled_for_call_balancing,
       enabled_for_sip_user_autobalancing,
       enabled
       )
VALUES
    ('ru_taxi_disp', '1', true, true, true),
    ('ru_taxi_disp', '2', true, true, true),
    ('ru_taxi_disp', '3', true, true, true),
    ('ru_taxi_support', '1', true, true, true),
    ('ru_taxi_support', '2', true, true, true),
    ('ru_taxi_econom', '1', true, true, true)
;
