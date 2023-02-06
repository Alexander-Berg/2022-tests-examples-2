--!syntax_v1

UPSERT INTO `market/request_compilations/struct/2022-01` (
    request_id,
    data,
    created_at
) VALUES
('23aad1ae-c205-42e8-94e1-e7c96728d738', 'STRING_VALUE_C1', CAST(1643399569000000 AS Timestamp)),
('37243441-785b-4a70-a2c2-bf48348f4225', 'STRING_VALUE_C2', CAST(1641694841000000 AS Timestamp)),
('4d6fb2df-15b9-4855-9cc1-e51f5f1bc674', 'STRING_VALUE_C3', CAST(1641490467000000 AS Timestamp)),
('5121c950-1024-4be1-9ba5-33e6dae2da4a', 'STRING_VALUE_C4', CAST(1641966527000000 AS Timestamp)),
('6adc50f7-5654-4f38-a669-de2aee65aeac', 'STRING_VALUE_C5', CAST(1642738350000000 AS Timestamp));
