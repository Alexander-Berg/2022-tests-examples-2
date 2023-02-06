--!syntax_v1

UPSERT INTO `main/request_compilations/index_by_request_id` (
    request_id,
    created_at
) VALUES
('5d04acd2-aee3-4058-a194-57b6ddc635f5', CAST(1772017115000000 AS Timestamp)),
('b90b5b11-2b83-40fc-9920-957f43e602b6', CAST(1770148072000000 AS Timestamp));
