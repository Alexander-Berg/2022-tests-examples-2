SET SEARCH_PATH TO fleet_signatures_storage;

INSERT INTO fleet_signatures_storage.documents (id,
                                                body,
                                                created_at,
                                                updated_at)
VALUES ('00000001-f462-48af-bb10-66b0e9942bd8',
        'test_document_2',
        '2020-04-10T08:25:18+00:00',
        '2020-04-10T08:25:18+00:00');

INSERT
INTO signatures (id,
                 document_id,
                 signer_identity,
                 signer_park_id,
                 signer_id,
                 signature_type,
                 signature_data,
                 signed_at,
                 updated_at)
VALUES ('00000002-4878-49b7-b203-62135cb951df',
        '00000001-f462-48af-bb10-66b0e9942bd8',
        'dispatcher',
        'park_1',
        'dispatcher_1',
        'simple',
        NULL,
        '2020-04-10T08:25:18+00:00',
        '2020-04-10T08:25:18+00:00'),
       ('00000002-80b0-41cf-8eaf-52ed0a54e88c',
        '00000001-f462-48af-bb10-66b0e9942bd8',
        'unknown',
        NULL,
        NULL,
        'qualified',
        'test_signature',
        '2020-04-10T08:25:18+00:00',
        '2020-04-10T08:25:18+00:00');
