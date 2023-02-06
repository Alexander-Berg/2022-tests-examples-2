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
    next_dispatch_run,
    draw_cnt,
    draw_cnt_no_candidates
    )
VALUES
    (
        1,
        'user_id_1',
        'offer_id_1',
        'order_id_1',
        '2020-03-16T17:10:26+0300',
        'example',
        'example_agglomeration',
        '{"econom"}',
        'taxi',
        'idle',
        '2020-03-16T17:10:31+0300',
        '2020-03-16T17:10:35+0300',
        '2020-03-16T17:10:40+0300',
        0,
        0
    ),
    (
        2,
        'user_id_1',
        'offer_id_2',
        'order_id_2',
        '2020-03-16T17:10:23+0300',
        'example',
        'example_agglomeration',
        '{"econom"}',
        'taxi',
        'idle',
        '2020-03-16T17:10:31+0300',
        '2020-03-16T17:10:34+0300',
        null,
        2,
        7
    ),
    (
        3,
        'user_id_1',
        'offer_id_3',
        'order_id_3',
        '2020-03-16T17:10:23+0300',
        'example',
        'example_agglomeration',
        '{"econom"}',
        'taxi',
        'idle',
        '2020-03-16T17:10:31+0300',
        '2020-03-16T17:10:34+0300',
        null,
        2,
        12
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
              ::jsonb),
         (
          3,
          '{"allowed_classes": ["econom"], "point": [37.622648, 55.756032], "order"
          :{"created": 1584378627.69, "nearest_zone": "example", "request": {
	          "offer": "offer_id_3",
	          "source": {"geopoint": [37.622648, 55.756032]},
	          "due": 1584378637.69}}}'
              ::jsonb
         );
