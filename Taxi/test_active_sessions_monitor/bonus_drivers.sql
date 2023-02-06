INSERT INTO state.sessions
    (session_id, active, point_id, start,                        "end",                        driver_id_id,          mode_id, submode_id,  destination_point,    session_deadline,              bonus_until               , completed)
    VALUES
    (2010,       True,   101,      '2018-10-11T16:01:11.540859', '2018-10-11T16:02:11.540859', IdId('uuid', 'dbid'),  1,       NULL,        (3, 4)::db.geopoint,  NULL,                          '2021-11-03T14:15:16+0000', TRUE     ),
    (2012,       False,  102,      '2018-10-12T16:05:11.540859', '2018-10-12T16:04:11.540859', IdId('uuid1', 'dbid'), 3,       NULL,        (3, 4)::db.geopoint,  '2018-10-12T17:05:11.540859',  NULL                      , TRUE     );
