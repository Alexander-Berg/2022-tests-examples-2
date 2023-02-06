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
