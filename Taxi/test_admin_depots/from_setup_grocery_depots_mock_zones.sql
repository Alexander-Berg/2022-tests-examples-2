INSERT INTO depots_wms.zones(created, updated, zone_id, depot_id, delivery_type, status, timetable, zone)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, '000000010000a001', 'id-99999901', 'foot', 'active',
        ARRAY [('everyday'::depots_wms.day_type,
                ('00:00', '24:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[], '{
    "type": "MultiPolygon",
    "coordinates": [
      [
        [
          [
            1,
            2
          ],
          [
            5,
            6
          ],
          [
            3,
            4
          ]
        ]
      ]
    ]
  }'::JSONB);
