INSERT INTO hiring_candidates.candidates(
    id,
    personal_phone_id
) VALUES (
    '0000',
    'ce4db5ccb4bcaf8f7cfb9d752172a1c5'
),
(
    '0001',
    'ae65aa5bd9a4d47ce21169b9dbaac896'
),
(
    '0002',
    '5e88de1a146747723b28a7d13d8f8ddf'
);

INSERT INTO hiring_candidates.leads(
    lead_id,
    created_ts,
    candidate_id,
    extra
) VALUES (
    'lead_0000_0',
    '2022-06-27T13:00:00'::TIMESTAMP,
    '0000',
    '{"main_lead": "false"}'
),
(
    'lead_0000_1',
    '2022-06-25T13:00:00'::TIMESTAMP,
    '0001',
    null
),
(
    'lead_0000_2',
    '2022-06-28T09:00:00'::TIMESTAMP,
    '0000',
    '{"main_lead": "true"}'
),
(
    'lead_0000_3',
    '2022-06-28T13:00:00'::TIMESTAMP,
    '0000',
    '{"main_lead": "false"}'
),
(
    'lead_0000_4',
    '2022-06-26T18:00:00'::TIMESTAMP,
    '0000',
    '{"main_lead": "true"}'
),
(
    'lead_0001_0',
    '2022-06-26T09:00:00'::TIMESTAMP,
    '0001',
    '{"main_lead": "false"}'
),
(
    'lead_0001_1',
    '2022-06-28T09:00:00'::TIMESTAMP,
    '0001',
    '{"main_lead": "false"}'
),
(
    'lead_0001_2',
    '2022-06-25T09:00:00'::TIMESTAMP,
    '0001',
    '{"main_lead": "false"}'
);
