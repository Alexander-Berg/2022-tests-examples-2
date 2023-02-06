UPDATE multioffer.multioffers SET wave = 2, status = 'in_progress'::multioffer.multioffer_status WHERE id = 'ecc6dc92-6d56-48a3-884d-f31390cd9a3c';

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('ecc6dc92-6d56-48a3-884d-f31390cd9a3c', 'declined'::multioffer.offer_status, 'a3608f8f7ee84e0b9c21862beef7e48d', 'fc7d65d48edd40f9be1ced0f08c98dcd', 2, 'alias_id3', '{}', FALSE);

INSERT INTO multioffer.multioffer_drivers (multioffer_id, offer_status, park_id, driver_profile_id, score, alias_id, candidate_json, answer)
    VALUES ('ecc6dc92-6d56-48a3-884d-f31390cd9a3c', 'sent'::multioffer.offer_status, 'a3608f8f7ee84e0b9c21862beef7e48d', '47ee2a629f624e6fa07ebd0e159da258', 3, 'alias_id4', '{}', NULL);
