INSERT INTO depots_wms.zones(created, updated, depot_id, zone, timetable, zone_id, status, delivery_type)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, 'id-99999901', '{
  "coordinates": [
    [
      [
        [
          1,
          2
        ],
        [
          3,
          4
        ],
        [
          5,
          6
        ]
      ]
    ]
  ],
  "type": "MultiPolygon"
}'::JSONB, ARRAY [('everyday'::depots_wms.day_type,
                   ('00:00', '24:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '455157df10b0cb4bbc07e1b958b4a1', 'active', 'foot');
INSERT INTO depots_wms.zones(created, updated, depot_id, zone, timetable, zone_id, status, delivery_type)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, 'id-99999902', '{
  "coordinates": [
    [
      [
        [
          1,
          2
        ],
        [
          3,
          4
        ],
        [
          5,
          6
        ]
      ]
    ]
  ],
  "type": "MultiPolygon"
}'::JSONB, ARRAY [('everyday'::depots_wms.day_type,
                   ('00:00', '24:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        'e157b937ab61b9e365f686347fbcb7', 'active', 'foot');
INSERT INTO depots_wms.zones(created, updated, depot_id, zone, timetable, zone_id, status, delivery_type)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, 'id-99999903', '{
  "coordinates": [
    [
      [
        [
          1,
          2
        ],
        [
          3,
          4
        ],
        [
          5,
          6
        ]
      ]
    ]
  ],
  "type": "MultiPolygon"
}'::JSONB, ARRAY [('everyday'::depots_wms.day_type,
                   ('00:00', '24:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '9daa2c420b0473d468315b63b0fb16', 'active', 'foot');
INSERT INTO depots_wms.zones(created, updated, depot_id, zone, timetable, zone_id, status, delivery_type)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, 'id-99999904', '{
  "coordinates": [
    [
      [
        [
          1,
          2
        ],
        [
          3,
          4
        ],
        [
          5,
          6
        ]
      ]
    ]
  ],
  "type": "MultiPolygon"
}'::JSONB, ARRAY [('everyday'::depots_wms.day_type,
                   ('00:00', '24:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '1bba5b1029283d4f6cc86350fc8dd1', 'active', 'foot');
INSERT INTO depots_wms.zones(created, updated, depot_id, zone, timetable, zone_id, status, delivery_type)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, 'id-5', '{
  "coordinates": [
    [
      [
        [
          1,
          2
        ],
        [
          3,
          4
        ],
        [
          5,
          6
        ]
      ]
    ]
  ],
  "type": "MultiPolygon"
}'::JSONB, ARRAY [('everyday'::depots_wms.day_type,
                   ('00:00', '24:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '8541c563467e90f107a4d71188d12b', 'active', 'foot');
INSERT INTO depots_wms.zones(created, updated, depot_id, zone, timetable, zone_id, status, delivery_type)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, 'id-6', '{
  "coordinates": [
    [
      [
        [
          1,
          2
        ],
        [
          3,
          4
        ],
        [
          5,
          6
        ]
      ]
    ]
  ],
  "type": "MultiPolygon"
}'::JSONB, ARRAY [('everyday'::depots_wms.day_type,
                   ('00:00', '24:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '11985b9832c0a656910136f51aeb98', 'active', 'foot');
INSERT INTO depots_wms.zones(created, updated, depot_id, zone, timetable, zone_id, status, delivery_type)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, 'id-666666', '{
  "coordinates": [
    [
      [
        [
          1,
          2
        ],
        [
          3,
          4
        ],
        [
          5,
          6
        ]
      ]
    ]
  ],
  "type": "MultiPolygon"
}'::JSONB, ARRAY [('everyday'::depots_wms.day_type,
                   ('00:00', '24:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        'cc96c37c1fb257c0c0987de9a4355e', 'active', 'foot');
INSERT INTO depots_wms.zones(created, updated, depot_id, zone, timetable, zone_id, status, delivery_type)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, 'id-777777', '{
  "coordinates": [
    [
      [
        [
          11.1,
          11.2
        ],
        [
          11.3,
          11.4
        ],
        [
          11.5,
          11.6
        ]
      ]
    ]
  ],
  "type": "MultiPolygon"
}'::JSONB, ARRAY [('everyday'::depots_wms.day_type,
                   ('00:00', '24:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '333f0ed817e237583242875cb86ca7', 'active', 'foot');
