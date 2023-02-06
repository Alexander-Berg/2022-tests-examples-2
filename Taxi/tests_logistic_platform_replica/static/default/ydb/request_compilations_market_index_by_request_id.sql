--!syntax_v1

UPSERT INTO `market/request_compilations/index_by_request_id` (
    request_id,
    created_at
) VALUES
('23aad1ae-c205-42e8-94e1-e7c96728d738', CAST(1643399569000000 AS Timestamp)),
('37243441-785b-4a70-a2c2-bf48348f4225', CAST(1641694841000000 AS Timestamp)),
('4d6fb2df-15b9-4855-9cc1-e51f5f1bc674', CAST(1641490467000000 AS Timestamp)),
('5121c950-1024-4be1-9ba5-33e6dae2da4a', CAST(1641966527000000 AS Timestamp)),
('6adc50f7-5654-4f38-a669-de2aee65aeac', CAST(1642738350000000 AS Timestamp));
