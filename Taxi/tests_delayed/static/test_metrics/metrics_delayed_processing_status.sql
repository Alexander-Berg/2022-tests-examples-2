/* V1 */

DO
    $fill_db$ DECLARE
        ARRIVE_TIME TIMESTAMP = TIMESTAMP '2019-02-03T04:00:00';
        NOW_MOCK TIMESTAMP = TIMESTAMP '2019-02-03T03:40:00';
    BEGIN
        INSERT INTO orders.orders
            (order_id,
             arrive_time,
             link_id,
             last_proceed_time,
             is_processing_change_time,
             is_processing)
        VALUES ('dispatched_delayed_order_id_1',
                ARRIVE_TIME,
                'link_1',
                TIMESTAMP '2019-02-03T00:00:00',
                TIMESTAMP '2019-02-03T00:00:00', FALSE), /* 1. Dispatched (not enough cars) */
               ('dispatched_delayed_order_id_2',
                NOW_MOCK - INTERVAL '5 minutes',
                'link_2',
                TIMESTAMP '2019-02-03T00:00:00',
                TIMESTAMP '2019-02-03T00:00:00', FALSE), /* 2. Dispatched (due < now) */
               ('success_delayed_order_id_1',
                ARRIVE_TIME,
                'link_2',
                TIMESTAMP '2019-02-03T00:00:00',
                TIMESTAMP '2019-02-03T00:00:00', FALSE), /* 3. Success */
               ('failed_delayed_order_id_1',
                ARRIVE_TIME,
                'link_2',
                TIMESTAMP '2019-02-03T00:00:00',
                TIMESTAMP '2019-02-03T00:00:00', FALSE), /* 4. Failed (archive does not contains it) */
               ('removed_delayed_order_id_1',
                ARRIVE_TIME,
                'link_2',
                TIMESTAMP '2019-02-03T00:00:00',
                TIMESTAMP '2019-02-03T00:00:00', FALSE); /* 5. Removed (cancelled) */

    END;
    $fill_db$;
