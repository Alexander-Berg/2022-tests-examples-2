INSERT INTO depots_wms.zones
(zone_id, depot_id, status, created, updated, delivery_type, timetable, zone, effective_from, effective_till)
VALUES
    (
        'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000_foot_without_timetable',
        'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        'active',
        current_timestamp - '1 year'::interval,
        current_timestamp,
        'foot',
        ARRAY[]::depots_wms.timetable_item[],
        '{"type": "MultiPolygon", "coordinates": [[[[37.64216423034668,55.73386421559154],[37.64572620391845,55.73615962895247],[37.64167070388794,55.743153766729286],[37.63817310333252,55.74206667732932],[37.640061378479004,55.73699319302477],[37.64216423034668,55.73386421559154]]]]}'::JSONB,
        current_timestamp + '1 day'::interval,
        NULL
    );
