INSERT INTO cargo_pricing.shared_calcs_parts (id, hash, updated_ts)
VALUES 
(
    '11111111-1111-1111-1111-111111111113'::UUID,
    'HASH1'::TEXT,
    '2020-10-10T10:00:01+03:00'::TIMESTAMPTZ
),
(
    '11111111-1111-1111-1111-111111111114'::UUID,
    'HASH2'::TEXT,
    '2019-03-09T09:59:59+03:00'::TIMESTAMPTZ
),
(
    '11111111-1111-1111-1111-111111111116'::UUID,
    'HASH4'::TEXT,
    '2020-10-10T09:10:00+03:00'::TIMESTAMPTZ    
);
