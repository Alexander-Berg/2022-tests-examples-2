-- 2 records: 
--   1 - old (remove)
--   2 - fresh (skip)

INSERT INTO united_dispatch.waybills (
        id, proposition_status, waybill, candidate, created_ts, 
        updated_ts, external_resolution, revision, lookup, 
        proposition_builder_shard, lookup_flow, previous_id, 
        update_proposition_id) 
VALUES (
        '6bdb8185-eb4e-48a7-8ac4-de203d116bed', 'new', '{}', NULL,
        '2021-10-17 17:52:01.955825+03', '2021-10-17 17:52:02.424329+03',
        'proposition_failed', 1, row(1, 1, 1)::united_dispatch.lookup_v1,
        'default', 'taxi-dispatch'::united_dispatch.lookup_flow, NULL, NULL
        ),
        (
        '40f0fec3-886c-41d1-878c-b014f6947f4f', 'new', '{}', NULL,
        '2021-11-17 17:52:01.955825+03', '2021-11-17 17:52:02.424329+03',
        'proposition_failed', 1, row(1, 1, 1)::united_dispatch.lookup_v1,
        'default', 'taxi-dispatch'::united_dispatch.lookup_flow, NULL, NULL
        );
