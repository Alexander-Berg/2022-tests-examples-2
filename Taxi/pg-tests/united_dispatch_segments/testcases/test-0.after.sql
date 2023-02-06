-- 1 record:
--   1 - fresh (skipped)
INSERT INTO
    united_dispatch.segments (
        id,
        waybill_building_version,
        is_waybill_send,
        dispatch_revision,
        taxi_classes,
        taxi_requirements,
        special_requirements,
        points,
        crutches,
        status,
        created_ts,
        updated_ts
    )
VALUES
     (
        'a861ab4d799b48e79f36c335acc3b289',
        1,
        true,
        2,
        '{courier,eda,express}',
        '{"door_to_door": true}',
        '{}',
        '{}',
        NULL,
        'executing',
        '2022-04-01T12:00:00.0000+03:00',
        '2022-04-14T11:59:59.0000+03:00'
    ),
    (
        'f51b9e9e57224a6093f17b8e6a3cefce',
        1,
        true,
        2,
        '{courier,eda,express}',
        '{"door_to_door": true}',
        '{}',
        '{}',
        NULL,
        'resolved',
        '2022-04-01T12:00:00.0000+03:00',
        '2022-04-14T12:00:01.0000+03:00'
    );

INSERT INTO
    united_dispatch.segment_executors (
        planner_type,
        segment_id,
        execution_order,
        planner_shard,
        status,
        created_ts,
        updated_ts
    )
VALUES
    (
        'eats',
        'a861ab4d799b48e79f36c335acc3b289',
        0,
        'moscow',
        'active',
        '2022-04-01T12:00:00.0000+03:00',
        '2022-05-14T11:59:59.0000+03:00'
    ),
    (
        'delivery',
        'a861ab4d799b48e79f36c335acc3b289',
        1,
        'moscow',
        'idle',
        '2022-04-01T12:00:00.0000+03:00',
        '2022-05-14T11:59:59.0000+03:00'
    ),
    (
        'grocery',
        'f51b9e9e57224a6093f17b8e6a3cefce',
        0,
        'moscow',
        'finished',
        '2022-04-01T12:00:00.0000+03:00',
        '2022-04-14T12:00:01.0000+03:00'
    );
