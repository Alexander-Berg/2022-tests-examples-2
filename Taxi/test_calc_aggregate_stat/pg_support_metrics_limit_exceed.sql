DO
$do$
    BEGIN
        FOR i IN 1..50000 LOOP
            INSERT INTO events.chatterbox_events
                (id, type, created_ts, login, action_type, in_addition, line, new_line, start_timestamp)
            VALUES
              (
                i, 'chatterbox_action', '2019-07-02 12:00:01.000000+00',
                'superuser', 'forward', FALSE, 'first', i, null
              );
        END LOOP;
    END
$do$;
