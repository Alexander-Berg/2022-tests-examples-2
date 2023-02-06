INSERT INTO depots_wms.depots (source, updated, depot_id, external_id, region_id, timezone, location, phone_number,
                               currency, status, hidden, title, name, price_list_id, root_category_id, assortment_id)
VALUES ('WMS', current_timestamp, 'id-99999901', '99999901', 213, 'Europe/Moscow',
        (37.371618, 55.840757)::depots_wms . depot_location, '', 'RUB', 'active'::depots_wms.depot_status, false,
        '"Партвешок За Полтишок" на Никольской', 'test_lavka_1', '99999901PRLIST', 'root-99999901', '99999901ASTMNT');

INSERT INTO depots_wms.zones(created, updated, depot_id, zone, timetable, zone_id, status, delivery_type)
VALUES (current_timestamp - '1 year'::interval, current_timestamp, 'id-99999901', '{
  "coordinates": [
    [[[
         37.04315185546875,
         55.33851784425634
       ],
       [
         37.97149658203125,
         55.33851784425634
       ],
       [
         37.97149658203125,
         55.77966236981707
       ],
       [
         37.04315185546875,
         55.77966236981707
       ],
       [
         37.04315185546875,
         55.33851784425634
       ]]]
  ],
  "type": "MultiPolygon"
}'::JSONB, ARRAY[('everyday'::depots_wms.day_type,
                  ('00:00', '24:00')::depots_wms . opened_timerange)]::depots_wms.timetable_item[],
        '455157df10b0cb4bbc07e1b958b4a1', 'active', 'foot');
