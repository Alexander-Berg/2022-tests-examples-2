INSERT INTO cursors
    (id, name, last_id, last_updated_at)
VALUES
    (1, 'requests', 2, '2021-08-17 14:00:00');


INSERT INTO requests
    (id, path, ip, request, data_server, data, created_at, updated_at, user_guid)
VALUES
    ( -- No log: updated_at behind cursor
        1,
        'https://api.rida.app/v1/logDriverPosition',
        '10.41.1.31',
        '{"lat":6.5154854999999996,"long":3.2890172,"heading":90,"user_guid":"5c339935-722b-4986-bdb7-1400a7efa284"}
         method: POST
         Language: en
         headers: {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvYXBpLnJpZGEuYXBwIiwiYXVkIjoiaHR0cHM6XC9cL2FwaS5yaWRhLmFwcCIsImlhdCI6MTYyMjEwOTg5NywibmJmIjoxNjIyMTA5ODk3LCJleHAiOjE2NTM2NDU4OTcsImlkIjo5MTA4MiwiZGV2aWNlX3V1aWQiOiI2ZDA1YWNmYS0zZjU0LTQyMTYtYmY1Ny0zMjJhNTVjMjU5NjEifQ.l7Wr8Ae3AdMXUq-wNG2IrWHsjJprdVZ8TF7Dgy7QP4Y","Accept-Encoding":"gzip","Content-Type":"application\/json","Content-Length":"171","Connection":"close","X-Publisher-Type":"http","Accept-Language":"en","Host":"api.rida.app"}
         userGUID: 5c339935-722b-4986-bdb7-1400a7efa284',
        'Response status: 304
         []
         duration: 0.201',
        '',
        '2021-08-17 13:23:14',
        '2021-08-17 13:23:14',
        '5c339935-722b-4986-bdb7-1400a7efa284'
    ),
    ( -- No log: updated_at at cursor & id behind cursor
        2,
        'https://api.rida.app/v1/logDriverPosition',
        '10.41.1.31',
        '{"lat":6.5154854999999996,"long":3.2890172,"heading":90,"user_guid":"5c339935-722b-4986-bdb7-1400a7efa284"}
         method: POST
         Language: en
         headers: {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvYXBpLnJpZGEuYXBwIiwiYXVkIjoiaHR0cHM6XC9cL2FwaS5yaWRhLmFwcCIsImlhdCI6MTYyMjEwOTg5NywibmJmIjoxNjIyMTA5ODk3LCJleHAiOjE2NTM2NDU4OTcsImlkIjo5MTA4MiwiZGV2aWNlX3V1aWQiOiI2ZDA1YWNmYS0zZjU0LTQyMTYtYmY1Ny0zMjJhNTVjMjU5NjEifQ.l7Wr8Ae3AdMXUq-wNG2IrWHsjJprdVZ8TF7Dgy7QP4Y","Accept-Encoding":"gzip","Content-Type":"application\/json","Content-Length":"171","Connection":"close","X-Publisher-Type":"http","Accept-Language":"en","Host":"api.rida.app"}
         userGUID: 5c339935-722b-4986-bdb7-1400a7efa284',
        'Response status: 304
         []
         duration: 0.202',
        '',
        '2021-08-17 14:00:00',
        '2021-08-17 14:00:00',
        '5c339935-722b-4986-bdb7-1400a7efa284'
    ),
    ( -- Logged: updated_at at cursor & id not behind cursor
        3,
        'https://api.rida.app/v1/logDriverPosition',
        '10.41.1.31',
        '{"lat":6.5154854999999996,"long":3.2890172,"heading":90,"user_guid":"5c339935-722b-4986-bdb7-1400a7efa284"}
         method: POST
         Language: en
         headers: {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvYXBpLnJpZGEuYXBwIiwiYXVkIjoiaHR0cHM6XC9cL2FwaS5yaWRhLmFwcCIsImlhdCI6MTYyMjEwOTg5NywibmJmIjoxNjIyMTA5ODk3LCJleHAiOjE2NTM2NDU4OTcsImlkIjo5MTA4MiwiZGV2aWNlX3V1aWQiOiI2ZDA1YWNmYS0zZjU0LTQyMTYtYmY1Ny0zMjJhNTVjMjU5NjEifQ.l7Wr8Ae3AdMXUq-wNG2IrWHsjJprdVZ8TF7Dgy7QP4Y","Accept-Encoding":"gzip","Content-Type":"application\/json","Content-Length":"171","Connection":"close","X-Publisher-Type":"http","Accept-Language":"en","Host":"api.rida.app"}
         userGUID: 5c339935-722b-4986-bdb7-1400a7efa284',
        'Response status: 304
         []
         duration: 0.203',
        '',
        '2021-08-17 14:00:00',
        '2021-08-17 14:00:00',
        '5c339935-722b-4986-bdb7-1400a7efa284'
    ),
    ( -- Logged: updated_at after cursor & id behind cursor
        0,
        'https://api.rida.app/v1/logDriverPosition',
        '10.41.1.31',
        '{"lat":6.5154854999999996,"long":3.2890172,"heading":90,"user_guid":"5c339935-722b-4986-bdb7-1400a7efa284"}
         method: POST
         Language: en
         headers: {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvYXBpLnJpZGEuYXBwIiwiYXVkIjoiaHR0cHM6XC9cL2FwaS5yaWRhLmFwcCIsImlhdCI6MTYyMjEwOTg5NywibmJmIjoxNjIyMTA5ODk3LCJleHAiOjE2NTM2NDU4OTcsImlkIjo5MTA4MiwiZGV2aWNlX3V1aWQiOiI2ZDA1YWNmYS0zZjU0LTQyMTYtYmY1Ny0zMjJhNTVjMjU5NjEifQ.l7Wr8Ae3AdMXUq-wNG2IrWHsjJprdVZ8TF7Dgy7QP4Y","Accept-Encoding":"gzip","Content-Type":"application\/json","Content-Length":"171","Connection":"close","X-Publisher-Type":"http","Accept-Language":"en","Host":"api.rida.app"}
         userGUID: 5c339935-722b-4986-bdb7-1400a7efa284',
        'Response status: 304
         []
         duration: 0.200',
        '',
        '2021-08-17 14:15:00',
        '2021-08-17 14:15:00',
        '5c339935-722b-4986-bdb7-1400a7efa284'
    ),
    ( -- No log: handle in blacklist
        4,
        'http://172.18.0.30/v1/checkStatus',
        '198.18.235.208',
        '[]
         method: GET
         Language: 
         headers: {"Connection":"close","Accept-Encoding":"gzip","User-Agent":"YC-Healthcheck","Host":"172.18.0.30:80","Content-Length":"","Content-Type":""}
         userGUID: ',
        'Response status: 200
         {"status":"OK"}
         duration: 0.204',
        '',
        '2021-08-17 15:00:00',
        '2021-08-17 15:00:00',
        null
    ),
    ( -- Logged: updated_at behind cursor & id behind cursor
        5,
        'https://api.rida.app/v1/getPointInfo',
        '10.41.1.31',
        '{"lat":6.5154854999999996,"long":3.2890172}
         method: POST
         Language: en
         headers: {"Authorization":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvYXBpLnJpZGEuYXBwIiwiYXVkIjoiaHR0cHM6XC9cL2FwaS5yaWRhLmFwcCIsImlhdCI6MTYyMjEwOTg5NywibmJmIjoxNjIyMTA5ODk3LCJleHAiOjE2NTM2NDU4OTcsImlkIjo5MTA4MiwiZGV2aWNlX3V1aWQiOiI2ZDA1YWNmYS0zZjU0LTQyMTYtYmY1Ny0zMjJhNTVjMjU5NjEifQ.l7Wr8Ae3AdMXUq-wNG2IrWHsjJprdVZ8TF7Dgy7QP4Y","Accept-Encoding":"gzip","Content-Type":"application\/json","Content-Length":"171","Connection":"close","X-Publisher-Type":"http","Accept-Language":"en","Host":"api.rida.app"}
         userGUID: 5c339935-722b-4986-bdb7-1400a7efa284',
        'Response status: 200
         {"status":"INVALID_DATA", "errors": {}}
         duration: 0.200',
        '',
        '2021-08-17 15:10:00',
        '2021-08-17 15:10:00',
        '5c339935-722b-4986-bdb7-1400a7efa284'
    );
