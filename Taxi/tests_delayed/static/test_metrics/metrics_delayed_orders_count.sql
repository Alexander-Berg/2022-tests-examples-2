/* V1 */

DO
    $fill_db$ DECLARE
        ARRIVE_TIME  TIMESTAMP = TIMESTAMP '2019-02-03T04:00:00';
        LAST_PROCEED TIMESTAMP = TIMESTAMP '2019-02-03T00:00:00';
    BEGIN
        INSERT INTO orders.orders
            (order_id,
             ARRIVE_TIME,
             zone,
             tariff,
             link_id,
             last_proceed_time,
             is_processing_change_time,
             is_processing)
        VALUES ('delayed_order_id_1',
                ARRIVE_TIME + INTERVAL '1' MINUTE,
                'moscow',
                'econom',
                'link_1',
                LAST_PROCEED,
                TIMESTAMP '2019-02-03T00:00:00',
                FALSE), /* 1 */
               ('delayed_order_id_2',
                ARRIVE_TIME + INTERVAL '1' MINUTE,
                'moscow',
                'econom',
                'link_2',
                LAST_PROCEED,
                TIMESTAMP '2019-02-03T03:45:00',
                TRUE), /* 2 */
               ('delayed_order_id_3',
                ARRIVE_TIME + INTERVAL '1' MINUTE,
                'moscow',
                'econom',
                'link_2',
                LAST_PROCEED,
                TIMESTAMP '2019-02-03T03:45:00',
                TRUE), /* 3 */
               ('delayed_order_id_4',
                ARRIVE_TIME + INTERVAL '1' MINUTE,
                'moscow',
                'econom',
                'link_2',
                LAST_PROCEED,
                TIMESTAMP '2019-02-03T03:45:00',
                TRUE), /* 4 */
               ('delayed_order_id_5',
                ARRIVE_TIME,
                'moscow',
                'econom',
                'link_2',
                LAST_PROCEED,
                TIMESTAMP '2019-02-03T03:45:00',
                TRUE), /* 5 */
               ('delayed_order_id_6',
                ARRIVE_TIME,
                'moscow',
                'econom',
                'link_2',
                LAST_PROCEED,
                TIMESTAMP '2019-02-03T03:45:00',
                TRUE), /* 6 */
               ('delayed_order_id_7',
                ARRIVE_TIME,
                'moscow',
                'econom',
                'link_2',
                LAST_PROCEED,
                TIMESTAMP '2019-02-03T03:45:00',
                FALSE); /* 7 */


    END;
        $fill_db$;
