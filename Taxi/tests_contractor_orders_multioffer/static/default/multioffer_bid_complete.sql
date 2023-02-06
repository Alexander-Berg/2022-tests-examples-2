UPDATE multioffer.multioffers
SET status = 'completed'
WHERE id = '72bcbde8-eaed-460f-8f88-eeb4e056c317';

UPDATE multioffer.multioffer_bids
SET status = 'won'
WHERE multioffer_id = '72bcbde8-eaed-460f-8f88-eeb4e056c317'
  AND id = '0be9a612-83f8-4f52-b585-16085c20299d';

UPDATE multioffer.multioffer_drivers
SET offer_status = 'win', answer = TRUE
WHERE multioffer_id = '72bcbde8-eaed-460f-8f88-eeb4e056c317'
  AND driver_profile_id = 'driver_profile_id_1';
