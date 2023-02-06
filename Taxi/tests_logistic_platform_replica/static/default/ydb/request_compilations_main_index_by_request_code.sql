--!syntax_v1

UPSERT INTO `main/request_compilations/index_by_request_code` (
    request_code,
    employer_code,
    request_id,
    created_at
) VALUES
('request_code1', 'first_employer', '13aad1ae-c205-42e8-94e1-e7c96728d738', CAST(1643399569000000 AS Timestamp)),
('request_code2', 'second_employer', '07243441-785b-4a70-a2c2-bf48348f4225', CAST(1641694841000000 AS Timestamp)),
('request_code3', 'third_employer', '2d6fb2df-15b9-4855-9cc1-e51f5f1bc674', CAST(1641490467000000 AS Timestamp)),
('request_code1', 'third_employer', '3121c950-1024-4be1-9ba5-33e6dae2da4a', CAST(1641966527000000 AS Timestamp)),
('request_code4', 'fourth_employer', 'aadc50f7-5654-4f38-a669-de2aee65aeac', CAST(1642738350000000 AS Timestamp)),
('request_code5', 'first_employer', '09c7720b-8e6c-4d30-bd73-5d52916be754', CAST(1671161946000000 AS Timestamp)),
('request_code6', 'first_employer', '288affa0-50e8-458e-8ab7-5bdb8938de7a', CAST(1670766632000000 AS Timestamp)),
('request_code7', 'second_employer', '5d04acd2-aee3-4058-a194-57b6ddc635f5', CAST(1672017115000000 AS Timestamp)),
('request_code8', 'first_employer', 'd81dec52-83e9-4175-93bb-0e913d6afbb9', CAST(1670018124000000 AS Timestamp)),
('request_code9', 'second_employer', '1717dcb9-3767-4232-ac04-43b832006edd', CAST(1670765326000000 AS Timestamp)),
('request_code10', 'fourth_employer', 'b90b5b11-2b83-40fc-9920-957f43e602b6', CAST(1670148072000000 AS Timestamp)),
('request_code11', 'third_employer', '6d2b13a2-f55b-4063-a269-d91d545508ae', CAST(1670090329000000 AS Timestamp));
