INSERT INTO catalog_wms.depots
(depot_id, external_id, name, updated, location, extended_zones, timezone, region_id, currency, status, source)
VALUES
('id-4', '4', 'lavka_foot_24h', CURRENT_TIMESTAMP, (1, 2)::catalog_wms.depot_location,
 ARRAY[
       (
           'foot',
           '{"type": "MultiPolygon", "coordinates": [[[[1.0, 1.0], [4.0, 1.0], [4.0, 4.0], [1.0, 4.0]]]]}'::JSONB,
           ARRAY[('everyday', ('00:00','24:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
           'active'
       )
      ]::catalog_wms.extended_zone_v1[],
      'Europe/Moscow', 213, 'RUB', 'active', '1C'
),
('id-5', '5', 'lavka_taxi_monday_10_12', CURRENT_TIMESTAMP, (1, 2)::catalog_wms.depot_location,
 ARRAY[
       (
           'yandex-taxi',
           '{"type": "MultiPolygon", "coordinates": [[[[7.0, 1.0], [10.0, 1.0], [10.0, 4.0], [7.0, 4.0]]]]}'::JSONB,
           ARRAY[('monday', ('10:00','12:00')::catalog_wms.timerange_v1)]::catalog_wms.timetable_item_v2[],
           'active'
       )
      ]::catalog_wms.extended_zone_v1[],
      'Europe/Moscow', 213, 'RUB', 'active', '1C'
);
