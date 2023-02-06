UPDATE multioffer.multioffer_drivers
    SET offer_status = 'accepted'::multioffer.offer_status, answer = TRUE
    WHERE offer_status = 'sent'::multioffer.offer_status AND multioffer_id = 'ecc6dc92-6d56-48a3-884d-f31390cd9a3c';
