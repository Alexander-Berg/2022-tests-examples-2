INSERT INTO dispatch_buffer.dispatch_meta
    (
    id,
    user_id,
    offer_id,
    order_id,
    created,
    zone_id,
    agglomeration,
    classes,
    service,
    dispatch_status,
    first_dispatch_run,
    last_dispatch_run,
    draw_cnt
    )
VALUES
    (
        1,
        'user_id_1',
        'offer_id_1',
        'order_id_1',
        '2020-03-16T17:10:26+0000',
        'example',
        'example_agglomeration',
        '{"econom"}',
        'taxi',
        'idle',
        '2020-03-16T17:10:31+0000',
        '2020-03-16T17:10:35+0000',
        1
    ),
(
        2,
        'user_id_1',
        'offer_id_2',
        'order_id_2',
        '2020-03-16T17:10:23+0000',
        'example',
        'example_agglomeration',
        '{"econom"}',
        'taxi',
        'idle',
        '2020-03-16T17:10:31+0000',
        '2020-03-16T17:10:34+0000',
        2
    ),
(
        3,
        'user_id_1',
        'offer_id_3',
        'order_id_3',
        '2020-03-16T17:10:24+0000',
        'example',
        'example_agglomeration',
        '{"econom"}',
        'taxi',
        'idle',
        '2020-03-16T17:10:31+0000',
        '2020-03-16T17:10:32+0000',
        3
),
(
        4,
        'user_id_1',
        'offer_id_4',
        'order_id_4',
        '2020-03-16T17:10:25+0000',
        'example',
        'example_agglomeration',
        '{"econom"}',
        'taxi',
        'idle',
        '2020-03-16T17:10:31+0000',
        NULL,
        0
);

INSERT INTO dispatch_buffer.order_meta (
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
