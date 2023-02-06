INSERT INTO dispatch_buffer.dispatch_meta (
    id,
    user_id,
    offer_id,
    order_id,
    created,
    updated,
    due,
    zone_id,
    service,
    dispatch_status,
    order_lookup,
    first_dispatch_run,
    last_dispatch_run,
    callback,
    classes
)
VALUES (
     1,
    'user_id_1',
    'offer_id_1',
    'order_id_1',
    NOW(),
    NOW(),
    NULL,
    'zone',
    'taxi',
    'dispatched',
    ROW(0,1,3),
    NULL,
    NULL,
    ROW ('callback_text', '300 milliseconds'::interval, 2),
    '{"econom"}'
), (
    2,
    'user_id_1',
    'offer_id_2',
    'order_id_2',
    NOW(),
    NOW(),
    NOW(),
    'zone',
    'taxi',
    'dispatched',
    ROW(0,2,3),
    NULL,
    NULL,
    ROW ('callback_text', '300 milliseconds'::interval, 2),
    '{"econom"}'
), (
    3,
    'user_id_1',
    'offer_id_3',
    'order_id_3',
    NOW(),
    NOW(),
    NOW(),
    'zone',
    'taxi',
    'idle',
    ROW(0,3,4),
    NULL,
    NULL,
    ROW ('callback_text', '300 milliseconds'::interval, 2),
    '{"econom"}'
),(
    4,
    'user_id_1',
    'offer_id_4',
    'order_id_4',
    NOW(),
    (NOW() + interval '30 minute'),
    (NOW() + interval '30 minute'),
    'zone',
    'taxi',
    'on_draw',
    ROW(0,3,4),
    NULL,
    NULL,
    ROW ('callback_text', '300 milliseconds'::interval, 2),
    '{"econom"}'
);

INSERT INTO dispatch_buffer.order_meta(
    id, order_meta
) VALUES (1,
          '{"allowed_classes": ["econom"], "point": [37.622648, 55.756032], "order"
          :{"created": 1584378627.69, "nearest_zone": "example", "request": {
	          "offer": "offer_id_1",
	          "source": {"geopoint": [37.622648, 55.756032]},
	          "due": 1584378637.69}}}'
              ::jsonb),
         (
             2,
             '{"allowed_classes": ["econom"], "point": [37.622648, 55.756032], "order"
		         :{"created": 1584378627.69, "nearest_zone": "example", "request": {
			         "offer": "offer_id_2",
			         "source": {"geopoint": [37.622648, 55.756032]},
			         "due": 1584378637.69}}}'
                 ::jsonb
         ),
         (
             3,
             '{"allowed_classes": ["econom"], "point": [37.622648, 55.756032], "order"
		         :{"created": 1584378627.69, "nearest_zone": "example", "request": {
			         "offer": "offer_id_3",
			         "source": {"geopoint": [37.622648, 55.756032]},
			         "due": 1584378637.69}}}'
                 ::jsonb
         ),
         (
             4,
             '{"allowed_classes": ["econom"], "point": [37.622648, 55.756032], "order"
		         :{"created": 1584378627.69, "nearest_zone": "example", "request": {
			         "offer": "order_id_4",
			         "source": {"geopoint": [37.622648, 55.756032]},
			         "due": 1584378637.69}}}'
                 ::jsonb
         );

INSERT INTO dispatch_buffer.dispatched_performer(
    id, dispatched_performer
) VALUES
          (1,
           '{}'::jsonb
              ),
         (
             2,
             '{}'::jsonb
         ),
         (
             3,
             '{}'::jsonb
         ),
         (
             4,
             '{}'::jsonb
         );
