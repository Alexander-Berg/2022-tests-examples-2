--!syntax_v1

UPSERT INTO `main/request_compilations/index_by_request_code` (
    request_code,
    employer_code,
    request_id,
    created_at
) VALUES
('request_code1', 'first_employer', '13aad1ae-c205-42e8-94e1-e7c96728d738', CAST(1743399569000000 AS Timestamp)),
('request_code2', 'second_employer', '07243441-785b-4a70-a2c2-bf48348f4225', CAST(1741694841000000 AS Timestamp)),
('request_code1', 'third_employer', '3121c950-1024-4be1-9ba5-33e6dae2da4a', CAST(1741966527000000 AS Timestamp)),
('request_code5', 'first_employer', '09c7720b-8e6c-4d30-bd73-5d52916be754', CAST(1771161946000000 AS Timestamp)),
('request_code8', 'first_employer', 'd81dec52-83e9-4175-93bb-0e913d6afbb9', CAST(1770018124000000 AS Timestamp)),
('request_code9', 'second_employer', '1717dcb9-3767-4232-ac04-43b832006edd', CAST(1770765326000000 AS Timestamp));
