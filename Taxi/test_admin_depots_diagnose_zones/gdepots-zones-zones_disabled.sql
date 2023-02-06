INSERT INTO depots_wms.zones(created, updated, depot_id, zone, timetable, zone_id, status, delivery_type)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, 'all-zones-disabled-depot', '{
  "coordinates": [
    [
      [
        [
          2,
          2
        ],
        [
          20,
          30
        ],
        [
          30,
          20
        ],
        [
          2,
          2
        ]
      ]
    ]
  ],
  "type": "MultiPolygon"
}'::JSONB, ARRAY [('everyday'::depots_wms.day_type,
                   ('07:00', '00:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        'e0424de2f00412b5267847f3a1e792', 'disabled', 'yandex-taxi');
INSERT INTO depots_wms.zones(created, updated, depot_id, zone, timetable, zone_id, status, delivery_type)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, 'all-zones-disabled-depot', '{
  "coordinates": [
    [
      [
        [
          2,
          2
        ],
        [
          20,
          30
        ],
        [
          30,
          20
        ],
        [
          2,
          2
        ]
      ]
    ]
  ],
  "type": "MultiPolygon"
}'::JSONB, ARRAY [('everyday'::depots_wms.day_type,
                   ('07:00', '00:00')::depots_wms.opened_timerange)]::depots_wms.timetable_item[],
        '0da1368c00a677410840cce1e6a82b', 'disabled', 'yandex-taxi-remote');
