INSERT INTO bank_applications.applications (application_id,
                                            user_id_type,
                                            user_id,
                                            type,
                                            status,
                                            reason,
                                            multiple_success_status_allowed,
                                            initiator)
VALUES ('7948e3a9-623c-4524-a390-9e4264d27a05',
        'BUID',
        '67754336-d4d1-43c1-aadb-cabd06674ea6',
        'DIGITAL_CARD_ISSUE',
        'FAILED',
        'error',
        TRUE,
        '{}'::jsonb);