INSERT INTO callcenter_queues.tel_state
(sip_username, metaqueues, subcluster, is_connected, is_paused, is_valid)
VALUES ('dm1', '{ru_taxi_disp, ru_taxi_support}', '1', True, True, True),
       ('dm2', '{ru_taxi_disp}', '1', True, False, True),
       ('dm3', '{ru_taxi_support}', '1', True, False, True),
       ('dm5', '{ru_taxi_econom}', '1', True, True, True),
       ('dm6', '{ru_taxi_disp, ru_taxi_support}', '2', True, False, True),
       ('dm7', '{ru_taxi_disp}', '3', True, False, True),
       ('dm8', '{ru_taxi_support}', '2', True, True, True),
       ('dm9', '{ru_taxi_econom}', '1', True, False, True);
